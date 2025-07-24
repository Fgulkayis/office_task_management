from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import MinValueValidator, MaxValueValidator

class GorevDurumu(models.TextChoices):
    BASLATILMADI = 'BSL', 'Başlatılmadı'
    DEVAM_EDIYOR = 'DVM', 'Devam Ediyor'
    TAMAMLANDI = 'TMM', 'Tamamlandı'
    IPTAL_EDILDI = 'IPT', 'İptal Edildi'

class Gorev(models.Model):
    baslik = models.CharField(max_length=200, verbose_name="Görev Başlığı")
    aciklama = models.TextField(verbose_name="Görev Açıklaması")
    atan_yetkili=models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='atanan_gorevler', verbose_name='Atayan Yetkili')
    atanan_calisan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gorevlerim', verbose_name='Atanan Çalışan')
    durum = models.CharField(max_length=3, choices=GorevDurumu.choices, default=GorevDurumu.BASLATILMADI, verbose_name='Görev Durumu')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    baslama_tarihi = models.DateTimeField(null=True, blank=True, verbose_name='Başlama Tarihi')
    tamamlanma_tarihi = models.DateTimeField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    dosya = models.FileField(upload_to='gorev_dosyalari/', null=True, blank=True, verbose_name="Ek Dosya")
    puan = models.IntegerField(default=0, null=True, verbose_name="Görev Puanı", validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
      ordering = ['-olusturma_tarihi']
      verbose_name = 'Görev'
      verbose_name_plural = "Görevler"


    def __str__(self):
       return f"{self.baslik} - {self.atanan_calisan.username} ({self.get_durum_display()})"

    @property
    def tamamlanma_suresi(self):
      if self.baslama_tarihi and self.tamamlanma_tarihi:
         return self.tamamlanma_tarihi - self.baslama_tarihi
      return None
