import requests
from .models import Candidato, Vaga

def sincronizar_com_sophia(vaga_id_rhino, vaga_id_sophia):
    api_key = "SUA_CHAVE_AQUI"
    url = f"https://api.starminds.com.br/v1/vagas/{vaga_id_sophia}/candidatos"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        dados = response.json() # Aqui estão os candidatos
        vaga = Vaga.objects.get(id=vaga_id_rhino)

        for item in dados['candidatos']:
            # Só cria se o candidato ainda não existir no seu sistema
            Candidato.objects.get_or_create(
                sophia_id=item['id'],
                defaults={
                    'vaga': vaga,
                    'nome': item['nome'],
                    'email': item['email'],
                    'link_entrevista': item['link_video'],
                    'score_comportamental': item['score'],
                    'status_candidato': 'Triagem'
                }
            )
        return True
    return False