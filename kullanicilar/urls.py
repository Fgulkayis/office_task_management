from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views 

app_name = 'kullanicilar' 

urlpatterns = [
    path('giris/', auth_views.LoginView.as_view(template_name='kullanicilar/giris.html'), name='giris'),
    path('cikis/', auth_views.LogoutView.as_view(template_name='kullanicilar/cikis.html'), name='cikis'), 
    path('kayit/', views.kayit_ol, name='kayit'),
    path('profilim/', views.profilim, name='profilim'),
    path('calisanlar/', views.calisan_listesi, name='calisan_listesi'),
    path('calisanlar/<str:username>/', views.calisan_detay, name='calisan_detay'),
    path('gorev/<int:pk>/puanla/', views.gorev_puanla, name='gorev_puanla'),
    path('toplu-gorev-ata/', views.toplu_gorev_atama, name='toplu_gorev_atama'),
]