from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
        'kullanici': request.user
    }
    return render(request, 'kullanicilar/profilim.html', context)
