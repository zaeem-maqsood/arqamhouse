from .base import *    


class OrderListView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, ListView):
    model = EventOrder
    template_name = "events/orders/event_orders.html"

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())



    def post(self, request, *args, **kwargs):
        data = request.POST
        print("It came to post")
        print(data)
        event = self.get_event(self.kwargs['slug'])
        all_orders = EventOrder.objects.select_related('transaction').filter(event=event).order_by('-created_at')
        search_terms = data["search"].split()

        if data["search"] == '':
            orders = all_orders
        else:
            counter = 0
            for search_term in search_terms:
                if counter == 0:
                    orders = all_orders.filter(Q(name__icontains=search_term) | Q(
                        transaction__amount__icontains=search_term) | Q(email__icontains=search_term))
                else:
                    orders = orders.filter(Q(name__icontains=search_term) | Q(
                        transaction__amount__icontains=search_term) | Q(email__icontains=search_term))
                print(counter)
                counter += 1
        
        orders = orders[:100]
        print(orders)
        html = render_to_string('events/orders/orders-dynamic-table-body.html', {'orders': orders, 'request':request})
        return HttpResponse(html)

    def get_context_data(self, *args, **kwargs):
        context = {}
        house = self.get_house()
        event = self.get_event(self.kwargs['slug'])
        orders = EventOrder.objects.filter(event=event).order_by('-created_at')
        print(orders)
        
        context["house"] = house
        context["orders"] = orders
        context["event"] = event
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context





