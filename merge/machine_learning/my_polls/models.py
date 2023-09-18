from django.db import models

# Create your models here.
class DescricaoCha(models.Model):
    id_descricao = models.AutoField(primary_key=True)
    conhecimentos = models.TextField(max_length=255)
    habilidades = models.TextField(max_length=255)
    atitudes = models.TextField(max_length=255)
    cargo = models.TextField(max_length=255)
    nivel = models.TextField(max_length=255)

    def __str__(self):
        return self.cargo
    