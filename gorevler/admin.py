from django.contrib import admin
from .models import Gorev, GorevDurumu
from datetime import timedelta, datetime

@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    list_display = (
        'baslik', 'atanan_calisan', 'atan_yetkili', 'durum', 'olusturma_tarihi',
        'baslama_tarihi', 'tamamlanma_tarihi', 'puan', 'get_tamamlanma_suresi',
    )
    list_filter = ('durum', 'atanan_calisan', 'atan_yetkili', 'olusturma_tarihi')
    search_fields = ('baslik', 'aciklama', 'atanan_calisan__username', 'atan_yetkili__username')
    date_hierarchy = 'olusturma_tarihi' 
    fieldsets = (
        (None, {
            'fields': ('baslik', 'aciklama', 'dosya',)
        }),
        ('Atama Bilgileri', {
            'fields':('atan_yetkili', 'atanan_calisan')
        }),
        ('Durum ve Zaman Bilgileri', {
            'fields':('durum', 'baslama_tarihi', 'tamamlanma_tarihi', 'puan', 'son_teslim_tarihi') 
        }),
    )
    readonly_fields = ('olusturma_tarihi', 'get_tamamlanma_suresi')
    

    def get_tamamlanma_suresi(self, obj):

        if obj.baslama_tarihi and obj.tamamlanma_tarihi:
            try:
                start_time = obj.baslama_tarihi
                end_time = obj.tamamlanma_tarihi


                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)

                saniye_farki = (end_time - start_time).total_seconds()

                gun = int(saniye_farki // 86400)
                saat = int((saniye_farki % 86400) // 3600)
                dakika = int((saniye_farki % 3600) // 60)
                saniye = int(saniye_farki % 60)

                sure = ""
                if gun > 0:
                    sure += f"{gun} gün "
                if saat > 0:
                    sure += f"{saat} saat "
                if dakika > 0:
                    sure += f"{dakika} dakika "
                if saniye > 0:
                    sure += f"{saniye} saniye"

                return sure.strip() if sure else "0 saniye"
            except Exception as e:
            
                return f"Hesaplama Hatası: {e}"
        return "Başlamadı / Bitmedi"
    get_tamamlanma_suresi.short_description = 'Tamamlanma Süresi'