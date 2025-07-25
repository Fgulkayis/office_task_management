# gorevler/tasks.py
from celery import shared_task
from django.contrib.auth.models import User
from gorevler.models import Gorev, GorevDurumu
from django.utils import timezone
import openpyxl
import os
import datetime 

@shared_task
def toplu_gorev_ata_excel(file_path, yetkili_user_id):
    print(f"Celery görevi başlatıldı: {file_path}")
    try:
        yetkili_user = User.objects.get(id=yetkili_user_id)
    except User.DoesNotExist:
        print(f"HATA: Yetkili kullanıcı bulunamadı: ID {yetkili_user_id}")
        return False

    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
    except Exception as e:
        print(f"HATA: Excel dosyası okunamadı veya bozuk: {e}")
        return False


    header_skipped = False
    created_count = 0
    failed_count = 0


    COL_USERNAME = 0 
    COL_BASLIK = 1    
    COL_ACIKLAMA = 2  
    COL_SON_TESLIM_TARIHI = 3 

    for row_index, row in enumerate(sheet.iter_rows(min_row=1), start=1):
        if not header_skipped: 
            header_skipped = True
            continue

       
        row_values = [cell.value for cell in row]

        try:
            
            calisan_username = str(row_values[COL_USERNAME]).strip() if row_values[COL_USERNAME] else None
            baslik = str(row_values[COL_BASLIK]).strip() if row_values[COL_BASLIK] else None
            aciklama = str(row_values[COL_ACIKLAMA]).strip() if row_values[COL_ACIKLAMA] else None
            son_teslim_tarihi_excel = row_values[COL_SON_TESLIM_TARIHI] 

            if not (calisan_username and baslik and aciklama):
                print(f"UYARI: Eksik bilgi içeren satır atlandı (Satır {row_index}): Çalışan: '{calisan_username}', Başlık: '{baslik}', Açıklama: '{aciklama}'")
                failed_count += 1
                continue

          
            try:
                atanan_calisan = User.objects.get(username=calisan_username)
            except User.DoesNotExist:
                print(f"UYARI: Çalışan bulunamadı: '{calisan_username}' (Satır {row_index}). Bu görev atlanıyor.")
                failed_count += 1
                continue

           
            son_teslim_tarihi = None
            if son_teslim_tarihi_excel:
                try:
                    if isinstance(son_teslim_tarihi_excel, (datetime.datetime, datetime.date)):
                        son_teslim_tarihi = son_teslim_tarihi_excel.date()
                    elif isinstance(son_teslim_tarihi_excel, (int, float)): 
                        son_teslim_tarihi = openpyxl.utils.datetime.from_excel(son_teslim_tarihi_excel).date()
                    elif isinstance(son_teslim_tarihi_excel, str):
                       
                        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y'):
                            try:
                                son_teslim_tarihi = datetime.datetime.strptime(son_teslim_tarihi_excel, fmt).date()
                                break
                            except ValueError:
                                continue
                        if not son_teslim_tarihi:
                            print(f"UYARI: Geçersiz son teslim tarihi string formatı: '{son_teslim_tarihi_excel}' (Satır {row_index}). Tarih atlandı.")
                    else:
                        print(f"UYARI: Bilinmeyen son teslim tarihi tipi: {type(son_teslim_tarihi_excel)} değeri '{son_teslim_tarihi_excel}' (Satır {row_index}). Tarih atlandı.")
                except Exception as date_e:
                    print(f"UYARI: Son teslim tarihi dönüştürülürken hata oluştu: '{son_teslim_tarihi_excel}' (Satır {row_index}) - Hata: {date_e}. Tarih atlandı.")

          
            Gorev.objects.create(
                baslik=baslik,
                aciklama=aciklama,
                atanan_calisan=atanan_calisan,
                atan_yetkili=yetkili_user,
                son_teslim_tarihi=son_teslim_tarihi,
                durum=GorevDurumu.BASLATILMADI
            )
            created_count += 1
            print(f"Görev oluşturuldu: '{baslik}' -> '{calisan_username}' (Satır {row_index})")

        except IndexError:
            print(f"HATA: Excel satırında beklenen sütun bulunamadı (Satır {row_index}). Satır atlandı. Lütfen Excel formatını kontrol edin.")
            failed_count += 1
            continue
        except Exception as e:
            print(f"KRİTİK HATA: Satır işlenirken beklenmeyen bir hata oluştu (Satır {row_index}): {e}")
            failed_count += 1
            continue


    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Geçici dosya silindi: {file_path}")
        else:
            print(f"Uyarı: Geçici dosya zaten silinmiş veya bulunamadı: {file_path}")
    except Exception as e:
        print(f"HATA: Geçici dosya silinirken hata oluştu: {e}")

    print(f"Celery görevi tamamlandı. Oluşturulan görevler: {created_count}, Başarısız olanlar: {failed_count}")
    return {'status': 'completed', 'created_tasks': created_count, 'failed_tasks': failed_count}