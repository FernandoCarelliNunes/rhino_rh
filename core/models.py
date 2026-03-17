
from django.db import models
from django.contrib.auth.models import User

# 1. Cadastro de Clientes (Empresas que contratam a Rhino)
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empresa_perfil', null=True, blank=True)

    def __str__(self):
        return self.nome

# 2. Cadastro de Vagas
class Vaga(models.Model):
    STATUS_CHOICES = [
        ('abertura', 'Abertura'),
        ('candidatura', 'Candidatura'),
        ('teste', 'Teste'),
        ('ent_recrutador', 'Entrevista Recrutador'),
        ('ent_gestor', 'Entrevista Gestor'),
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    ]

    titulo = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='abertura')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.cliente.nome}"

# 3. Cadastro de Candidatos
class Candidato(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidatos')
    curriculo = models.FileField(upload_to='curriculos/')
    status_candidato = models.CharField(max_length=20, default='Triagem')

    def __str__(self):
        return self.nome