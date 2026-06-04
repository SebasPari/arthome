from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'core/home.html')


@login_required
def dashboard_view(request):
    user = request.user

    if user.is_artist:
        from offerings.models import Booking, Offering
        from accounts.models import ArtistProfile

        profile, _ = ArtistProfile.objects.get_or_create(user=user)
        offerings  = Offering.objects.filter(artist=user, is_active=True)
        all_bookings = Booking.objects.filter(
            offering__artist=user
        ).select_related('offering', 'host').order_by('-created_at')

        pending   = all_bookings.filter(status=Booking.STATUS_PENDING)
        confirmed = all_bookings.filter(status=Booking.STATUS_CONFIRMED)

        return render(request, 'core/dashboard_artist.html', {
            'profile':   profile,
            'offerings': offerings,
            'pending':   pending,
            'confirmed': confirmed,
            'total_bookings': all_bookings.count(),
        })

    else:
        from offerings.models import Booking

        bookings = Booking.objects.filter(
            host=user
        ).select_related('offering', 'offering__artist').order_by('-created_at')

        pending   = bookings.filter(status=Booking.STATUS_PENDING)
        confirmed = bookings.filter(status=Booking.STATUS_CONFIRMED)

        return render(request, 'core/dashboard_host.html', {
            'bookings': bookings,
            'pending':  pending,
            'confirmed': confirmed,
        })
