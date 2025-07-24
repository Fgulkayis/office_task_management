from django.urls import path
from . import views 

app_name = 'gorevler' 

urlpatterns = [
    path('benim-gorevlerim/', views.gorev_listesi, name='gorev_listesi'),
]