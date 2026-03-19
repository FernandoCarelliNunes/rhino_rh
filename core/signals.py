# core/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender='core.Candidato') # Usamos a string 'core.Candidato' para evitar importação precoce
def registrar_historico_status(sender, instance, **kwargs):
    # Importamos os modelos AQUI DENTRO da função
    from .models import Candidato, HistoricoStatus 
    
    if instance.id:
        try:
            antigo_candidato = Candidato.objects.get(id=instance.id)
            if antigo_candidato.status_candidato != instance.status_candidato:
                HistoricoStatus.objects.create(
                    candidato=instance,
                    status_anterior=antigo_candidato.status_candidato,
                    status_novo=instance.status_candidato
                )
        except Candidato.DoesNotExist:
            pass