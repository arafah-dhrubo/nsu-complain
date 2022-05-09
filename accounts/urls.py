from django.urls import path

from accounts import views

urlpatterns = [
    path('login/', views.login_account, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout_account, name="logout"),
    path('settings/', views.settings, name="settings"),
    path('resend-email', views.verify_account, name="resend_email"),
    path('settings/password/', views.password, name="password"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
