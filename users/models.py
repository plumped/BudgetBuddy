from django.db import models
from django.contrib.auth.models import AbstractUser


class Family(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('ADULT', 'Erwachsener'),
        ('CHILD', 'Kind'),
    ]

    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null=True, related_name='members')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='ADULT')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username