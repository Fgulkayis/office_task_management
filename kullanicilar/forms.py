from django import forms
from gorevler.models import Gorev
from django.core.validators import MinValueValidator, MaxValueValidator 


class GorevAtamaForm(forms.ModelForm):
    class Meta:
        model = Gorev
        fields = ['baslik', 'aciklama', 'son_teslim_tarihi', 'dosya']
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
            'son_teslim_tarihi': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'baslik': 'Görev Başlığı',
            'aciklama': 'Görev Açıklaması',
            'son_teslim_tarihi': 'Son Teslim Tarihi',
            'dosya': 'Ek Dosya',
        }

class GorevPuanlamaForm(forms.ModelForm):
    class Meta:
        model = Gorev
        fields = ['puan']
        widgets = {
            'puan': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }
        labels = {
            'puan': 'Puan (1-5)',
        }

class ExcelYuklemeForm(forms.Form):
    excel_dosyasi = forms.FileField(
        label='Görev Excel Dosyası',
        help_text='Çalışan kullanıcı adı, görev başlığı, açıklama ve son teslim tarihi sütunlarını içeren bir Excel (.xlsx) dosyası yükleyin.'
    )