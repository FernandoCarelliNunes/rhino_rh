from django import forms
from .models import Candidato
from .models import Vaga
from django.contrib.auth.models import User
from .models import EmpresaPerfil


class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome', 'email', 'vaga', 'curriculo']
        
        
class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['titulo', 'cliente', 'descricao', 'status']
        

class CadastroClienteForm(forms.ModelForm):
    # Campos extras para o Usuário
    username = forms.CharField(label="Nome de Usuário (Login)", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail de Contato", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = EmpresaPerfil
        fields = ['nome', 'cnpj'] # Campos da empresa
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
        }