from django.db import models


class Candidato(models.Model):
    cand_id = models.BigAutoField(primary_key=True)
    cand_experiencia = models.TextField()
    cand_contato = models.CharField(max_length=50)
    cand_nome = models.CharField(max_length=50)
    cand_pontos_cha = models.IntegerField(blank=True, null=True)
    cand_cargo = models.CharField(max_length=50)
    cand_nivel = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'candidato'


class DescCargo(models.Model):
    desc_id = models.BigAutoField(primary_key=True)
    desc_vaga = models.CharField(max_length=50)
    desc_nivel = models.CharField(max_length=50)
    desc_conhecimentos = models.TextField(blank=True, null=True)
    desc_habilidades = models.TextField(blank=True, null=True)
    desc_atitudes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'desc_cargo'


class DescCargoCandidato(models.Model):
    desc = models.OneToOneField(DescCargo, models.DO_NOTHING, primary_key=True)  # The composite primary key (desc_id, cand_id) found, that is not supported. The first column is selected.
    cand = models.ForeignKey(Candidato, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'desc_cargo_candidato'
        unique_together = (('desc', 'cand'),)


class DescCargoEdit(models.Model):
    desc_edit_id = models.BigAutoField(primary_key=True)
    desc_edit_vaga = models.CharField(max_length=50)
    desc_edit_nivel = models.CharField(max_length=20)
    desc_edit_conhecimentos = models.TextField(blank=True, null=True)
    desc_edit_habilidades = models.TextField(blank=True, null=True)
    desc_edit_atitudes = models.TextField(blank=True, null=True)
    emp = models.ForeignKey('Empresa', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'desc_cargo_edit'


class Empresa(models.Model):
    emp_id = models.BigAutoField(primary_key=True)
    emp_nome = models.CharField(max_length=50)
    emp_cnpj = models.CharField(unique=True, max_length=18)
    emp_descricao = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresa'