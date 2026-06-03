import uuid
from django.db import models
from django.contrib.auth.models import User

class TrackingLink(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=50, unique=True)
    require_gps = models.BooleanField(default=True)
    redirect_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracking_links')

    def __str__(self):
        return f"{self.name} ({self.code})"


class TrackingHit(models.Model):
    tracking_link = models.ForeignKey(TrackingLink, on_delete=models.CASCADE, related_name='hits')
    ip_address = models.GenericIPAddressField()
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    
    country = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    full_address = models.TextField(blank=True, null=True)
    
    isp = models.CharField(max_length=255, blank=True, null=True)
    asn = models.CharField(max_length=255, blank=True, null=True)
    
    browser = models.CharField(max_length=100, blank=True, null=True)
    browser_version = models.CharField(max_length=100, blank=True, null=True)
    os = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    
    language = models.CharField(max_length=100, blank=True, null=True)
    screen_width = models.IntegerField(null=True, blank=True)
    screen_height = models.IntegerField(null=True, blank=True)
    referrer = models.CharField(max_length=500, blank=True, null=True)
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hit on {self.tracking_link.code} at {self.visited_at}"
