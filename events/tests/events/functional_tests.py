from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from django.urls import reverse
from profiles.models import Profile
from houses.models import House, HouseUser
from payments.models import HouseBalance, HouseBalanceLog
from cities_light.models import City, Region, Country


class EventCreationTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)
            

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
        
    def test_create_event_with_only_title(self):
        
        self.selenium.get('%s%s' % ('http://127.0.0.1:8000', '/house/dashboard'))
        username_input = self.selenium.find_element_by_id("id_email")
        password_input = self.selenium.find_element_by_id("id_password")
        submit = self.selenium.find_element_by_xpath(
            "// button[contains(@class, 'btn btn--primary type--uppercase')]")
        username_input.send_keys('nim36@hotmail.com')
        password_input.send_keys('Ed81ae9600!')
        submit.send_keys(Keys.RETURN)
        # Submit the form

        # Go to create an event
        self.selenium.get('%s%s' % ('http://127.0.0.1:8000', '/events/create'))
        self.selenium.implicitly_wait(3)
        title = self.selenium.find_element_by_id("id_title")
        submit = self.selenium.find_element_by_id("Create")

        # Create Event
        title.send_keys('New Event')
        submit.send_keys(Keys.RETURN)

        # Ends off at event page

    def test_create_paid_ticket(self):

        # navigate to tickets 
        self.selenium.get('%s%s' % ('http://127.0.0.1:8000', '/events/new-event/tickets/list'))
        self.selenium.implicitly_wait(3)
        paid_ticket = self.selenium.find_element_by_id("new_paid_ticket")
        paid_ticket.send_keys(Keys.RETURN)

        # Create new paid ticket view
        title = self.selenium.find_element_by_id("id_title")
        description = self.selenium.find_element_by_id("id_description")
        submit = self.selenium.find_element_by_id("create-ticket")

        title.send_keys('Paid Ticket')
        description.send_keys('An Example of a tickets decription goes here')
        submit.send_keys(Keys.RETURN)
        # Ends off on the ticket list view

    def test_create_free_ticket(self):

        self.selenium.implicitly_wait(3)
        paid_ticket = self.selenium.find_element_by_id("new_free_ticket")
        paid_ticket.send_keys(Keys.RETURN)

        # Create new paid ticket view
        title = self.selenium.find_element_by_id("id_title")
        description = self.selenium.find_element_by_id("id_description")
        submit = self.selenium.find_element_by_id("create-ticket")

        title.send_keys('Free Ticket')
        description.send_keys('An Example of a tickets decription goes here')
        submit.send_keys(Keys.RETURN)
        # Ends off on the ticket list view

    def test_create_donation_ticket(self):

        self.selenium.implicitly_wait(3)
        paid_ticket = self.selenium.find_element_by_id("new_donation_ticket")
        paid_ticket.send_keys(Keys.RETURN)

        # Create new paid ticket view
        title = self.selenium.find_element_by_id("id_title")
        description = self.selenium.find_element_by_id("id_description")
        submit = self.selenium.find_element_by_id("create-ticket")

        title.send_keys('Donation Ticket')
        description.send_keys('An Example of a tickets decription goes here')
        submit.send_keys(Keys.RETURN)
        # Ends off on the ticket list view

    




        

        
