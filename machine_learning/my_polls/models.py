from django.db import models

class Candidato(models.Model):
    cand_id = models.BigAutoField(primary_key=True)
    cand_exp = models.TextField()
    cand_link = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'candidato'


class CandidatoVaga(models.Model):
    vaga = models.OneToOneField('Vaga', models.DO_NOTHING, primary_key=True)  # The composite primary key (vaga_id, cand_id) found, that is not supported. The first column is selected.
    cand = models.ForeignKey(Candidato, models.DO_NOTHING)
    cand_vaga_rank = models.IntegerField()
    cand_vaga_pontos_cha = models.IntegerField()
    cand_percent_match = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'candidato_vaga'
        unique_together = (('vaga', 'cand'),)


class Empresa(models.Model):
    emp_id = models.BigAutoField(primary_key=True)
    emp_nome = models.CharField(max_length=50)
    emp_cnpj = models.CharField(unique=True, max_length=18)
    emp_descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresa'


class EmpresaVaga(models.Model):
    vaga = models.ForeignKey('Vaga', models.DO_NOTHING)
    emp = models.OneToOneField(Empresa, models.DO_NOTHING, primary_key=True)  # The composite primary key (emp_id, vaga_id) found, that is not supported. The first column is selected.

    class Meta:
        managed = False
        db_table = 'empresa_vaga'
        unique_together = (('emp', 'vaga'),)


class Vaga(models.Model):
    vaga_id = models.BigAutoField(primary_key=True)
    vaga_nome = models.CharField(max_length=50)
    vaga_nivel = models.CharField(max_length=50)
    vaga_conhecimentos = models.TextField(blank=True, null=True)
    vaga_habilidades = models.TextField(blank=True, null=True)
    vaga_atitudes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vaga'