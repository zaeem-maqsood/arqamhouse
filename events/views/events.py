from .base import *




class EventSendToSubscribersView(HouseAccountMixin, RedirectView):

    permanent = False
    query_string = True
    pattern_name = 'events:dashboard'

    def get_redirect_url(self, *args, **kwargs):
        print("It came here")
        event = get_object_or_404(Event, slug=kwargs['slug'])
        if event.active:
            print(event)
            event.send_to_subscribers = True
            event.save()
            # Update all of the subscribers scores -----------------------
            subscribers = Subscriber.objects.filter(house=event.house)
            print(subscribers)
            for subscriber in subscribers:
                subscriber.events_total += 1
                subscriber.save()

            if event.image: 
                content = CONTENT
                content = content.replace("[event_image]", event.image.url)
            else:
                content = NO_IMAGE_CONTENT
                
            content = content.replace("[house_name]", event.house.name)
            content = content.replace("[event_name]", event.title)
            content = content.replace("[event_url]", f"https://www.arqamhouse.com{event.get_landing_view()}")
            print(content)

            campaign = Campaign.objects.create(name=f"{event.title} Initial Campaign", house=event.house, total=subscribers.count(), subject=f"New Event By {event.house.name}",
                                               draft=False, content=content)
            campaign.subscribers_sent_to.add(*subscribers)

            task = send_campaign_emails.delay(campaign.id)

            # Update all of the subscribers scores -----------------------
            messages.success(self.request, 'Subscribers have been notified!') 
        else:
            messages.warning(self.request, 'You cannot send out campaigns for inactive events')
        return super().get_redirect_url(*args, **kwargs)


class EventTrafficView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, View):

    template_name = "events/traffic.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
        except Exception as e:
            print(e)
            raise Http404
        return event

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = self.get_event(self.kwargs['slug'])

        event_referer_domains = EventRefererDomain.objects.filter(event=event)

        context["event_referer_domains"] = event_referer_domains
        context["event"] = event
        context["house"] = house
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context



