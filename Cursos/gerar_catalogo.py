"""
Gera/atualiza o arquivos.json usado pela plataforma Minha Escola.
Roda a partir da própria pasta raiz (C:\\Cursos) e varre tudo
recursivamente, montando a árvore de séries > módulos > aulas.

Uso: basta rodar `python gerar_catalogo.py` dentro de C:\\Cursos
(o start.bat já faz isso automaticamente antes de subir o servidor).
"""
import json
import os
import re

# Extensões que entram no catálogo como "aula"/"material"
EXTENSOES_VALIDAS = {'.ts', '.pdf', '.mp4', '.mkv', '.mov'}

# Nomes que nunca devem ser tratados como conteúdo de curso
IGNORAR_NOMES = {
    'arquivos.json', 'index.html', 'mux.min.js',
    'gerar_catalogo.py', 'start.bat', 'files.zip', 'files',
    'servidor.py', 'progresso.json', 'styles.css', 'app.js',
}


def chave_ordenacao_natural(nome):
    # Quebra o nome em pedaços de texto e números, convertendo os números
    # pra int, assim "2" vem antes de "10" (em vez de comparação alfabética
    # onde "10" < "2" por ordem de caractere).
    pedacos = re.split(r'(\d+)', nome)
    return [int(p) if p.isdigit() else p.lower() for p in pedacos]


def pasta_deve_ser_ignorada(nome):
    return nome.startswith('.') or nome in IGNORAR_NOMES


def construir_arvore(caminho_raiz):
    raiz = {}

    def visitar(pasta_fisica, no_arvore):
        try:
            itens = sorted(os.listdir(pasta_fisica), key=chave_ordenacao_natural)
        except PermissionError:
            return

        for nome in itens:
            if pasta_deve_ser_ignorada(nome):
                continue

            caminho_completo = os.path.join(pasta_fisica, nome)

            if os.path.isdir(caminho_completo):
                subno = no_arvore.setdefault(nome, {})
                visitar(caminho_completo, subno)
            else:
                _, ext = os.path.splitext(nome)
                if ext.lower() in EXTENSOES_VALIDAS:
                    no_arvore.setdefault('_files', []).append(nome)

    visitar(caminho_raiz, raiz)
    return raiz


def main():
    raiz = os.getcwd()
    arvore = construir_arvore(raiz)

    destino = os.path.join(raiz, 'arquivos.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(arvore, f, ensure_ascii=False, indent=2)

    total_series = len(arvore)
    print(f'Catalogo atualizado: {total_series} series encontradas em {destino}')


if __name__ == '__main__':
    main()
