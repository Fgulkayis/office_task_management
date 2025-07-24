from django.db import models
from django.contrib.auth.models import User

class YetkiliProfil(models.Model):
    user= models.OneToOneField(User, on_delete= models.CASCADE, related_name='yetkili_profili')

    def __str__(self):
        return f"Yetkili: {self.user.username}"
    

class CalisanProfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calisan_profil')
    puan = models.IntegerField(default=0)

    def __str__(self):
        return f"Çalışan: {self.user.username} (Puan: {self.puan})"
    
def is_yetkili(user):
    return hasattr(user, 'yetkili_profil')

def is_calisan(user):
    return hasattr(user, 'calisan_profil')


