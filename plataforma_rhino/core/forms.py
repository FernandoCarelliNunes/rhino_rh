from django import forms
from .models import Candidato
from .models import Vaga


class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome', 'email', 'vaga', 'curriculo']
        
        
class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['titulo', 'cliente', 'descricao', 'status']