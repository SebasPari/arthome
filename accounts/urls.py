from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('join/', views.join_view, name='join'),
    path('logout/', views.logout_view, name='logout'),
    path('artists/', views.artist_list_view, name='artist_list'),
    path('artists/<int:pk>/', views.artist_detail_view, name='artist_detail'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]
