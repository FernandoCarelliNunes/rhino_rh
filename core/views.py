from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from .models import Vaga, Candidato, Cliente, HistoricoStatus
from .forms import VagaForm, CandidatoForm, CadastroClienteForm
from django.shortcuts import render, get_object_or_404, redirect




# Adicione ao topo: from django.views.decorators.clickjacking import xframe_options_exempt

def inscrever_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    
    if request.method == 'POST':
        form = InscricaoVagaForm(request.POST, request.FILES)
        if form.is_valid():
            candidato = form.save(commit=False)
            candidato.vaga = vaga
            candidato.status_candidato = 'Triagem'
            candidato.save()
            # Criamos o histórico inicial
            HistoricoStatus.objects.create(
                candidato=candidato,
                status_anterior='Novo',
                status_novo='Triagem'
            )
            return render(request, 'core/inscricao_sucesso.html', {'vaga': vaga})
    else:
        form = InscricaoVagaForm()
    
    return render(request, 'core/inscrever_vaga.html', {'form': form, 'vaga': vaga})

# --- 1. DASHBOARD ---
@login_required
def dashboard(request):
    if request.user.is_superuser:
        vagas = Vaga.objects.all().order_by('-criado_em')
        status_data = Candidato.objects.values('status_candidato').annotate(total=Count('id'))
    else:
        perfil = getattr(request.user, 'cliente_perfil', None)
        if perfil:
            vagas = Vaga.objects.filter(cliente=perfil).order_by('-criado_em')
            status_data = Candidato.objects.filter(vaga__cliente=perfil).values('status_candidato').annotate(total=Count('id'))
        else:
            vagas = Vaga.objects.none()
            status_data = []

    context = {
        'vagas': vagas,
        'vagas_ativas_count': vagas.count(),
        'status_labels': [item['status_candidato'] for item in status_data],
        'status_totals': [item['total'] for item in status_data],
    }
    return render(request, 'core/dashboard.html', context)

# --- 2. VAGAS ---
@login_required
def cadastrar_vaga(request):
    perfil = getattr(request.user, 'cliente_perfil', None)

    if request.method == 'POST':
        form = VagaForm(request.POST)
        
        if not request.user.is_superuser:
            form.fields['cliente'].required = False

        if form.is_valid():
            vaga = form.save(commit=False)
            if not request.user.is_superuser:
                if perfil:
                    vaga.cliente = perfil
                else:
                    messages.error(request, "Seu usuário não tem uma empresa vinculada.")
                    return redirect('dashboard')
            
            vaga.save()
            messages.success(request, "Vaga publicada com sucesso!")
            return redirect('dashboard')
        else:
            print("❌ ERRO DE VALIDAÇÃO NO FORMULÁRIO:", form.errors)
            return render(request, 'core/cadastrar_vaga.html', {'form': form})
    else:
        form = VagaForm()
        if not request.user.is_superuser:
            if 'cliente' in form.fields:
                form.fields.pop('cliente')
    return render(request, 'core/cadastrar_vaga.html', {'form': form})

@login_required
def detalhes_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    
    if not request.user.is_superuser:
        if vaga.cliente != getattr(request.user, 'cliente_perfil', None):
            return redirect('dashboard')

    candidatos = vaga.candidatos.all().prefetch_related('historicos')
    
    # Adicionado 'reprovados' para bater com os cards do HTML
    contagem = {
        'triagem': candidatos.filter(status_candidato='Triagem').count(),
        'teste': candidatos.filter(status_candidato='Teste').count(),
        'entrevistas': candidatos.filter(status_candidato__icontains='Entrevista').count(),
        'aprovados': candidatos.filter(status_candidato='Aprovado').count(),
        'reprovados': candidatos.filter(status_candidato='Reprovado').count(),
    }

    return render(request, 'core/detalhes_vaga.html', {
        'vaga': vaga,
        'candidatos': candidatos,
        'total_inscritos': candidatos.count(),
        'contagem': contagem,
    })

@login_required
def mudar_status_vaga(request, vaga_id, novo_status):
    vaga = get_object_or_404(Vaga, id=vaga_id)
    
    # 🛡️ TRAVA DE SEGURANÇA: Apenas admin pode mudar o status da vaga
    if not request.user.is_superuser:
        messages.error(request, "Apenas os recrutadores da Rhino podem alterar o status das vagas.")
        return redirect('dashboard')
            
    vaga.status = novo_status
    vaga.save()
    messages.success(request, f"Status da vaga '{vaga.titulo}' atualizado com sucesso!")
    return redirect('dashboard')

# --- 3. CANDIDATOS ---
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

@login_required
def mudar_status_candidato(request, candidato_id, novo_status):
    candidato = get_object_or_404(Candidato, id=candidato_id)
    vaga_id = candidato.vaga.id # Para redirecionar de volta à vaga certa
    
    candidato.status_candidato = novo_status
    candidato.save()
    
    messages.success(request, f"Candidato {candidato.nome} movido para {novo_status}")
    return redirect('detalhes_vaga', vaga_id=vaga_id)

# --- 4. RELATÓRIOS ---
@login_required
def relatorio_geral(request):
    if request.user.is_superuser:
        vagas = Vaga.objects.all()
    else:
        perfil = getattr(request.user, 'cliente_perfil', None)
        vagas = Vaga.objects.filter(cliente=perfil)

    vagas_status = vagas.values('status').annotate(total=Count('id'))
    funil_geral = Candidato.objects.filter(vaga__in=vagas).values('status_candidato').annotate(total=Count('id'))

    context = {
        'vagas_status': vagas_status,
        'funil_geral': funil_geral,
        'total_vagas': vagas.count(),
        'total_candidatos': Candidato.objects.filter(vaga__in=vagas).count()
    }
    return render(request, 'core/relatorio_geral.html', context)

# --- 5. ADMINISTRAÇÃO ---
@user_passes_test(lambda u: u.is_superuser)
def cadastrar_cliente(request):
    if request.method == 'POST':
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            empresa = form.save(commit=False)
            empresa.usuario = user
            empresa.save()
            messages.success(request, f"Cliente {empresa.nome} cadastrado!")
            return redirect('dashboard')
    else:
        form = CadastroClienteForm()
    return render(request, 'core/cadastrar_cliente.html', {'form': form})



def inscrever_vaga(request, vaga_id):
    vaga = get_object_or_404(Vaga, id=vaga_id)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        curriculo = request.FILES.get('curriculo') # Arquivos vêm em request.FILES

        # Criar o candidato vinculado à vaga
        Candidato.objects.create(
            vaga=vaga,
            nome=nome,
            email=email,
            curriculo=curriculo,
            status_candidato='Triagem' # Status inicial padrão
        )

        messages.success(request, f"Sucesso! Sua candidatura para {vaga.titulo} foi enviada.")
        return render(request, 'core/sucesso_inscricao.html', {'vaga': vaga})

    return render(request, 'core/inscrever_vaga.html', {'vaga': vaga})