"""
Fonctions d'envoi d'emails pour ArtHome.
En développement (EMAIL_BACKEND=console), les emails s'affichent dans le terminal.
"""
from django.core.mail import send_mail
from django.conf import settings


def _send(subject, body, to_email):
    """Wrapper bas niveau — catch les erreurs pour ne pas bloquer l'UX."""
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
    except Exception as e:
        # En prod, logger l'erreur plutôt que de crasher
        print(f"[ArtHome email error] {e}")


def notify_artist_new_booking(booking):
    """L'hôte vient d'envoyer une demande → on notifie l'artiste."""
    artist = booking.offering.artist
    host   = booking.host
    subject = f"✦ Nouvelle demande de {host.full_name} — ArtHome"
    body = f"""Bonjour {artist.full_name},

{host.full_name} souhaite vous inviter pour une prestation !

Prestation demandée : {booking.offering.title}
{"Date souhaitée : " + booking.date_wish.strftime("%d/%m/%Y") if booking.date_wish else ""}
Participants : {booking.guests}
{"Adresse : " + booking.address if booking.address else ""}

Message de {host.full_name} :
«  {booking.message}  »

Connectez-vous à votre tableau de bord pour confirmer ou refuser cette demande :
http://127.0.0.1:8000/dashboard/

—
ArtHome
"""
    _send(subject, body, artist.email)


def notify_host_booking_confirmed(booking):
    """L'artiste a confirmé → on notifie l'hôte."""
    host   = booking.host
    artist = booking.offering.artist
    subject = f"✓ Votre demande a été confirmée par {artist.full_name} — ArtHome"
    body = f"""Bonjour {host.full_name},

Bonne nouvelle ! {artist.full_name} a confirmé votre demande.

Prestation : {booking.offering.title}
{"Date : " + booking.date_wish.strftime("%d/%m/%Y") if booking.date_wish else ""}
Participants : {booking.guests}
{"Adresse : " + booking.address if booking.address else ""}

{('Message de ' + artist.full_name + ' : \n« ' + booking.artist_note + ' »') if booking.artist_note else ""}

Retrouvez tous les détails dans votre tableau de bord :
http://127.0.0.1:8000/dashboard/

—
ArtHome
"""
    _send(subject, body, host.email)


def notify_host_booking_declined(booking):
    """L'artiste a refusé → on notifie l'hôte."""
    host   = booking.host
    artist = booking.offering.artist
    subject = f"Votre demande pour « {booking.offering.title} » — ArtHome"
    body = f"""Bonjour {host.full_name},

{artist.full_name} n'est malheureusement pas disponible pour votre demande.

{('Son message : « ' + booking.artist_note + ' »') if booking.artist_note else ""}

Vous pouvez explorer d'autres artistes sur ArtHome :
http://127.0.0.1:8000/accounts/artists/

—
ArtHome
"""
    _send(subject, body, host.email)
