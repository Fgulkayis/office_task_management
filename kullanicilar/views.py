from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
import os
from django.conf import settings
from .forms import GorevAtamaForm, GorevPuanlamaForm, ExcelYuklemeForm
from gorevler.models import Gorev, GorevDurumu
from gorevler.tasks import toplu_gorev_ata_excel

def is_yetkili(user):
    return user.is_authenticated and user.is_staff


def kayit_ol(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hesabınız "{username}" başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
            return redirect('kullanicilar:giris')
    else:
        form = UserCreationForm()
    return render(request, 'kullanicilar/kayit_ol.html', {'form': form})

@login_required
def profilim(request):
    context = {
        'kullanici': request.user,
        'kullanici_gorevleri': Gorev.objects.filter(atanan_calisan=request.user).order_by('-olusturma_tarihi')
    }
    return render(request, 'kullanicilar/profilim.html', context)


@login_required
@user_passes_test(is_yetkili, login_url='/hesaplar/giris/')
def calisan_listesi(request):
    calisanlar = User.objects.filter(is_staff=False).order_by('username')
    context = {
        'calisanlar': calisanlar
    }
    return render(request, 'kullanicilar/calisan_listesi.html', context)

@login_required
@user_passes_test(is_yetkili, login_url='/hesaplar/giris/')
def calisan_detay(request, username):
    calisan = get_object_or_404(User, username=username, is_staff=False)
    atanan_gorevler = Gorev.objects.filter(atanan_calisan=calisan).order_by('-olusturma_tarihi')

    if request.method == 'POST':
        form = GorevAtamaForm(request.POST, request.FILES)
        if form.is_valid():
            gorev = form.save(commit=False)
            gorev.atanan_calisan = calisan
            gorev.atan_yetkili = request.user
            gorev.save()
            messages.success(request, f"'{calisan.username}' kullanıcısına yeni görev başarıyla atandı.")
            return redirect('kullanicilar:calisan_detay', username=username)
    else:
        form = GorevAtamaForm()

    context = {
        'calisan': calisan,
        'atanan_gorevler': atanan_gorevler,
        'form': form
    }
    return render(request, 'kullanicilar/calisan_detay.html', context)

@login_required
@user_passes_test(is_yetkili, login_url='/hesaplar/giris/')
def gorev_puanla(request, pk):
    gorev = get_object_or_404(Gorev, pk=pk)
    if request.method == 'POST':
        form = GorevPuanlamaForm(request.POST, instance=gorev)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{gorev.baslik}' görevi puanlandı.")
            return redirect('kullanicilar:calisan_detay', username=gorev.atanan_calisan.username)
    else:
        form = GorevPuanlamaForm(instance=gorev)

    context = {
        'gorev': gorev,
        'form': form
    }
    return render(request, 'kullanicilar/gorev_puanla.html', context)

@login_required
@user_passes_test(is_yetkili, login_url='/hesaplar/giris/')
def toplu_gorev_atama(request):
    print("toplu_gorev_atama view'i çalıştırıldı.") 
    if request.method == 'POST':
        form = ExcelYuklemeForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_dosyasi']

            upload_dir = os.path.join(settings.MEDIA_ROOT, 'temp_uploads')
            os.makedirs(upload_dir, exist_ok=True)

            file_name = f"toplu_gorev_{timezone.now().strftime('%Y%m%d%H%M%S')}_{excel_file.name}"
            file_path = os.path.join(upload_dir, file_name)

            with open(file_path, 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)

            print(f"Excel dosyası kaydedildi: {file_path}") 
            print(f"Celery görevi tetikleniyor. Kullanıcı ID: {request.user.id}") 

            toplu_gorev_ata_excel.delay(file_path, request.user.id)

            messages.success(request, 'Excel dosyası başarıyla yüklendi. Görevler arka planda atanıyor.')
            return redirect('kullanicilar:calisan_listesi')
        else:
            print("Form geçerli değil:", form.errors) 
            messages.error(request, 'Lütfen geçerli bir Excel dosyası yükleyin. Hataları aşağıda kontrol edin.')
    else:
        form = ExcelYuklemeForm()

    context = {
        'form': form
    }
    return render(request, 'kullanicilar/toplu_gorev_atama.html', context)