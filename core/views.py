from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vaga, Cliente, Candidato  # <--- CERTIFIQUE-SE DE QUE 'Candidato' ESTÁ AQUI
from .forms import CandidatoForm

@login_required
def dashboard(request):
    # Se o usuário for um Cliente, filtramos as vagas
    if hasattr(request.user, 'empresa_perfil'):
        vagas = Vaga.objects.filter(cliente=request.user.empresa_perfil)
    else:
        # Se for Admin ou Recrutador da Rhino, vê tudo
        vagas = Vaga.objects.all()
        
    return render(request, 'core/dashboard.html', {'vagas': vagas})

from django.shortcuts import render, redirect
from .forms import CandidatoForm

@login_required
def cadastrar_candidato(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = CandidatoForm()
    return render(request, 'core/cadastrar_candidato.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
def detalhes_vaga(request, vaga_id):
    # Garante que o cliente só veja a vaga se for dele, ou o recrutador veja tudo
    if hasattr(request.user, 'empresa_perfil'):
        vaga = get_object_or_404(Vaga, id=vaga_id, cliente=request.user.empresa_perfil)
    else:
        vaga = get_object_or_404(Vaga, id=vaga_id)
        
    candidatos = vaga.candidatos.all()
    return render(request, 'core/detalhes_vaga.html', {'vaga': vaga, 'candidatos': candidatos})

@login_required
def mudar_status_candidato(request, candidato_id, novo_status):
    candidato = get_object_or_404(Candidato, id=candidato_id)
    candidato.status_candidato = novo_status
    candidato.save()
    return redirect('detalhes_vaga', vaga_id=candidato.vaga.id)

from .forms import VagaForm

@login_required
def cadastrar_vaga(request):
    if request.method == 'POST':
        form = VagaForm(request.POST)
        if form.is_valid():
            vaga = form.save(commit=False)
            # Se for um cliente logado, forçamos a vaga a ser dele
            if hasattr(request.user, 'empresa_perfil'):
                vaga.cliente = request.user.empresa_perfil
            vaga.save()
            return redirect('dashboard')
    else:
        form = VagaForm()
    return render(request, 'core/cadastrar_vaga.html', {'form': form})

@login_required
def mudar_status_vaga(request, vaga_id, novo_status):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    vaga.status = novo_status
    vaga.save()
    return redirect('dashboard')

from django.db.models import Count

@login_required
def relatorios(request):
    # Filtragem por segurança (Cliente só vê seus dados)
    if hasattr(request.user, 'empresa_perfil'):
        vagas_base = Vaga.objects.filter(cliente=request.user.empresa_perfil)
        candidatos_base = Candidato.objects.filter(vaga__cliente=request.user.empresa_perfil)
    else:
        vagas_base = Vaga.objects.all()
        candidatos_base = Candidato.objects.all()

    # Indicador 1: Candidatos por Etapa (Funil)
    status_candidatos = candidatos_base.values('status_candidato').annotate(total=Count('id'))

    # Indicador 2: Vagas por Cliente
    vagas_por_cliente = vagas_base.values('cliente__nome').annotate(total=Count('id'))

    # Indicador 3: Totais Gerais
    total_vagas = vagas_base.count()
    total_candidatos = candidatos_base.count()

    context = {
        'status_candidatos': status_candidatos,
        'vagas_por_cliente': vagas_por_cliente,
        'total_vagas': total_vagas,
        'total_candidatos': total_candidatos,
    }
    return render(request, 'core/relatorios.html', context)