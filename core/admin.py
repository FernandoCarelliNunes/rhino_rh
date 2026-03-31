from django.contrib import admin
from .models import Cliente, Vaga, Candidato, HistoricoStatus

admin.site.register(Cliente)
admin.site.register(Vaga)
admin.site.register(Candidato)
admin.site.register(HistoricoStatus)