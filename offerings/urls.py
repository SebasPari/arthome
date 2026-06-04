from django.urls import path
from . import views

app_name = 'offerings'

urlpatterns = [
    # Offering CRUD
    path('nouvelle/', views.offering_create_view, name='create'),
    path('<int:pk>/modifier/', views.offering_edit_view, name='edit'),
    path('<int:pk>/supprimer/', views.offering_delete_view, name='delete'),

    # Bookings — host
    path('reserver/<int:artist_pk>/', views.booking_create_view, name='booking_create'),
    path('mes-demandes/', views.host_bookings_view, name='host_bookings'),
    path('mes-demandes/<int:pk>/annuler/', views.booking_cancel_view, name='booking_cancel'),

    # Bookings — artist
    path('demandes-recues/', views.artist_bookings_view, name='artist_bookings'),
    path('demandes-recues/<int:pk>/repondre/', views.booking_respond_view, name='booking_respond'),
]
