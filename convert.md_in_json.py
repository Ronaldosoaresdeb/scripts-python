import os
import json
import re
from pathlib import Path

def parse_question_file(file_path):
    """Analisa um arquivo de questão capturando TODAS as opções"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai metadados básicos
    question_data = {
        "arquétipo": re.search(r'Arquétipo: "(.*?)"', content).group(1),
        "título": re.search(r'Título: "(.*?)"', content).group(1),
        "pergunta": re.search(r'Pergunta: "(.*?)"', content).group(1),
        "referência": re.search(r'> (https?://[^\s]+)', content).group(1) if re.search(r'> (https?://[^\s]+)', content) else "",
        "opções": []
    }

    # Regex aprimorado para capturar TODAS as opções
    options = re.findall(
        r'^\d+\.\s*\[(X|\s)\]\s*(.*?)(?=\n\d+\.|\n\Z|\n\s*\Z)',
        content,
        re.MULTILINE | re.DOTALL
    )

    for mark, text in options:
        question_data["opções"].append({
            "texto": text.strip(),
            "correta": mark.strip().upper() == 'X'
        })

    return question_data

def convert_files(input_dir, output_dir):
    """Converte todos os arquivos .md mantendo TODAS as opções"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.md'):
            continue
            
        md_path = os.path.join(input_dir, filename)
        json_path = os.path.join(output_dir, filename.replace('.md', '.json'))
        
        try:
            question_json = parse_question_file(md_path)
            
            # Verifica se capturou todas as opções
            if len(question_json["opções"]) < 1:
                print(f"⚠️ Aviso: {filename} parece não ter opções válidas")
                continue
                
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(question_json, f, ensure_ascii=False, indent=2)
            
            print(f"✅ {filename} - {len(question_json['opções'])} opções processadas")
            
        except Exception as e:
            print(f"❌ Erro em {filename}: {str(e)}")

if __name__ == "__main__":
    # CONFIGURAÇÃO - AJUSTE ESTES CAMINHOS!
    INPUT_DIR = r'C:\Users\Ronaldo\Documents\temp\actions'
    OUTPUT_DIR = r'C:\Users\Ronaldo\Documents\temp\actions\questions_json'
    
    print("🚀 Iniciando conversão...")
    convert_files(INPUT_DIR, OUTPUT_DIR)
    print("✅ Conversão concluída com sucesso!")