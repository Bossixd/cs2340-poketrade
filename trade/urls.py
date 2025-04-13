from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    path('', views.trade_list, name='trade_list'),
    path('new/', views.new_trade, name='new_trade'),
    path('detail/<int:trade_id>/', views.trade_detail, name='trade_detail'),
    path('accept/<int:trade_id>/', views.accept_trade, name='accept_trade'),
    path('reject/<int:trade_id>/', views.reject_trade, name='reject_trade'),
    path('cancel/<int:trade_id>/', views.cancel_trade, name='cancel_trade'),
    path('search-user-cards/', views.search_user_cards, name='search_user_cards'),
]