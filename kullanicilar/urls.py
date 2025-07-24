from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views 

app_name = 'kullanicilar' 

urlpatterns = [
    path('giris/', auth_views.LoginView.as_view(template_name='kullanicilar/giris.html'), name='giris'),
    path('cikis/', auth_views.LogoutView.as_view(template_name='kullanicilar/cikis.html'), name='cikis'), 
    path('kayit/', views.kayit_ol, name='kayit'),
    path('profilim/', views.profilim, name='profilim'),
]