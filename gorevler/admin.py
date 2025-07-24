from django.contrib import admin
from .models import Gorev, GorevDurumu

@admin.register(Gorev)
class GorevAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'atanan_calisan', 'atan_yetkili', 'durum', 'olusturma_tarihi', 'baslama_tarihi', 'tamamlanma_tarihi',
    'puan', 'get_tamamlanma_suresi',)
    list_filter = ('durum', 'atanan_calisan', 'atan_yetkili', 'olusturma_tarihi')
    search_fields = ('baslik', 'aciklama', 'atanan_calisan__username', 'atan_yetkili__username')
    fieldsets = (
        (None, {
            'fields': ('baslik', 'aciklama', 'dosya',)
        }),
        ('Atama Bilgileri', {
            'fields':('atan_yetkili', 'atanan_calisan')
        }),
        ('Durum ve Zaman Bilgileri', {
            'fields':('durum', 'baslama_tarihi', 'tamamlanma_tarihi', 'puan')
        }),
        
     )
    readonly_fields = ('olusturma_tarihi', 'get_tamamlanma_suresi')
    

    def get_tamamlanma_suresi(self, obj):
        if obj.tamamlanma_suresi:
            total_seconds = int(obj.tamamlanma_suresi.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours}s {minutes}dk {seconds}sn"
        return "N/A"
    get_tamamlanma_suresi.short_description = "Tamamlanma Süresi"