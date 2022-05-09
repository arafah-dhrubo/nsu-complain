from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    is_verified = models.BooleanField(default=False)
    photo = models.FileField(upload_to='uploads/', verbose_name='ID Card')

    def __str__(self):
        return self.user.username
