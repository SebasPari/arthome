from django.db import models
from django.conf import settings


class Offering(models.Model):
    CATEGORY_CLASS = 'class'
    CATEGORY_EVENT = 'event'
    CATEGORY_COMMISSION = 'commission'
    CATEGORY_PERFORMANCE = 'performance'
    CATEGORY_CHOICES = [
        (CATEGORY_CLASS, 'Atelier'),
        (CATEGORY_EVENT, 'Événement'),
        (CATEGORY_COMMISSION, 'Commission'),
        (CATEGORY_PERFORMANCE, 'Spectacle'),
    ]

    PRICE_FIXED = 'fixed'
    PRICE_HOURLY = 'hourly'
    PRICE_FREE = 'free'
    PRICE_CONTACT = 'contact'
    PRICE_CHOICES = [
        (PRICE_FIXED, 'Prix fixe'),
        (PRICE_HOURLY, 'Par heure'),
        (PRICE_FREE, 'Gratuit'),
        (PRICE_CONTACT, 'Sur devis'),
    ]

    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offerings',
        limit_choices_to={'role': 'artist'},
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(max_length=10, choices=PRICE_CHOICES, default=PRICE_FIXED)
    location = models.CharField(max_length=200, blank=True)
    date_time = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to='offerings/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.artist.full_name}"

    def price_display(self):
        if self.price_type == self.PRICE_FREE:
            return 'Gratuit'
        if self.price_type == self.PRICE_CONTACT:
            return 'Sur devis'
        if self.price and self.price_type == self.PRICE_HOURLY:
            return f'{self.price} $/h'
        if self.price:
            return f'{self.price} $'
        return '—'


class Booking(models.Model):
    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_DECLINED  = 'declined'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING,   'En attente'),
        (STATUS_CONFIRMED, 'Confirmée'),
        (STATUS_DECLINED,  'Refusée'),
        (STATUS_CANCELLED, 'Annulée'),
    ]

    offering  = models.ForeignKey(Offering, on_delete=models.CASCADE, related_name='bookings')
    host      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bookings_as_host',
    )
    message   = models.TextField(help_text='Décrivez votre espace, la date souhaitée, le nombre de participants…')
    date_wish = models.DateField(null=True, blank=True, verbose_name='Date souhaitée')
    guests    = models.PositiveSmallIntegerField(default=1, verbose_name='Nombre de participants')
    address   = models.CharField(max_length=255, verbose_name='Adresse', blank=True)
    status    = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    artist_note = models.TextField(blank=True, verbose_name='Réponse de l\'artiste')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.offering.title} — {self.host.full_name} ({self.get_status_display()})"
