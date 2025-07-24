from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Gorev 

@login_required 
def gorev_listesi(request):
    gorevler = Gorev.objects.filter(atanan_calisan=request.user).order_by('-olusturma_tarihi')
    context = {
        'gorevler': gorevler
    }
    return render(request, 'gorevler/gorev_listesi.html', context)
