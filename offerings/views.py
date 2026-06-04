from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Offering, Booking
from .forms import OfferingForm, BookingForm, ArtistNoteForm


# ──────────────────────────────────────────────
# OFFERING CRUD
# ──────────────────────────────────────────────

@login_required
def offering_create_view(request):
    if not request.user.is_artist:
        messages.error(request, "Cette page est réservée aux artistes.")
        return redirect('core:home')

    if request.method == 'POST':
        form = OfferingForm(request.POST, request.FILES)
        if form.is_valid():
            offering = form.save(commit=False)
            offering.artist = request.user
            offering.save()
            messages.success(request, f'« {offering.title} » a été créée avec succès !')
            return redirect('accounts:artist_detail', pk=request.user.artist_profile.pk)
    else:
        form = OfferingForm()

    return render(request, 'offerings/offering_form.html', {
        'form': form, 'action': 'create',
    })


@login_required
def offering_edit_view(request, pk):
    offering = get_object_or_404(Offering, pk=pk)
    if offering.artist != request.user:
        messages.error(request, "Vous ne pouvez modifier que vos propres prestations.")
        return redirect('core:home')

    if request.method == 'POST':
        form = OfferingForm(request.POST, request.FILES, instance=offering)
        if form.is_valid():
            form.save()
            messages.success(request, f'« {offering.title} » a été mise à jour.')
            return redirect('accounts:artist_detail', pk=request.user.artist_profile.pk)
    else:
        form = OfferingForm(instance=offering)

    return render(request, 'offerings/offering_form.html', {
        'form': form, 'action': 'edit', 'offering': offering,
    })


@login_required
def offering_delete_view(request, pk):
    offering = get_object_or_404(Offering, pk=pk)
    if offering.artist != request.user:
        messages.error(request, "Vous ne pouvez supprimer que vos propres prestations.")
        return redirect('core:home')

    if request.method == 'POST':
        title = offering.title
        offering.delete()
        messages.success(request, f'« {title} » a été supprimée.')
        return redirect('accounts:artist_detail', pk=request.user.artist_profile.pk)

    return render(request, 'offerings/offering_confirm_delete.html', {'offering': offering})


# ──────────────────────────────────────────────
# BOOKINGS — HOST SIDE
# ──────────────────────────────────────────────

@login_required
def booking_create_view(request, artist_pk):
    """Host sends a booking request to an artist."""
    from accounts.models import ArtistProfile
    artist_profile = get_object_or_404(ArtistProfile, pk=artist_pk)
    artist = artist_profile.user

    if request.user == artist:
        messages.error(request, "Vous ne pouvez pas vous réserver vous-même.")
        return redirect('accounts:artist_detail', pk=artist_pk)

    if request.user.is_artist:
        messages.error(request, "Les artistes ne peuvent pas envoyer de demandes.")
        return redirect('accounts:artist_detail', pk=artist_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST, artist=artist)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.host = request.user
            booking.save()
            # Email à l'artiste
            from core.emails import notify_artist_new_booking
            notify_artist_new_booking(booking)
            messages.success(
                request,
                f'Votre demande pour « {booking.offering.title} » a été envoyée à {artist.full_name} !'
            )
            return redirect('offerings:host_bookings')
    else:
        form = BookingForm(artist=artist)

    return render(request, 'offerings/booking_form.html', {
        'form': form,
        'artist_profile': artist_profile,
    })


@login_required
def host_bookings_view(request):
    """Host sees all their sent booking requests."""
    if request.user.is_artist:
        return redirect('offerings:artist_bookings')

    bookings = Booking.objects.filter(host=request.user).select_related(
        'offering', 'offering__artist'
    )
    return render(request, 'offerings/host_bookings.html', {'bookings': bookings})


@login_required
def booking_cancel_view(request, pk):
    """Host cancels one of their pending requests."""
    booking = get_object_or_404(Booking, pk=pk, host=request.user)
    if booking.status == Booking.STATUS_PENDING:
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        messages.success(request, "Demande annulée.")
    return redirect('offerings:host_bookings')


# ──────────────────────────────────────────────
# BOOKINGS — ARTIST SIDE
# ──────────────────────────────────────────────

@login_required
def artist_bookings_view(request):
    """Artist sees all incoming booking requests."""
    if not request.user.is_artist:
        return redirect('offerings:host_bookings')

    bookings = Booking.objects.filter(
        offering__artist=request.user
    ).select_related('offering', 'host')

    pending   = bookings.filter(status=Booking.STATUS_PENDING)
    confirmed = bookings.filter(status=Booking.STATUS_CONFIRMED)
    past      = bookings.filter(status__in=[Booking.STATUS_DECLINED, Booking.STATUS_CANCELLED])

    return render(request, 'offerings/artist_bookings.html', {
        'pending': pending,
        'confirmed': confirmed,
        'past': past,
    })


@login_required
def booking_respond_view(request, pk):
    """Artist confirms or declines a booking, with optional note."""
    booking = get_object_or_404(Booking, pk=pk, offering__artist=request.user)

    if booking.status != Booking.STATUS_PENDING:
        messages.error(request, "Cette demande a déjà été traitée.")
        return redirect('offerings:artist_bookings')

    if request.method == 'POST':
        action = request.POST.get('action')
        note_form = ArtistNoteForm(request.POST, instance=booking)
        if note_form.is_valid():
            booking = note_form.save(commit=False)
            from core.emails import notify_host_booking_confirmed, notify_host_booking_declined
            if action == 'confirm':
                booking.status = Booking.STATUS_CONFIRMED
                booking.save()
                notify_host_booking_confirmed(booking)
                messages.success(request, f"Demande de {booking.host.full_name} confirmée !")
            elif action == 'decline':
                booking.status = Booking.STATUS_DECLINED
                booking.save()
                notify_host_booking_declined(booking)
                messages.info(request, f"Demande de {booking.host.full_name} refusée.")
        return redirect('offerings:artist_bookings')

    note_form = ArtistNoteForm(instance=booking)
    return render(request, 'offerings/booking_respond.html', {
        'booking': booking,
        'note_form': note_form,
    })
