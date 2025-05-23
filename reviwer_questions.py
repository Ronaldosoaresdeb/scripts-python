import os
import json
from openai import OpenAI

# ✅ Configura conexão com servidor Ollama local
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # valor qualquer, pois o Ollama ignora
)

PASTA_ORIGINAL = "data"
PASTA_REVISADA = "revisado"
PASTA_LOG = "logs"
CAMINHO_LOG_ERROS = os.path.join(PASTA_LOG, "erros.txt")

os.makedirs(PASTA_LOG, exist_ok=True)

for topico in os.listdir(PASTA_ORIGINAL):
    caminho_topico_original = os.path.join(PASTA_ORIGINAL, topico)
    if not os.path.isdir(caminho_topico_original):
        continue

    # Cria pastas para revisado e logs
    caminho_topico_revisado = os.path.join(PASTA_REVISADA, topico)
    caminho_topico_logs = os.path.join(PASTA_LOG, topico)
    os.makedirs(caminho_topico_revisado, exist_ok=True)
    os.makedirs(caminho_topico_logs, exist_ok=True)

    for arquivo in os.listdir(caminho_topico_original):
        if not arquivo.endswith(".json"):
            continue

        caminho_arquivo = os.path.join(caminho_topico_original, arquivo)

        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                pergunta = json.load(f)

            prompt = f"""
Você é um especialista técnico em GitHub Actions. Sua tarefa é reescrever a seguinte pergunta em português claro, com linguagem técnica e acessível ao público brasileiro, sem perder o sentido.

Pergunta original:
"{pergunta['pergunta']}"

Reescreva a pergunta de forma clara e explique brevemente o que você melhorou. A resposta deve estar nesse formato:

PERGUNTA REESCRITA:
<NOVA PERGUNTA AQUI>

COMENTÁRIO:
<EXPLICAÇÃO AQUI>
"""

            resposta = client.chat.completions.create(
                model="llama3",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            resposta_texto = resposta.choices[0].message.content.strip()

            # Separa nova pergunta e comentário
            if "PERGUNTA REESCRITA:" in resposta_texto and "COMENTÁRIO:" in resposta_texto:
                nova_parte, comentario_parte = resposta_texto.split("COMENTÁRIO:")
                nova_pergunta = nova_parte.replace("PERGUNTA REESCRITA:", "").strip()
                comentario = comentario_parte.strip()
            else:
                nova_pergunta = resposta_texto
                comentario = "Nenhum comentário gerado."

            # Atualiza o campo da pergunta
            pergunta["pergunta"] = nova_pergunta

            # Salva pergunta revisada
            caminho_saida = os.path.join(caminho_topico_revisado, arquivo)
            with open(caminho_saida, "w", encoding="utf-8") as f:
                json.dump(pergunta, f, indent=2, ensure_ascii=False)

            # Salva o comentário em log
            nome_log = f"{topico.lower()}-{arquivo}"
            caminho_log = os.path.join(caminho_topico_logs, nome_log)
            with open(caminho_log, "w", encoding="utf-8") as f:
                f.write(f"{{{{ {comentario} }}}}\n")

            print(f"✔ Revisado: {caminho_saida}")
            print(f"📝 Log: {caminho_log}")

        except Exception as e:
            mensagem_erro = f"❌ Erro em {topico}/{arquivo}: {str(e)}"
            print(mensagem_erro)
            with open(CAMINHO_LOG_ERROS, "a", encoding="utf-8") as log_erro:
                log_erro.write(mensagem_erro + "\n")
            continue
