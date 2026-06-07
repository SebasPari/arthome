from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import LoginForm, RegisterForm, ArtistProfileForm
from .models import CustomUser, ArtistProfile


def join_view(request):
    """Combined login + register page."""
    login_form = LoginForm()
    register_form = RegisterForm()
    active_tab = 'login'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            active_tab = 'login'
            login_form = LoginForm(data=request.POST)
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')

        elif action == 'register':
            active_tab = 'register'
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Bienvenue sur ArtHome, {user.full_name} !')
                return redirect('core:dashboard')

    return render(request, 'accounts/join.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_tab': active_tab,
    })


def logout_view(request):
    logout(request)
    return redirect('core:home')


def approve_user_view(request, user_id, token):
    """Lien d'approbation envoyé par email à l'admin."""
    from django.contrib.auth.tokens import default_token_generator
    user = get_object_or_404(CustomUser, pk=user_id, is_active=False)

    if not default_token_generator.check_token(user, token):
        messages.error(request, 'Ce lien est invalide ou a expiré.')
        return redirect('core:home')

    user.is_active = True
    user.save()

    from core.emails import notify_user_approved
    notify_user_approved(user)

    messages.success(request, f'Le compte de {user.full_name} ({user.email}) a été approuvé. Un email de confirmation lui a été envoyé.')
    return redirect('core:home')


def artist_list_view(request):
    """Browse artists with advanced search and filters."""
    from offerings.models import Offering

    profiles = ArtistProfile.objects.select_related('user').filter(user__is_active=True)

    # --- collect filter params ---
    query      = request.GET.get('q', '').strip()
    discipline = request.GET.get('discipline', '').strip()
    category   = request.GET.get('category', '').strip()
    location   = request.GET.get('location', '').strip()
    sort       = request.GET.get('sort', '').strip()

    # --- apply filters ---
    if query:
        profiles = profiles.filter(
            Q(user__full_name__icontains=query) |
            Q(discipline__icontains=query) |
            Q(bio__icontains=query)
        )

    if discipline:
        profiles = profiles.filter(discipline__icontains=discipline)

    if location:
        profiles = profiles.filter(location__icontains=location)

    if category:
        # keep only artists who have at least one offering of this category
        profiles = profiles.filter(
            user__offerings__category=category,
            user__offerings__is_active=True,
        ).distinct()

    # --- sort ---
    if sort == 'name':
        profiles = profiles.order_by('user__full_name')
    elif sort == 'offerings':
        from django.db.models import Count
        profiles = profiles.annotate(
            nb=Count('user__offerings', filter=Q(user__offerings__is_active=True))
        ).order_by('-nb')
    else:
        profiles = profiles.order_by('-created_at')

    # --- filter options ---
    all_disciplines = (
        ArtistProfile.objects.exclude(discipline='')
        .values_list('discipline', flat=True).distinct().order_by('discipline')
    )
    all_locations = (
        ArtistProfile.objects.exclude(location='')
        .values_list('location', flat=True).distinct().order_by('location')
    )
    category_choices = Offering.CATEGORY_CHOICES

    active_filters = any([query, discipline, category, location])

    return render(request, 'accounts/artist_list.html', {
        'profiles': profiles,
        'query': query,
        'discipline': discipline,
        'category': category,
        'location': location,
        'sort': sort,
        'all_disciplines': all_disciplines,
        'all_locations': all_locations,
        'category_choices': category_choices,
        'active_filters': active_filters,
        'total': profiles.count(),
    })


def artist_detail_view(request, pk):
    """Public profile page for a single artist."""
    profile = get_object_or_404(
        ArtistProfile.objects.select_related('user'),
        pk=pk,
        user__is_active=True,
    )
    offerings = profile.user.offerings.filter(is_active=True)
    return render(request, 'accounts/artist_detail.html', {
        'profile': profile,
        'offerings': offerings,
    })


@login_required
def profile_edit_view(request):
    """Artists edit their own profile."""
    if not request.user.is_artist:
        messages.error(request, "Cette page est réservée aux artistes.")
        return redirect('core:home')

    profile, _ = ArtistProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ArtistProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user,
        )
        if form.is_valid():
            form.save_user(request.user)
            form.save()
            messages.success(request, 'Profil mis à jour avec succès !')
            return redirect('accounts:artist_detail', pk=profile.pk)
    else:
        form = ArtistProfileForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
    })