class OrderPublicDetailView(DetailView):
    model = EventOrder
    template_name = "events/orders/event_order_detail_public.html"

    def get_order(self, order_id):
        try:
            order = EventOrder.objects.get(public_id=order_id)
            return order
        except Exception as e:
            print(e)
            raise Http404

    def view_tickets(self, event, order):

        # PDF Attachment
        pdf_context = {}
        pdf_context["order"] = order
        
        pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
        pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))

        pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

        response = HttpResponse(pdf_file, content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=confirmation.pdf'
        return response

    def post(self, request, *args, **kwargs):
        data = request.POST
        order_id = self.kwargs['public_id']
        order = self.get_order(order_id)
        event = order.event
        print(data)
        if 'Refund' in data:
            print("single refund")
            attendee = Attendee.objects.get(id=data["Refund"])
            request_refund = EventRefundRequest.objects.create(order=order, attendee=attendee)
            messages.success(request, "Refund Request Sent! Please wait a couple of days for your refund to be processed.")

        if 'Full Refund' in data:
            request_refund = EventRefundRequest.objects.create(order=order)
            messages.success(request, "Refund Request Sent! Please wait a couple of days for your refund to be processed.")

        view_name = "order_detail_public"
        return HttpResponseRedirect(reverse(view_name, kwargs={"public_id": order.public_id}))


    def get(self, request, *args, **kwargs):
        context = {}
        data = request.GET
        order_id = self.kwargs['public_id']
        order = self.get_order(order_id)
        event = order.event

        if 'view_tickets' in data:
            return self.view_tickets(event, order)

        attendees = Attendee.objects.filter(order=order)    

        show_total_order_refund = True
        for attendee in attendees:
            if attendee.get_refundable_or_not() == 'Refund Not Available':
                show_total_order_refund = False
                break
        context["show_total_order_refund"] = show_total_order_refund

        active_attendees = attendees.filter(active=True)

        current_time = timezone.localtime(timezone.now())
        event_start_time = event.start
        time_left = event_start_time - current_time
        time_left_days = time_left.days
        time_left_hours = time_left.seconds//3600

        refund_requests = EventRefundRequest.objects.filter(order=order, dismissed=False, processed=False)
        print("Refund Requests")
        print(refund_requests)
        context["refund_requests"] = refund_requests

        context["event_start_time"] = event_start_time
        context["time_left_days"] = time_left_days
        context["time_left_hours"] = time_left_hours
        context["active_attendees"] = active_attendees
        context["event_cart_items"] = order.event_cart.eventcartitem_set.all
        context["event"] = event
        context["order"] = order
        context["attendees"] = attendees

        return render(request, self.template_name, context)





class OrderDetailView(HouseAccountMixin, EventSecurityMixin, UserPassesTestMixin, FormView):
    model = EventOrder
    template_name = "events/orders/event_order_detail.html"

    def get_success_url(self):
        view_name = "events:order_list"
        return reverse(view_name, kwargs={"slug": self.kwargs['slug']})

    def get_event(self, slug):
        try:
            event = Event.objects.get(slug=slug)
            return event
        except Exception as e:
            print(e)
            raise Http404

    def get_order(self, order_id):
        try:
            order = EventOrder.objects.get(public_id=order_id)
            return order
        except Exception as e:
            print(e)
            raise Http404

    def get_context_data(self, *args, **kwargs):
        context = {}

        slug = self.kwargs['slug']
        order_id = self.kwargs['public_id']
        event = self.get_event(slug)
        order = self.get_order(order_id)
        house = self.get_house()
        subscriber = Subscriber.objects.get(house=event.house, profile__email=order.email)
        

        house_balance = HouseBalance.objects.get(house=house)
        attendees = Attendee.objects.filter(order=order)
        active_attendees = attendees.filter(active=True)
        context["active_attendees"] = active_attendees
        event_order_refunds = EventOrderRefund.objects.filter(order=order)
        if event_order_refunds:
            total_payout = event_order_refunds.aggregate(Sum('refund__house_amount'))
            total_payout = order.event_cart.total_no_fee - total_payout["refund__house_amount__sum"]
            if total_payout < 0.00:
                total_payout = 0.00
            total_payout = '{0:.2f}'.format(total_payout)
            context["total_payout"] = total_payout

        refund_requests = EventRefundRequest.objects.filter(order=order)
        context["refund_requests"] = refund_requests

        context["subscriber"] = subscriber
        context["house_balance"] = house_balance
        context["event_cart_items"] = order.event_cart.eventcartitem_set.all
        context["house"] = house
        context["event"] = event
        context["order"] = order
        context["event_order_refunds"] = event_order_refunds
        context["attendees"] = attendees
        context["event_tab"] = True
        context["dashboard_events"] = self.get_events()
        return context

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


    def send_refund_confirmation_email(self, order):
        
        # PDF Attachment
        pdf_context = {}
        event_order_refunds = EventOrderRefund.objects.filter(order=order)
        pdf_context["event_order_refunds"] = event_order_refunds
        if event_order_refunds:
            total_payout = event_order_refunds.aggregate(Sum('refund__amount'))
            total_payout = order.event_cart.total - total_payout["refund__amount__sum"]
            if total_payout < 0.00:
                total_payout = 0.00
            total_payout = '{0:.2f}'.format(total_payout)
            pdf_context["total_payout"] = total_payout
        
        pdf_context["order"] = order
        pdf_content = render_to_string('pdfs/refund_summary.html', pdf_context)
        pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
        pdf_file = HTML(string=pdf_content).write_pdf(stylesheets=[pdf_css])

        # Compose Email
        subject = 'Order Refund For %s' % (order.event.title)
        context = {}
        context["event"] = order.event
        context["order"] = order
        html_content = render_to_string('emails/order_refund.html', context)
        text_content = strip_tags(html_content)
        from_email = 'Order Refund <info@arqamhouse.com>'
        to = ['%s' % (order.email)]
        email = EmailMultiAlternatives(subject=subject, body=text_content,
                                       from_email=from_email, to=to)
        email.attach_alternative(html_content, "text/html")
        email.attach("updated_confirmation.pdf", pdf_file, 'application/pdf')
        email.send()
        return "Done"


    def view_tickets(self, event, order):

        # PDF Attachment
        pdf_context = {}
        pdf_context["order"] = order
        pdf_content = render_to_string('pdfs/ticket.html', pdf_context)
        pdf_css = CSS(string=render_to_string('pdfs/ticket.css'))
        

        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=tickets.pdf'

        pdf_file = HTML(string=pdf_content).write_pdf(response, stylesheets=[pdf_css])
        return response



    def post(self, request, *args, **kwargs):
        data = request.POST
        print(data)
        slug = kwargs['slug']
        order_id = kwargs['public_id']
        event = self.get_event(slug)
        order = self.get_order(order_id)
        attendees = Attendee.objects.filter(order=order)

        if 'view_tickets' in data:
            return self.view_tickets(event, order)


        if 'Refund' in data:

            attendee_to_be_refunded_id = data['Refund']
            attendee_to_be_refunded = attendees.get(id=attendee_to_be_refunded_id)
            ticket = attendee_to_be_refunded.ticket
            amount = int(attendee_to_be_refunded.ticket_buyer_price * 100)
            if attendee_to_be_refunded.ticket_pass_fee:
                house_amount = int(attendee_to_be_refunded.ticket_price * 100)
            else:
                house_amount = int((attendee_to_be_refunded.ticket_price - attendee_to_be_refunded.ticket_fee) * 100)

            if attendees.filter(active=True, ticket__paid=True).count() == 1 or attendees.filter(active=True, ticket__donation=True).count() == 1:
                partial_refund = False
                full_refund = True
            else:
                partial_refund = True
                full_refund = False

            if attendee_to_be_refunded.active:
                event_order_refund = EventOrderRefund.objects.create(order=order, attendee=attendee_to_be_refunded)
                refund = Refund.objects.create(transaction=order.transaction, amount=(
                    amount/100), house_amount=(house_amount/100), partial_refund=partial_refund)

                try:
                    event_refund_request = EventRefundRequest.objects.get(order=order, attendee=attendee_to_be_refunded, dismissed=False)
                    event_refund_request.processed = True
                    event_refund_request.save()
                except:
                    pass

                
                event_order_refund.refund = refund
                event_order_refund.save()
                
                attendee_to_be_refunded.active = False
                attendee_to_be_refunded.save()
                attendee_to_be_refunded.ticket.amount_sold -= 1
                attendee_to_be_refunded.ticket.sold_out = False
                attendee_to_be_refunded.ticket.save()
                
                order.partial_refund = partial_refund
                order.refunded = full_refund
                order.save()

                stripe.api_key = settings.STRIPE_SECRET_KEY
                response = stripe.Refund.create(charge=order.transaction.payment_id, amount=amount)
            
            # Send Confirmation Email
            self.send_refund_confirmation_email(order)



        # User wants a full refund on the order
        if 'Full Refund' in data:

            try:
                event_refund_request = EventRefundRequest.objects.get(order=order, dismissed=False)
                event_refund_request.processed = True
                event_refund_request.save()
            except:
                pass

            for attendee in attendees:
                if attendee.active and not attendee.ticket.free:
                    amount = int(attendee.ticket_buyer_price * 100)

                    if attendee.ticket_pass_fee:
                        house_amount = int(attendee.ticket_price * 100)
                    else:
                        house_amount = int((attendee.ticket_price - attendee.ticket_fee) * 100)

                    event_order_refund = EventOrderRefund.objects.create(order=order, attendee=attendee)
                    refund = Refund.objects.create(transaction=order.transaction, amount=(amount/100), house_amount=(house_amount/100))

                    event_order_refund.refund = refund
                    event_order_refund.save()
                    attendee.active = False
                    attendee.save()
                    attendee.ticket.amount_sold -= 1
                    attendee.ticket.sold_out = False
                    attendee.ticket.save()
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    response = stripe.Refund.create(charge=order.transaction.payment_id, amount=amount)

                order.refunded = True
                order.save()

            # Send Confirmation email
            self.send_refund_confirmation_email(order)


        return render(request, self.template_name, self.get_context_data(data))






