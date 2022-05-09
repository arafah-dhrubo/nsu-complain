from django.contrib.auth.models import User
from django.db import models


class Complain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    mail = models.CharField(max_length=225)
    message = models.TextField()
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username
