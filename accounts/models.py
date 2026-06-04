from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_ARTIST = 'artist'
    ROLE_CLIENT = 'host'
    ROLE_CHOICES = [
        (ROLE_ARTIST, 'Artiste'),
        (ROLE_CLIENT, 'Hôte'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CLIENT)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.email

    @property
    def is_artist(self):
        return self.role == self.ROLE_ARTIST

    @property
    def is_host(self):
        return self.role == self.ROLE_CLIENT


class ArtistProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='artist_profile'
    )
    discipline = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} — {self.discipline}"
