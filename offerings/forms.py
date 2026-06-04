from django import forms
from django.conf import settings
from .models import Offering, Booking


def validate_image_size(image):
    max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 4)
    if image and hasattr(image, 'size') and image.size > max_mb * 1024 * 1024:
        raise forms.ValidationError(f"L'image ne doit pas dépasser {max_mb} Mo.")


class OfferingForm(forms.ModelForm):
    class Meta:
        model = Offering
        fields = [
            'title', 'category', 'description',
            'price_type', 'price',
            'location', 'date_time', 'image', 'is_active',
        ]
        labels = {
            'title': 'Titre',
            'category': 'Catégorie',
            'description': 'Description',
            'price_type': 'Type de tarif',
            'price': 'Montant',
            'location': 'Lieu (optionnel)',
            'date_time': 'Date & heure (optionnel)',
            'image': 'Photo',
            'is_active': 'Prestation visible sur le site',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'ex. Atelier aquarelle en famille, Concert privé jazz…'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': (
                    'Décrivez votre prestation : ce que vous apportez, '
                    'combien de personnes peuvent participer, la durée, '
                    'le matériel fourni…'
                ),
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'ex. Chez vous (Montréal), Île-de-France…'
            }),
            'date_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'price': forms.NumberInput(attrs={
                'placeholder': '0.00', 'min': '0', 'step': '0.01'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_image_size(image)
        return image

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get('price_type')
        price = cleaned_data.get('price')
        if price_type in (Offering.PRICE_FIXED, Offering.PRICE_HOURLY) and not price:
            self.add_error('price', 'Veuillez indiquer un montant pour ce type de tarif.')
        return cleaned_data


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['offering', 'message', 'date_wish', 'guests', 'address']
        labels = {
            'offering':  'Prestation souhaitée',
            'message':   'Votre message',
            'date_wish': 'Date souhaitée',
            'guests':    'Nombre de participants',
            'address':   'Adresse chez vous',
        }
        widgets = {
            'offering': forms.Select(),
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': (
                    'Présentez-vous, décrivez votre espace et ce que vous attendez '
                    'de cette prestation…'
                ),
            }),
            'date_wish': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d',
            ),
            'guests': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
            'address': forms.TextInput(attrs={
                'placeholder': 'ex. 12 rue des Arts, Montréal, QC'
            }),
        }

    def __init__(self, *args, artist=None, **kwargs):
        super().__init__(*args, **kwargs)
        if artist:
            self.fields['offering'].queryset = (
                Offering.objects.filter(artist=artist, is_active=True)
            )


class ArtistNoteForm(forms.ModelForm):
    """Form for artists to respond to a booking request."""
    class Meta:
        model = Booking
        fields = ['artist_note']
        labels = {'artist_note': 'Votre réponse à l\'hôte (optionnel)'}
        widgets = {
            'artist_note': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ajoutez un message pour l\'hôte…',
            }),
        }
