from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('my-listings/', views.my_listings, name='my_listings'),
    path('list-card/', views.list_card, name='list_card'),
    path('cancel-listing/<int:listing_id>/', views.cancel_listing, name='cancel_listing'),
    path('buy-card/<int:listing_id>/', views.buy_card, name='buy_card'),
    path('roll/', views.roll, name='roll'),
    path('set_desired/', views.set_desired, name='set_desired'),
]
