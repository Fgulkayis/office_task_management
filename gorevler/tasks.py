import openpyxl
from celery import shared_task
from django.contrib.auth.models import User
from gorevler.models import Gorev, GorevDurumu
from datetime import datetime
import os
from django.db import transaction 
from django.contrib.auth import get_user_model 

User = get_user_model() 

@shared_task
def toplu_gorev_ata_excel(file_path, yetkili_user_id):
    print(f"Celery görevi başlatıldı. Dosya yolu: {file_path}, Yetkili ID: {yetkili_user_id}")
    
    try:
        
        try:
            atan_yetkili = User.objects.get(id=yetkili_user_id)
            if not atan_yetkili.is_staff:
                print(f"HATA: ID {yetkili_user_id} olan kullanıcı yetkili değil.")
                return
            print(f"Yetkili kullanıcı bulundu: {atan_yetkili.username}")
        except User.DoesNotExist:
            print(f"HATA: Yetkili kullanıcı bulunamadı: ID {yetkili_user_id}")
            return
        
       
        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            print("Excel dosyası başarıyla yüklendi.")
        except Exception as e:
            print(f"KRİTİK HATA: Excel dosyası okunamadı veya bozuk: {e}")
            return


        header = [cell.value for cell in sheet[1]]
        print(f"Excel başlıkları: {header}")

        COL_USERNAME = 'çalışan kullanıcı adı'
        COL_BASLIK = 'görev başlığı'
        COL_ACIKLAMA = 'açıklama'
        COL_TESLIM_TARIHI = 'son teslim tarihi'

        
        try:
            username_idx = header.index(COL_USERNAME)
            baslik_idx = header.index(COL_BASLIK)
            aciklama_idx = header.index(COL_ACIKLAMA)
            teslim_tarihi_idx = header.index(COL_TESLIM_TARIHI)
            print("Gerekli tüm sütun başlıkları bulundu.")
        except ValueError as e:
            print(f"HATA: Excel dosyasında beklenen sütun başlıkları bulunamadı: {e}. Lütfen sütun adlarını kontrol edin: '{COL_USERNAME}', '{COL_BASLIK}', '{COL_ACIKLAMA}', '{COL_TESLIM_TARIHI}'")
            return
            
        gorevler_olusturuldu_sayisi = 0

 
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2), start=2): 
            row_values = [cell.value for cell in row]
            print(f"İşlenen satır {row_idx}: {row_values}") 

            try:
                username = row_values[username_idx]
                baslik = row_values[baslik_idx]
                aciklama = row_values[aciklama_idx]
                son_teslim_tarihi_str = row_values[teslim_tarihi_idx]
                
                if not username or not baslik or not aciklama:
                    print(f"UYARI: Satır {row_idx} atlandı: Eksik görev bilgisi (Kullanıcı Adı, Başlık veya Açıklama boş).")
                    continue


                try:
                    calisan = User.objects.get(username=username, is_staff=False)
                    print(f"Çalışan bulundu: {calisan.username}")
                except User.DoesNotExist:
                    print(f"UYARI: Satır {row_idx} atlandı: '{username}' adında bir çalışan bulunamadı.")
                    continue

                son_teslim_tarihi = None
                if son_teslim_tarihi_str:
                    try:

                        if isinstance(son_teslim_tarihi_str, datetime):
                            son_teslim_tarihi = son_teslim_tarihi_str.date() 
                        elif isinstance(son_teslim_tarihi_str, (int, float)): 
                            son_teslim_tarihi = datetime.fromtimestamp((son_teslim_tarihi_str - 25569) * 86400).date()
                        else:
                            
                            for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'): 
                                try:
                                    son_teslim_tarihi = datetime.strptime(str(son_teslim_tarihi_str), fmt).date()
                                    break
                                except ValueError:
                                    pass
                            if son_teslim_tarihi is None:
                                print(f"UYARI: Satır {row_idx} için geçersiz son teslim tarihi formatı: '{son_teslim_tarihi_str}'. Bu görev için son teslim tarihi ayarlanmadı.")

                    except Exception as date_err:
                        print(f"UYARI: Satır {row_idx} için son teslim tarihi dönüştürme hatası: {date_err}. Değer: '{son_teslim_tarihi_str}'")
                        son_teslim_tarihi = None 


                with transaction.atomic(): 
                    Gorev.objects.create(
                        atanan_calisan=calisan,
                        atan_yetkili=atan_yetkili,
                        baslik=baslik,
                        aciklama=aciklama,
                        durum=GorevDurumu.BASLATILMADI,
                        son_teslim_tarihi=son_teslim_tarihi
                    )
                    gorevler_olusturuldu_sayisi += 1
                    print(f"Başarılı: '{baslik}' görevi '{username}' için oluşturuldu.")

            except Exception as e:
                print(f"KRİTİK HATA: Satır {row_idx} işlenirken beklenmeyen bir hata oluştu: {e}")


        print(f"Celery görevi tamamlandı. Toplam {gorevler_olusturuldu_sayisi} görev oluşturuldu.")

    except Exception as overall_e:
        print(f"GENEL HATA: Toplu görev atama sırasında genel bir hata oluştu: {overall_e}")


    finally:

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Geçici dosya silindi: {file_path}")
            except Exception as e:
                print(f"UYARI: Geçici dosya silinirken hata oluştu: {e}")