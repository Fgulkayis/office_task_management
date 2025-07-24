import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Gorev, GorevDurumu
from django.http import HttpResponse, FileResponse
import os


@login_required 
def gorev_listesi(request):
    gorevler = Gorev.objects.filter(atanan_calisan=request.user).order_by('-olusturma_tarihi')
    context = {
        'gorevler': gorevler
    }
    return render(request, 'gorevler/gorev_listesi.html', context)

@login_required
def gorev_detay(request, pk):
    gorev = get_object_or_404(Gorev, pk=pk, atanan_calisan=request.user)
    context = {
        'gorev': gorev
    }
    return render(request, 'gorevler/gorev_detay.html', context)

@login_required
def gorev_durum_guncelle(request, pk):
    gorev = get_object_or_404(Gorev, pk=pk, atanan_calisan=request.user)

    if request.method == 'POST':
        yeni_durum = request.POST.get('yeni_durum') 
        
        if yeni_durum == GorevDurumu.DEVAM_EDIYOR and gorev.durum == GorevDurumu.BASLATILMADI:
            gorev.durum = GorevDurumu.DEVAM_EDIYOR
            gorev.baslama_tarihi = timezone.now()
            messages.success(request, f'"{gorev.baslik}" görevi başlatıldı!')

        elif yeni_durum == GorevDurumu.TAMAMLANDI and gorev.durum == GorevDurumu.DEVAM_EDIYOR:
            gorev.durum = GorevDurumu.TAMAMLANDI
            gorev.tamamlanma_tarihi = timezone.now() 
            messages.success(request, f'"{gorev.baslik}" görevi başarıyla tamamlandı!')
   
        elif yeni_durum == GorevDurumu.IPTAL_EDILDI and gorev.durum in [GorevDurumu.BASLATILMADI, GorevDurumu.DEVAM_EDIYOR]:
             gorev.durum = GorevDurumu.IPTAL_EDILDI
             messages.warning(request, f'"{gorev.baslik}" görevi iptal edildi.')
        else:
            messages.error(request, 'Geçersiz görev durumu değişikliği veya zaten bu durumda.') 
            return redirect('gorevler:gorev_detay', pk=gorev.pk)

        gorev.save()
        return redirect('gorevler:gorev_detay', pk=gorev.pk)
    
    return redirect('gorevler:gorev_listesi')
@login_required
def dosya_goruntule(request, pk):
    gorev = get_object_or_404(Gorev, pk=pk)


    if request.user != gorev.atanan_calisan and not request.user.is_staff:
        messages.error(request, "Bu dosyayı görüntüleme yetkiniz yok.")
        return redirect('gorevler:gorev_detay', pk=gorev.pk)

    if gorev.dosya:
        file_path = gorev.dosya.path 
        
        if os.path.exists(file_path):
            
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream' 


            response = FileResponse(open(file_path, 'rb'), content_type=mime_type)

            response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
            return response
        else:
            messages.error(request, "Dosya bulunamadı.")
            return redirect('gorevler:gorev_detay', pk=gorev.pk)
    else:
        messages.warning(request, "Bu görevde ekli dosya yok.")
        return redirect('gorevler:gorev_detay', pk=gorev.pk)