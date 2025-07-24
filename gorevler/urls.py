from django.urls import path
from . import views 

app_name = 'gorevler' 

urlpatterns = [
    path('benim-gorevlerim/', views.gorev_listesi, name='gorev_listesi'),
    path('<int:pk>/', views.gorev_detay, name='gorev_detay'),
    path('<int:pk>/durum-guncelle/', views.gorev_durum_guncelle, name='gorev_durum_guncelle'),
    path('<int:pk>/dosya-goruntule/', views.dosya_goruntule, name='dosya_goruntule'), 
]