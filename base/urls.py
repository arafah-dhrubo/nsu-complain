from django.urls import path

from base import views

urlpatterns = [
    path('', views.home, name="home"),
    path('send-complain/', views.send_complain, name="send_complain"),
    path('all-complain/', views.all_complains, name='all_complains'),
    path('single-complain/<cid>/', views.single_complain, name='single_complain')
]
