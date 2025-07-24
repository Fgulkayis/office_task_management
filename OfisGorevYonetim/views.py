from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='/hesaplar/giris/')
def anasayfa(request):
    context = {
        'kullanici_adi': request.user.username
    }
    return render(request, 'anasayfa.html', context)