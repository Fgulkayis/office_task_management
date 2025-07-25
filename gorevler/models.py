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
    son_teslim_tarihi = models.DateField(null=True, blank=True, verbose_name="Son Teslim Tarihi")
    dosya = models.FileField(upload_to='gorev_dosyalari/', null=True, blank=True, verbose_name="Ek Dosya")
    puan = models.IntegerField(default=0, null=True, verbose_name="Görev Puanı", validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
      ordering = ['-olusturma_tarihi']
      verbose_name = 'Görev'
      verbose_name_plural = "Görevler"


    def __str__(self):
       return f"{self.baslik}  ({self.atanan_calisan.username})"

    @property
    def tamamlanma_suresi(self):
        if self.baslama_tarihi and self.tamamlanma_tarihi:
            delta = self.tamamlanma_tarihi - self.baslama_tarihi
            total_seconds = int(delta.total_seconds())

            if total_seconds <= 0:
                return "Hesaplanamadı"

            days = total_seconds // 86400
            total_seconds %= 86400
            hours = total_seconds // 3600
            total_seconds %= 3600
            minutes = total_seconds // 60
            seconds = total_seconds % 60

            parts = []
            if days > 0:
                parts.append(f"{days} gün")
            if hours > 0:
                parts.append(f"{hours} saat")
            if minutes > 0:
                parts.append(f"{minutes} dakika")
            if seconds > 0 and not (days or hours or minutes): # 
                parts.append(f"{seconds} saniye")

            if not parts:
                return "1 dakikadan az" if delta.total_seconds() > 0 else "Henüz tamamlanmadı"

            return ", ".join(parts)
        elif self.baslama_tarihi and not self.tamamlanma_tarihi:
            return "Devam Ediyor"
        return "Henüz Başlatılmadı" 
