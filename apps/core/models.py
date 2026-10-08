from django.contrib.auth.models import AbstractUser
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.code} - {self.name}'


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CASHIER = 'cashier', 'Cajero'
        MANAGER = 'manager', 'Gerente'

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.CASHIER)
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.SET_NULL)
