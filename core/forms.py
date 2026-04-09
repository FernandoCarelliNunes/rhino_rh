from django import forms
from .models import Cliente, Vaga, Candidato

from django.contrib.auth.models import User
#from .models import EmpresaPerfil


class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome', 'email', 'vaga', 'curriculo']
        
        

class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = [
            'titulo', 
            'cliente', 
            'data_abertura',  # <--- Adicione aqui
            'descricao_sumaria', 
            'responsabilidades', 
            'requisitos_obrigatorios', 
            'diferenciais', 
            'arquivo_vaga'
        ]
        
        labels = {
            'data_abertura': 'Data de Abertura',}
            
        widgets = {
            # Isso faz aparecer o calendário no campo de data
            'data_abertura': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao_sumaria': forms.Textarea(attrs={'rows': 3}),
            'responsabilidades': forms.Textarea(attrs={'rows': 4}),
            'requisitos_obrigatorios': forms.Textarea(attrs={'rows': 4}),
            'diferenciais': forms.Textarea(attrs={'rows': 3}),
        }        

class CadastroClienteForm(forms.ModelForm):
    # Campos extras para o Usuário
    username = forms.CharField(label="Nome de Usuário (Login)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail de Contato", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Cliente # Mudei aqui de EmpresaPerfil para Cliente
        fields = ['nome', 'cnpj', 'logo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
        }
        
class InscricaoVagaForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome', 'email', 'curriculo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
            'curriculo': forms.FileInput(attrs={'class': 'form-control'}),
        }