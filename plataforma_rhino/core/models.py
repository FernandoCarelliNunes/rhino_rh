from django.db import models
from django.contrib.auth.models import User

# 1. Cadastro de Clientes (Empresas que contratam a Rhino)
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18, unique=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    # PADRONIZADO: Agora sempre usaremos 'cliente_perfil' nas Views
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cliente_perfil', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.nome

# 2. Cadastro de Vagas
class Vaga(models.Model):
    titulo = models.CharField(max_length=200)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # O status continua existindo no banco, mas com um padrão (default)
    status = models.CharField(max_length=20, default='aberto') 
    descricao_sumaria = models.TextField()
    responsabilidades = models.TextField()
    requisitos_obrigatorios = models.TextField()
    diferenciais = models.TextField(blank=True, null=True)
    # O campo de anexo de currículo geralmente fica no formulário do CANDIDATO, 
    # mas se o Zeca quer anexar um arquivo à VAGA (ex: um descritivo PDF), usamos:
    arquivo_vaga = models.FileField(upload_to='vagas/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    # Campo automático de registro do sistema
    criado_em = models.DateTimeField(auto_now_add=True)
    # Novos campos para o financeiro
    data_abertura = models.DateField(null=True, blank=True, verbose_name="Data de Abertura Real")
    data_fechamento = models.DateField(null=True, blank=True, verbose_name="Data de Encerramento")
    
    

    def __str__(self):
        return self.titulo
    
# 3. Cadastro de Candidatos
class Candidato(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidatos')
    curriculo = models.FileField(upload_to='curriculos/')
    status_candidato = models.CharField(max_length=20, default='Triagem')
    
    sophia_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    link_entrevista = models.URLField(max_length=500, blank=True, null=True)
    score_comportamental = models.FloatField(default=0.0)
    favorito = models.BooleanField(default=False) # A estrelinha da Kika

    def __str__(self):
        return self.nome

# 4. Histórico de Status (Apenas uma versão)
class HistoricoStatus(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='historicos')
    status_anterior = models.CharField(max_length=100)
    status_novo = models.CharField(max_length=100)
    data_mudanca = models.DateTimeField(auto_now_add=True)
    usuario_responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Históricos de Status"

    def __str__(self):
        return f"{self.candidato.nome}: {self.status_anterior} -> {self.status_novo}"  
    
    
class Etapa(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='etapas_vaga')
    nome = models.CharField(max_length=100) # Ex: Entrevista RH, Teste de IA
    ordem = models.PositiveIntegerField(default=0) # Para organizar o funil

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.nome} ({self.vaga.titulo})"