class EventDashboardView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, DetailView):
    model = Event
    template_name = "events/event_dashboard.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_tickets(self, event):
        tickets = Ticket.objects.filter(event=event, deleted=False)
        return tickets

    def get_total_sales(self, event):
        orders = EventOrder.objects.filter(event=event, refunded=False, failed=False).select_related("transaction")
        total_sales = decimal.Decimal(0.00)
        for order in orders:
            if order.transaction.house_amount:
                total_sales += order.transaction.house_amount
        return total_sales


    def graph_data(self, event):
        
        today = timezone.now()
        days_earlier = today - timedelta(days=10)
        attendees = Attendee.objects.filter(order__event=event, order__created_at__range=(days_earlier, today), active=True)

        day_label = []
        tickets_label = []

        for x in range(10):
            one_day_earlier = today - timedelta(days=x)
            attendees_for_day = attendees.filter(order__created_at__day=one_day_earlier.day)

            tickets_sum = 0
            for attendee in attendees_for_day:
                tickets_sum += 1

            tickets_label.append("%s" % (tickets_sum))
            day_label.append("%s %s" % (one_day_earlier.strftime('%b'), one_day_earlier.day))

        tickets_label = list(reversed(tickets_label))
        day_label = list(reversed(day_label))
        graph_data = {'tickets_label':tickets_label, 'day_label':day_label}
        return graph_data
            
    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        slug = kwargs['slug']
        event = self.get_event(slug)

        all_attendees = Attendee.objects.filter(order__event=event).order_by('order__created_at')

        if 'Export To Excel' in data:
            return self.export_to_excel(event, all_attendees.filter(order__failed=False))


        if 'stop_sales' in data:
            if data['stop_sales'] == 'true':
                event.ticket_sales = False
                messages.warning(request, 'Ticket sales are now stopped. You may resume them at any time.')
            else:
                event.ticket_sales = True
                messages.success(request, 'Ticket sales have resumed.')
            event.save()

        # Undoing a deletion of an event
        if "Undo Delete" in data:
            event.deleted = False
            event.save()
            messages.success(request, 'Event recovered Successfully')

        if "Archive" in data:
            event.active = False
            event.save()
            messages.info(request, """Successfully archived '%s' """ %
                             (event.title))

        if "Re-Open" in data:
            event.active = True
            event.save()
            messages.success(request,  """Successfully unarchived '%s' """ %
                             (event.title))

        if "Delete" in data:
            event.active = False
            event.deleted = True
            event.save()
            messages.warning(request, 'Event Deleted Successfully')

        view_name = "events:dashboard"
        return HttpResponseRedirect(reverse(view_name, kwargs={"slug": event.slug}))


    def get(self, request, *args, **kwargs):

        context = {}
        slug = kwargs['slug']
        house = self.get_house()
        event = self.get_event(slug)

        event_referer_domain = EventRefererDomain.objects.filter(event=event).order_by("-count").first()
        context["event_referer_domain"] = event_referer_domain

        # Check if event should be archived or not
        archive_past_events(event)

        dashboard_events = self.get_events()
        tickets = self.get_tickets(event)
        questions = EventQuestion.objects.filter(event=event, question__deleted=False, question__approved=True)
        email = EventEmailConfirmation.objects.get(event=event)
        refund_requests = EventRefundRequest.objects.filter(order__event=event, processed=False, dismissed=False)

        if event.active == False:
            context["inactive_event_tab"] = True
            context["event_tab"] = False
        else:
            context["event_tab"] = True

        context["refund_requests"] = refund_requests
        context["email"] = email
        context["questions"] = questions
        context["tickets"] = tickets
        context["total_sales"] = self.get_total_sales(event)
        context["graph_data"] = self.graph_data(event)

        context["dashboard_events"] = dashboard_events
        context["house"] = house
        context["event"] = event
        context["request"] = request
        return render(request, self.template_name, context)


    def export_to_excel(self, event, attendees):

        event_questions = EventQuestion.objects.filter(
            event=event, order_question=False, question__deleted=False)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
        response['Content-Disposition'] = 'attachment; filename={event}-guest-list.xlsx'.format(
            event=event.slug)
        workbook = Workbook()

        # Get active worksheet/tab
        worksheet = workbook.active
        worksheet.title = 'Attendees'

        # Define the titles for columns
        columns = ['Name', 'Ticket', 'Order No.', 'Gender', 'Age',
                    'Refunded', 'Address', 'City', 'Region', 'Country', ]
        for event_question in event_questions:
            columns.append(event_question.question.title)
        row_num = 1

        # Assign the titles for each cell of the header
        for col_num, column_title in enumerate(columns, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = column_title

        # Iterate through all movies
        for attendee in attendees:
            row_num += 1

            answers = Answer.objects.filter(attendee=attendee, question__question__deleted=False)

            # Define the data for each cell in the row
            row = []
            row.append(attendee.name)
            row.append(attendee.ticket.title)
            row.append(attendee.order.number)
            if attendee.gender:
                row.append(attendee.gender)
            else:
                row.append("N/A")

            if attendee.age:
                row.append(attendee.age)
            else:
                row.append("N/A")

            if attendee.active:
                row.append("No")
            else:
                row.append("Yes")

            if attendee.address:
                try:
                    row.append(attendee.address)
                except:
                    row.append("No Address")

                try:
                    row.append(attendee.city.name)
                except:
                    row.append("No City")
                
                try:
                    row.append(attendee.region.name)
                except:
                    row.append("No Region")

                try:
                    row.append(attendee.country.name)
                except:
                    row.append("No Country")
                    
            else:
                row.append("No Address")
                row.append("No City")
                row.append("No Region")
                row.append("No Country")

            for event_question in event_questions:
                value = "N/A"
                for answer in answers:
                    if answer.question.pk == event_question.pk:
                        value = answer.value
                row.append(value)

            # Assign the data for each cell of the row
            for col_num, cell_value in enumerate(row, 1):
                wrapped_alignment = Alignment(vertical='center', wrap_text=True)
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value
                cell.alignment = wrapped_alignment

        # Change column widths
        name_column_letter = get_column_letter(1)
        ticket_name_column_letter = get_column_letter(2)
        note_column_letter = get_column_letter(6)

        name_column_dimensions = worksheet.column_dimensions[name_column_letter]
        ticket_name_column_dimensions = worksheet.column_dimensions[ticket_name_column_letter]
        note_column_dimensions = worksheet.column_dimensions[note_column_letter]

        name_column_dimensions.width = 30
        ticket_name_column_dimensions.width = 30
        note_column_dimensions.width = 30

        for x in range(7, (event_questions.count() + 11)):
            column_letter = get_column_letter(x)
            column_dimensions = worksheet.column_dimensions[column_letter]
            column_dimensions.width = 40

        workbook.save(response)

        return response



class EventCheckoutView(FormView):
    template_name = "events/event_checkout_form.html"

    def get_success_url(self):
        view_name = "events:landing"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

    def get_successful_order_url(self, order):
        view_name = "order_detail_public"
        return reverse(view_name, kwargs={"public_id": order.public_id})

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_cart(self):
        cart_id = self.request.session.get('cart')
        if cart_id:
            cart = EventCart.objects.get(id=cart_id)
        else:
            return None
        return cart



    def get_context_data(self, data=None, errors=None, *args, **kwargs):
        context = {}
        request = self.request
        slug = self.kwargs['slug']
        event = self.get_event(slug)
        cart = self.get_cart()
        cart_items = EventCartItem.objects.filter(event_cart=cart)
        attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
            
        context["errors"] = errors
        context["cart_items"] = cart_items
        context["cart"] = cart
        context["attendee_common_questions"] = attendee_common_questions
        context["event"] = event
        context["public_key"] = settings.STRIPE_PUBLIC_KEY
        context["total"] = cart.total * decimal.Decimal(100.00)
        context["data"] = data
        return context


    def get(self, request, *args, **kwargs):
        # Check if the user should be here in the first place
        cart = self.get_cart()
        cart_items = EventCartItem.objects.filter(event_cart=cart)
        if not cart_items.exists():
            return HttpResponseRedirect(self.get_success_url())

        return render(request, self.template_name, self.get_context_data())


    def validate_data(self, data, event, cart):
        errors = {}

        # Check buyer name and email
        print(data["name"])
        if data["name"] == "":
            errors["name"] = "Please enter the buyers full name."

        if data["email"] == "":
            errors["email"] = "Please enter your email address. Watch for typos, your tickets get sent there!"
        else:
            try:
                validate_email(data["email"])
            except:
                errors["email"] = "Invalid email address, please enter a valid email address so we can send your ticket there!"


        order_questions = EventQuestion.objects.filter(event=event, order_question=True, question__deleted=False, question__approved=True).order_by("question__order")
        for order_question in order_questions:
            value = data["%s_order_question" % (order_question.question.id)]

            if order_question.question.required and value == "":
                if order_question.question.question_type == "Simple" or order_question.question.question_type == "Long":
                    errors["%s_order_question" % (
                        order_question.question.id)] = "Please enter a valid answer for question '%s'." % (order_question.question.title)

        cart_items = EventCartItem.objects.filter(event_cart=cart)
        attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)

        for cart_item in cart_items:
            if not cart_item.ticket.express:
                for quantity in range(cart_item.quantity):
                    attendee_name = data["%s_%s_name" % (quantity, cart_item.ticket.id)]
                    
                    if attendee_name == "":
                        errors["%s_%s_name" % (quantity, cart_item.ticket.id)] = "Please enter the attendees full name."

                    if attendee_common_questions.age:
                        attendee_age = data["%s_%s_age" % (quantity, cart_item.ticket.id)]

                        if attendee_common_questions.age_required:
                            if attendee_age == "":
                                errors["%s_%s_age" % (quantity, cart_item.ticket.id)] = "Please enter the attendees age."

                    if attendee_common_questions.address:
                        try:
                            attendee_address = data["%s_%s_address" % (quantity, cart_item.ticket.id)]
                            if attendee_common_questions.address_required:
                                if attendee_address == "":
                                    errors["%s_%s_address" % (quantity, cart_item.ticket.id)] = "Please enter the attendees address."
                        except:
                            pass

                    attendee_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id, question__deleted=False, question__approved=True).order_by("question__order")
                    for attendee_question in attendee_questions:
                        value = data["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)]

                        if attendee_question.question.required and value == "":
                            if attendee_question.question.question_type == "Simple" or attendee_question.question.question_type == "Long":
                                errors["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)] = "Please enter a valid answer for question '%s'." % (attendee_question.question.title)


        return errors



    def post(self, request, *args, **kwargs):
        data = request.POST

        print("\n\nerrors")
        print(data)
        print("errors\n\n")

        errors = {}
        slug = kwargs['slug']
        event = self.get_event(slug)
        cart = self.get_cart()

        errors = self.validate_data(data, event, cart)
        print("\n\nerrors")
        print(errors)
        print("errors\n\n")

        # =========================================== FIRST CHECK =================================================
        # The first check is to see if the form is passing basic validation on the data. Once we know the form is valid 
        # we can comfortably create the order and transaction models and move onto checking if payment is also valid.
        if errors:
            return self.render_to_response(self.get_context_data(data=data, errors=errors))


        # Get buyer name and email address
        name = data['name']
        email = data['email']


        # ====================== Create Arqam House Profile and Subscribe them to the house ===========================
        # Check if user exists in the system 
        email = email.lower()
        try:
            profile = Profile.objects.get(email=email)
            account_created = False

        # If the user doesn't exist at all then we need to create a customer
        except:
            profile_temp_password = get_random_string(length=10)
            profile = Profile.objects.create_user(name=data["name"], email=email, password=profile_temp_password, temp_password=profile_temp_password)
            self.send_new_profile_email(profile, profile_temp_password)
            account_created = True


        # Try for subscriber
        # Either they are already a subscriber 
        try:
            subscriber = Subscriber.objects.get(profile=profile, house=event.house)
            event_order = EventOrder.objects.filter(event=event, email=email).exists()
            if not event_order:
                subscriber.attendance_total = subscriber.attendance_total + 1
                subscriber.events.add(event)
                if subscriber.attendance_total > subscriber.events_total:
                    subscriber.events_total += 1
                subscriber.save()

        # Or we need to create a subscriber
        except Exception as e:
            print(e)
            subscriber = Subscriber.objects.create(profile=profile, house=event.house, events_total=1, attendance_total=1)
            subscriber.events.add(event)



        # =================================== SECOND CHECK (if payment required) =======================================
        # Only get the Stripe Token if payment enabled
        if cart.pay:

            # We need to do a sanity check to make sure that the stripe token is in the data
            try:
                stripe_token = data["stripeToken"]
            except Exception as e:
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))



            # =========================================== Check if the charge succeeds or not ====================================================================
            stripe.api_key = settings.STRIPE_SECRET_KEY

            charge = None
            
            try:

                if profile.stripe_customer_id:
                    customer = stripe.Customer.retrieve(profile.stripe_customer_id)
                else:
                    customer = stripe.Customer.create(source=stripe_token, email=email, name=data['name'])
                    print(customer)
                    profile.stripe_customer_id = customer.id
                    profile.save()

                # Charge the card
                charge = stripe.Charge.create(
                            amount = int(cart.total * 100),
                            currency = 'cad',
                            description = self.get_charge_description(event, cart),
                            # source = stripe_token,
                            customer = customer.id,
                            metadata = {
                                'transaction_amount': cart.total,
                                'transaction_arqam_amount': cart.arqam_charge,
                                'transaction_stripe_amount': cart.stripe_charge,
                                'transaction_house_amount': cart.total_no_fee,
                                'buyer_email': data['email'],
                                'buyer_name': data['name'],
                                'cart_id': cart.id,
                                'event_name': event.title,
                                'event_id': event.pk,
                                'house_name': event.house.name,
                                'house_id': event.house.pk
                                },
                            statement_descriptor=self.get_charge_descriptor(event),
                        )

                print("Charge goes here")
                print(charge)
                print("Charge goes here")

            except stripe.error.CardError as e:
                print(e)
                errors["payment"] = e.error.message
                charge_error = ChargeError.objects.create(event_cart=cart,
                    payment_id=e.error.charge, failure_code=e.error.code, failure_message=e.error.message, outcome_type=e.error.type, network_status=e.http_status, reason=e.error.param, email=data["email"], name=data["name"])
                return self.render_to_response(self.get_context_data(data=data, errors=errors))
                
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))
            
            except Exception as e:
                print(e)
                errors["payment"] = "Your payment was not processed. A network error prevented payment processing, please try again later."
                self.send_error_email(event, e, data)
                return self.render_to_response(self.get_context_data(data=data, errors=errors))




        # ====================================================  Handling all the form data =======================================================================
        # we know that this information is valid and won't giev and issues. All we have to do is save it here basically.


        # Create Transaction Object
        transaction = Transaction.objects.create(house=event.house, name=name)
        # transaction.save()

        # Create Order Object
        order = EventOrder.objects.create(name=name, email=email, event=event, event_cart=cart, transaction=transaction, house_created=cart.house_created)
        # order.save()

        # Get Buyer questions and make answers
        order_questions = EventQuestion.objects.filter(event=event, order_question=True, question__deleted=False, question__approved=True).order_by("question__order")
        for order_question in order_questions:
            value = data["%s_order_question" % (order_question.question.id)]

            # Create Order answers
            order_answer = OrderAnswer.objects.create(question=order_question, value=value, order=order)
            order_answer.save()

        # get answers from attendees 
        cart_items = EventCartItem.objects.filter(event_cart=cart)
        attendee_common_questions = AttendeeCommonQuestions.objects.get(event=event)
        

        for cart_item in cart_items:

            if cart_item.ticket.express:
                for quantity in range(cart_item.quantity):

                    attendee_name = "%s-%s" % (order.name, int(quantity)+1)
                    if cart_item.donation_ticket:
                        attendee = Attendee.objects.create(
                            order=order, ticket=cart_item.ticket, ticket_refund_policy=cart_item.ticket.refund_policy, name=attendee_name, email=email, gender=None,
                            ticket_buyer_price=cart_item.donation_buyer_amount, ticket_price=cart_item.donation_amount, ticket_fee=cart_item.donation_fee,
                            ticket_pass_fee=True)
                    else:
                        attendee = Attendee.objects.create(
                            order=order, ticket=cart_item.ticket, ticket_refund_policy=cart_item.ticket.refund_policy, name=attendee_name, email=email, gender=None,
                            ticket_buyer_price=cart_item.ticket_buyer_price, ticket_price=cart_item.ticket_price, ticket_fee=cart_item.ticket_fee,
                            ticket_pass_fee=cart_item.pass_fee)
                    attendee.save()

            else:
                attendee_questions = EventQuestion.objects.filter(tickets__id=cart_item.ticket.id, question__deleted=False, question__approved=True).order_by("question__order")
                for quantity in range(cart_item.quantity):

                    attendee_email = None
                    age = None
                    gender = None
                    address = None
                    
                    # Step 3a get the attendee_name
                    attendee_name = data["%s_%s_name" % (quantity, cart_item.ticket.id)]

                    # Step 3b answers to common questions
                    if attendee_common_questions.email:
                        attendee_email = data["%s_%s_email" % (quantity, cart_item.ticket.id)]

                    if attendee_common_questions.age:
                        age = data["%s_%s_age" % (quantity, cart_item.ticket.id)]

                    if attendee_common_questions.gender:
                        gender = data["%s_%s_gender" % (quantity, cart_item.ticket.id)] 

                    if attendee_common_questions.address:
                        try:
                            address = data["%s_%s_address" % (quantity, cart_item.ticket.id)]
                        except:
                            address = "N/A"

                    if cart_item.donation_ticket:
                        attendee = Attendee.objects.create(
                            order=order, ticket=cart_item.ticket, ticket_refund_policy=cart_item.ticket.refund_policy, name=attendee_name, email=attendee_email, age=age, gender=gender, address=address,
                            ticket_buyer_price=cart_item.donation_buyer_amount, ticket_price=cart_item.donation_amount, ticket_fee=cart_item.donation_fee,
                            ticket_pass_fee=True)
                    else:
                        attendee = Attendee.objects.create(
                            order=order, ticket=cart_item.ticket, ticket_refund_policy=cart_item.ticket.refund_policy, name=attendee_name, email=attendee_email, age=age, gender=gender, address=address,
                            ticket_buyer_price=cart_item.ticket_buyer_price, ticket_price=cart_item.ticket_price, ticket_fee=cart_item.ticket_fee,
                            ticket_pass_fee=cart_item.pass_fee)
                    attendee.save()

                    # Step 3c answers to custom questions
                    for attendee_question in attendee_questions:
                        value = data["%s_%s_%s" % (quantity, attendee_question.question.id, cart_item.ticket.id)]

                        answer = Answer.objects.create(question=attendee_question, value=value, attendee=attendee)
                        answer.save()

        # ==============================  FINALIZE AND SAVE TRANSCATION AND ORDER INFORMATION =============================================
        # If there is a payment to be made
        if cart.pay:
            
            transaction.amount = cart.total
            transaction.arqam_amount = cart.arqam_charge
            transaction.stripe_amount = cart.stripe_charge
            transaction.house_amount = cart.total_no_fee

            transaction.payment_id = charge['id']
            transaction.last_four = charge.source['last4']
            transaction.brand = charge.source['brand']
            transaction.network_status = charge.outcome['network_status']
            transaction.risk_level = charge.outcome['risk_level']
            transaction.seller_message = charge.outcome['seller_message']
            transaction.outcome_type = charge.outcome['type']
            transaction.email = email
            transaction.name = data['name']
            transaction.address_line_1 = charge.source['address_line1']
            transaction.address_state = charge.source['address_state']
            transaction.address_postal_code = charge.source['address_zip']
            transaction.address_city = charge.source['address_city']
            transaction.address_country = charge.source['address_country']
            transaction.save()

            cart.processed = True
            cart.update_tickets_available()
            cart.save()
            del request.session['cart']
            request.session.modified = True

            print("Cart Processed")
            print(cart.processed)

            self.send_confirmation_email(event, data['email'], order)
            self.send_owner_confirmation_email(event, order)
            

            if account_created:
                messages.success(request, f"Congratulations! tickets are now linked to {email}, please login with provided temporary login to view all orders and login to live events.")
            else:
                messages.success(request, "Congratulations! You're all set.")
            return HttpResponseRedirect(self.get_successful_order_url(order))

        # If there is no payment to be made
        else:

            transaction.amount = 0.00
            transaction.arqam_amount = 0.00
            transaction.stripe_amount = 0.00
            transaction.house_amount = 0.00

            transaction.email = email
            transaction.name = data["name"]

            cart.processed = True
            cart.update_tickets_available()
            cart.save()
            del request.session['cart']
            request.session.modified = True

            self.send_confirmation_email(event, email, order)
            self.send_owner_confirmation_email(event, order)

            if account_created:
                messages.success(request, f"Congratulations! tickets are now linked to {email}, please login with provided credentials to view all orders and login to live events.")
            else:
                messages.success(request, "Congratulations! You're all set.")
            return HttpResponseRedirect(self.get_successful_order_url(order))


        return render(request, self.template_name, self.get_context_data(data))


    def send_new_profile_email(self, profile, password):

        # Compose Email
        subject = 'Arqam House Account Credentials'
        context = {}
        context["profile"] = profile
        context["password"] = password
        html_content = render_to_string('emails/account_creation_from_order.html', context)
        text_content = strip_tags(html_content)
        from_email = 'Arqam House <info@arqamhouse.com>'
        to = ['%s' % (profile.email)]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return "Done"


    def send_confirmation_email(self, event, email, order):

        # PDF Attachment
        pdf_context = {}
        pdf_context["order"] = order
        pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
        pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
        pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

        # Compose Email
        subject = 'Order Confirmation For %s' % (event.title)
        email_confirmation = EventEmailConfirmation.objects.get(event=event)
        context = {}
        house_users = HouseUser.objects.filter(house=event.house, profile__is_superuser=False)
        context["event"] = event
        context["house_users"] = house_users
        context["message"] = email_confirmation.message
        context["order"] = order
        html_content = render_to_string('emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)
        from_email = 'Order Confirmation <info@arqamhouse.com>'
        to = ['%s' % (email)]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.attach("confirmation.pdf", pdf_file, 'application/pdf')
        email.send()
        return "Done"

    def send_owner_confirmation_email(self, event, order):

        to = []
        if event.house.order_confirmations:
            to.append(event.house.email)

        house_users = HouseUser.objects.filter(house=event.house).exclude(profile__email=event.house.email)
        for house_user in house_users:
            if house_user.order_confirmations:
                to.append(house_user.profile.email)

        if to:
            for x in to:
                # Compose Email
                subject = 'New Order For %s' % (event.title)
                context = {}
                context["event"] = event
                context["order"] = order
                html_content = render_to_string('emails/owner_order_confirmation.html', context)
                text_content = strip_tags(html_content)
                from_email = 'New Order <orders@arqamhouse.com>'
                email = EmailMultiAlternatives(subject=subject, body=text_content,
                                            from_email=from_email, to=[x])
                email.attach_alternative(html_content, "text/html")
                email.send()

        return "Done"

    def send_error_email(self, event, error, data):
        # Compose Email
        subject = 'Checkout Error %s' % (event.title)
        context = {}
        context["event"] = event
        text_content = "There was an error while someone was trying to checkout for event '%s' with event id %s. Error: %s. Data: %s" % (event.title, event.pk, error, data)
        from_email = 'Chekout Error <info@arqamhouse.com>'
        to = ["errors@arqamhouse.com"]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.send()
        return "Done"

    def get_charge_description(self, event, cart):
        return ("Cart #: %s for Event: %s (Event ID: %s)." % (cart.id, event.title, event.id))


    def get_charge_descriptor(self, event):
        event_title = ''.join(e for e in event.title if e.isalnum())
        event_title = "AH* %s" % (event_title)
        if len(event_title) > 20:
            descriptor = event_title[:19]
            # descriptor = "AH* %s" % (event.house.name)
            # if len(descriptor) > 20:
                # descriptor = 'Arqam House Inc.'
        else:
            descriptor = event_title
        return descriptor




class PastEventsView(HouseAccountMixin, UserPassesTestMixin, EventMixin, ListView):
    model = Event
    template_name = "events/past_events.html"

    def test_func(self):
        house_users = HouseUser.objects.filter(profile=self.request.user)
        house = self.get_house()
        for house_user in house_users:
            if house == house_user.house:
                return True
        return False


    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        inactive_events = self.get_inactive_events(house=house)
        deleted_events = self.get_deleted_events(house=house)
        context["events"] = inactive_events
        context["deleted_events"] = deleted_events
        context["house"] = house
        context["dashboard_events"] = self.get_events()
        context["past_event_tab"] = True
        return context



class EventCreateView(HouseAccountMixin, CreateView):
    model = Event
    form_class = EventMainForm
    template_name = "events/event_main_form.html"

    def get_success_url(self):
        event = self.object
        view_name = "events:update_venue"
        return reverse(view_name, kwargs={'slug': event.slug})

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["create_event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        data = request.POST
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        house = self.get_house()
        form.instance.house = house
        self.object = form.save()
        self.object.active = True
        self.object.save()

        messages.success(request, 'Event Created!')

        if settings.DEBUG == False:
            self.send_text_message(self.object)

        valid_data = super(EventCreateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    
    def send_text_message(self, event):
        account_sid = settings.ACCOUNT_SID
        auth_token = settings.AUTH_TOKEN
        client = Client(account_sid, auth_token)
        message = client.messages.create(
                    body="A New Event Was Created!\nHouse Name: %s\nEvent Name: %s\nEvent URL: www.arqamhouse.com/events/%s\n- Arqam House" % (event.house.name, event.title, event.slug),
                    from_='+16475571902',
                    to='+16472985582'
                )




class EventDescriptionView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):

    model = Event
    form_class = EventDescriptionForm
    template_name = "events/event_description.html"

    def get_success_url(self):
        view_name = "events:landing"
        return reverse(view_name, kwargs={"slug": self.object.slug})

    def get_edit_url(self):
        view_name = "events:update"
        return reverse(view_name, kwargs={"slug": self.object.slug})

    def get_success_delete_url(self):
        view_name = "events:past"
        return reverse(view_name)

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["event"] = self.object
        
        if self.object.active == False:
            context["inactive_event_tab"] = True
            context["events_tab"] = False
        else:
            context["events_tab"] = True

        context["update_event"] = True

        if self.object.active:
            context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.GET
        form = EventDescriptionForm(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()
        valid_data = super(EventDescriptionView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))



class EventImageView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):

    model = Event
    form_class = EventImageForm
    template_name = "events/event_image.html"

    def get_success_url(self):

        if not self.object.image:
            view_name = "events:update_image"
        elif self.object.description:
            view_name = "events:landing"
        elif not self.object.description:
            view_name = "events:update_description"
        else:
            view_name = "events:landing"

        return reverse(view_name, kwargs={"slug": self.object.slug})

    def get_edit_url(self):
        view_name = "events:update"
        return reverse(view_name, kwargs={"slug": self.object.slug})

    def get_success_delete_url(self):
        view_name = "events:past"
        return reverse(view_name)

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["event"] = self.object
        context["time"] = timezone.now()
        
        if self.object.active == False:
            context["inactive_event_tab"] = True
            context["events_tab"] = False
        else:
            context["events_tab"] = True

        context["update_event"] = True

        if self.object.active:
            context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.GET
        form = EventImageForm(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        if "Remove" in data:
            self.object.image = None
            self.object.save()
            messages.warning(request, 'Event image successfully removed')

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()
        valid_data = super(EventImageView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class EventVenueView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):

    model = Event
    form_class = EventVenueForm
    template_name = "events/event_venue.html"

    def get_success_url(self):

        if self.object.image and self.object.description:
            view_name = "events:landing"
        
        elif not self.object.image and self.object.description:
            view_name = "events:landing"

        elif self.object.image and not self.object.description:
            view_name = "events:landing"

        elif not self.object.image and not self.object.description:
            view_name = "events:update_image"

        else:
            view_name = "events:landing"

        return reverse(view_name, kwargs={"slug": self.object.slug})


    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["event"] = self.object
        
        if self.object.active == False:
            context["inactive_event_tab"] = True
            context["events_tab"] = False
        else:
            context["events_tab"] = True

        context["update_event"] = True

        if self.object.active:
            context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.GET
        form = EventVenueForm(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()
        valid_data = super(EventVenueView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class EventURLView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):

    model = Event
    form_class = EventURLForm
    template_name = "events/event_url.html"

    def get_success_url(self):
        if self.object.venue_name:
            view_name = "events:landing"
        else:
            view_name = "events:update_url"
        return reverse(view_name, kwargs={"slug": self.object.slug})


    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["event"] = self.object
        
        if self.object.active == False:
            context["inactive_event_tab"] = True
            context["events_tab"] = False
        else:
            context["events_tab"] = True

        context["update_event"] = True

        if self.object.active:
            context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.GET

        if 'url' in data:

            url = data['url']
            slugify_url = slugify(url)
            
            if Event.objects.filter(slug=slugify_url).exclude(slug=slug).exists():
                return HttpResponse("taken")
            else:
                return HttpResponse("not_taken")
        else:
            form = EventURLForm(instance=self.object)
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()
        valid_data = super(EventURLView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))




class EventUpdateView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventMainForm
    template_name = "events/event_main_form.html"

    def get_success_url(self):
        view_name = "events:landing"
        return reverse(view_name, kwargs={"slug": self.object.slug})


    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            raise Http404

    def get_context_data(self, form, *args, **kwargs):
        context = {}
        house = self.get_house()
        context["form"] = form
        context["house"] = house
        context["event"] = self.object
        
        if self.object.active == False:
            context["inactive_event_tab"] = True
            context["events_tab"] = False
        else:
            context["events_tab"] = True

        context["update_event"] = True

        if self.object.active:
            context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)

        data = request.GET

        if 'url' in data:

            url = data['url']
            slugify_url = slugify(url)
            
            if Event.objects.filter(slug=slugify_url).exists():
                return HttpResponse("taken")
            else:
                return HttpResponse("not_taken")
        else:
            initial = {}
            if self.object.start:
                initial["start"] = timezone.localtime(self.object.start).strftime("%m/%d/%Y %I:%M %p")
            if self.object.end:
                initial["end"] = timezone.localtime(self.object.end).strftime("%m/%d/%Y %I:%M %p")
            form = EventMainForm(instance=self.object, initial=initial)
            
            return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        slug = kwargs['slug']
        self.object = self.get_event(slug)
        data = request.POST

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, request):
        data = request.POST
        self.object = form.save()
        messages.success(request, 'Event Updated Successfully!')
            
        valid_data = super(EventUpdateView, self).form_valid(form)
        return valid_data

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))





