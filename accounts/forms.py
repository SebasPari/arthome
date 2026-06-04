from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from .models import CustomUser, ArtistProfile


def validate_image_size(image):
    max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 4)
    if image and hasattr(image, 'size') and image.size > max_mb * 1024 * 1024:
        raise forms.ValidationError(f"L'image ne doit pas dépasser {max_mb} Mo.")


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'vous@example.com', 'autocomplete': 'email'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'autocomplete': 'current-password'}),
    )


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••', 'autocomplete': 'new-password'}),
        min_length=8,
    )
    discipline = forms.CharField(
        label='Discipline',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'ex. Illustration, Photographie, Musique…'}),
    )
    bio = forms.CharField(
        label='Courte bio',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Une phrase sur votre pratique'}),
    )

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'role']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Votre nom', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'vous@example.com', 'autocomplete': 'email'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            if user.role == CustomUser.ROLE_ARTIST:
                ArtistProfile.objects.create(
                    user=user,
                    discipline=self.cleaned_data.get('discipline', ''),
                    bio=self.cleaned_data.get('bio', ''),
                )
        return user


class ArtistProfileForm(forms.ModelForm):
    """Form for artists to edit their public profile."""
    full_name = forms.CharField(
        label='Nom complet',
        widget=forms.TextInput(attrs={'placeholder': 'Votre nom'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'vous@example.com'}),
    )

    class Meta:
        model = ArtistProfile
        fields = ['discipline', 'bio', 'location', 'website', 'avatar']
        labels = {
            'discipline': 'Discipline',
            'bio': 'Bio',
            'location': 'Localisation',
            'website': 'Site web',
            'avatar': 'Photo de profil',
        }
        widgets = {
            'discipline': forms.TextInput(attrs={
                'placeholder': 'ex. Illustration, Photographie, Musique…'
            }),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Décrivez votre pratique artistique, votre style, ce que vous proposez à domicile…',
                'rows': 4,
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'ex. Montréal, QC'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://votre-site.com'
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['full_name'].initial = user.full_name
            self.fields['email'].initial = user.email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        validate_image_size(avatar)
        return avatar

    def save_user(self, user, commit=True):
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.username = user.email
        if commit:
            user.save()
