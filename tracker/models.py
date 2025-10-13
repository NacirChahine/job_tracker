
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Interview", "Interview"),
        ("Offer", "Offer"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Applied")
    applied_date = models.DateField(default=timezone.now)
    link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.position} at {self.company_name}"
