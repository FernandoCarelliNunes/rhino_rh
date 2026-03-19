from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vaga, Cliente, Candidato  # <--- CERTIFIQUE-SE DE QUE 'Candidato' ESTÁ AQUI
from .forms import CandidatoForm
from django.contrib.auth.models import User

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

@login_required
def dashboard(request):
    # Se for Admin ou Recrutador da Rhino, vê todas as vagas de todos os clientes
    if request.user.is_superuser or request.user.tipo_acesso == 'RECRUTADOR':
        vagas = Vaga.objects.all()
    else:
        # Se for Cliente, filtramos para ver apenas as vagas vinculadas à empresa dele
        vagas = Vaga.objects.filter(cliente=request.user.empresa_perfil)
    
    return render(request, 'core/dashboard.html', {'vagas': vagas})

from django.db.models import Count

@login_required
def detalhes_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    
    # Segurança: Cliente só acessa se a vaga for dele
    if not request.user.is_superuser and not request.user.groups.filter(name='Recrutadores').exists():
        if vaga.cliente != request.user.empresa_perfil:
            return redirect('dashboard')

    candidatos = vaga.candidatos.all().prefetch_related('historicos')
    
    # Calculando os totais de cada fase de forma simples e direta
    contagem = {
        'triagem': candidatos.filter(status_candidato='Triagem').count(),
        'teste': candidatos.filter(status_candidato='Teste').count(),
        'entrevistas': candidatos.filter(status_candidato__icontains='Entrevista').count(),
        'aprovados': candidatos.filter(status_candidato='Aprovado').count(),
        'reprovados': candidatos.filter(status_candidato='Reprovado').count(),
    }

    context = {
        'vaga': vaga,
        'candidatos': candidatos,
        'total_inscritos': candidatos.count(),
        'contagem': contagem,
    }
    return render(request, 'core/detalhes_vaga.html', context)

# No seu core/views.py, onde exibe os detalhes ou na própria mudança de status
def detalhes_candidato(request, candidato_id):
    candidato = get_object_or_404(Candidato, id=candidato_id)
    # Procuramos todos os históricos deste candidato, do mais novo para o mais antigo
    historicos = candidato.historicos.all().order_by('-data_mudanca') 
    
    return render(request, 'core/detalhes_candidato.html', {
        'candidato': candidato,
        'historicos': historicos
    })
    
from django.db.models import Count

# Verifique se não há nada "solto" acima destas linhas
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Verifica se é Admin ou Recrutador
    if request.user.is_superuser or getattr(request.user, 'tipo_acesso', None) == 'RECRUTADOR':
        vagas = Vaga.objects.all()
        status_data = Candidato.objects.values('status_candidato').annotate(total=Count('id'))
    else:
        # Pega o perfil vinculado (ajuste o nome se for empresa_perfil ou cliente_perfil)
        perfil = getattr(request.user, 'cliente_perfil', None)
        vagas = Vaga.objects.filter(cliente=perfil)
        status_data = Candidato.objects.filter(vaga__cliente=perfil).values('status_candidato').annotate(total=Count('id'))

    context = {
        'vagas': vagas,
        'status_labels': [item['status_candidato'] for item in status_data] or [],
        'status_totals': [item['total'] for item in status_data] or [],
    }
    return render(request, 'core/dashboard.html', context)

from django.db.models import Avg, F, ExpressionWrapper, fields
from datetime import timedelta

@login_required
def relatorio_geral(request):
    # Filtro de segurança por cliente
    if request.user.is_superuser:
        vagas = Vaga.objects.all()
    else:
        vagas = Vaga.objects.filter(cliente=request.user.empresa_perfil)

    # 1. Total de vagas por status
    vagas_status = vagas.values('status').annotate(total=Count('id'))

    # 2. Total de candidatos no funil geral
    funil_geral = Candidato.objects.filter(vaga__in=vagas).values('status_candidato').annotate(total=Count('id'))

    # 3. Tempo médio de fechamento (SLA)
    # Calculamos a diferença entre a data de criação e a data do último histórico para vagas 'Aprovado'
    vagas_fechadas = vagas.filter(status='aprovado').annotate(
        tempo_fechamento=ExpressionWrapper(
            F('updated_at') - F('criado_em'), # Você precisará ter esses campos no model Vaga
            output_field=fields.DurationField()
        )
    )
    
    media_dias = vagas_fechadas.aggregate(media=Avg('tempo_fechamento'))['media']
    if media_dias:
        media_dias = media_dias.days
    else:
        media_dias = "Em cálculo..."

    context = {
        'vagas_status': vagas_status,
        'funil_geral': funil_geral,
        'media_dias': media_dias,
        'total_vagas': vagas.count(),
        'total_candidatos': Candidato.objects.filter(vaga__in=vagas).count()
    }
    return render(request, 'core/relatorio_geral.html', context)

from django.contrib.auth.decorators import user_passes_test
from .forms import CadastroClienteForm

@user_passes_test(lambda u: u.is_superuser) # Só admins acessam
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            # 1. Cria o Usuário do Django
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # 2. Cria o Perfil da Empresa vinculado ao Usuário
            empresa = form.save(commit=False)
            empresa.usuario = user
            empresa.save()
            
            return redirect('dashboard')
    else:
        form = CadastroClienteForm()
    
    return render(request, 'core/cadastrar_cliente.html', {'form': form})
