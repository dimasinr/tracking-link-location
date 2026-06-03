import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import TrackingLink, TrackingHit

class GeolocationTrackingTests(TestCase):
    def setUp(self):
        # Create standard admin user
        self.user = User.objects.create_user(username='admin', password='password123')
        self.client = Client()
        
        # Create a test link
        self.link = TrackingLink.objects.create(
            name="Test Tracker",
            description="Testing GPS Link",
            code="TESTCODE",
            require_gps=True,
            redirect_url="https://example.com/success",
            created_by=self.user
        )

    def test_tracking_link_creation(self):
        self.assertEqual(self.link.code, "TESTCODE")
        self.assertTrue(self.link.require_gps)
        self.assertEqual(self.link.hits.count(), 0)

    def test_consent_view_status(self):
        # Get consent page
        response = self.client.get(f'/t/{self.link.code}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Klaim Hadiah Sekarang")

    def test_track_location_api(self):
        payload = {
            "code": "TESTCODE",
            "latitude": -6.21462,
            "longitude": 106.84513,
            "accuracy": 10,
            "screen_width": 1920,
            "screen_height": 1080
        }
        
        # Call API
        response = self.client.post(
            '/api/track/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertTrue(res_data['success'])
        self.assertEqual(res_data['redirect_url'], "https://example.com/success")
        
        # Verify hit was recorded
        self.assertEqual(self.link.hits.count(), 1)
        hit = self.link.hits.first()
        self.assertEqual(float(hit.latitude), -6.21462)
        self.assertEqual(float(hit.longitude), 106.84513)
        self.assertEqual(hit.accuracy, 10.0)
        self.assertEqual(hit.screen_width, 1920)
