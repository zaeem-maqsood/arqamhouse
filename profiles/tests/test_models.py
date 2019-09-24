from django.test import TestCase
from profiles.models import Profile


class ProfileModelTestCase(TestCase):

    def setUp(self):

        # Create a profile
        Profile.objects.create(email="zaeem.maqsood@gmail.com", password="Ed81ae9600!", name="Zaeem Maqsood")

        # Create a profile
        Profile.objects.create(email="zaeem@arqamhouse.com", password="Ed81ae9600!", name="Zaeem Maqsood")

    def test_slugs(self):
        profile = Profile.objects.get(email="zaeem.maqsood@gmail.com")
        profile2 = Profile.objects.get(email="zaeem@arqamhouse.com")
        self.assertNotEquals(profile.slug, profile2.slug)
