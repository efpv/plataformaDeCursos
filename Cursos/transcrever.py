#!/usr/bin/env python3
"""
transcrever.py — Gera transcrições em .txt para os vídeos do catálogo,
reaproveitando o mesmo arquivos.json que o player (app.js) já usa.

Cada vídeo "Aula 1.mp4" gera um "Aula 1.txt" na MESMA pasta — é a mesma
convenção que o app.js espera (ver caminhoTranscricao em app.js).

Requisitos:
    pip install faster-whisper
    ffmpeg precisa estar instalado no sistema (faster-whisper usa por baixo dos panos)

Uso:
    python transcrever.py                     # transcreve tudo que ainda não tem .txt (lote)
    python transcrever.py --modelo small      # escolhe o tamanho do modelo Whisper
    python transcrever.py --idioma pt         # força o idioma (senão detecta automaticamente)
    python transcrever.py --forcar            # re-transcreve mesmo o que já tem .txt
    python transcrever.py --base "C:\\Cursos"  # se não estiver rodando na própria pasta

    # Transcrever só UM vídeo específico (ex: o que está em execução no player agora):
    python transcrever.py --arquivo "AUVP\\1 - Modulo 1\\Aula 1.ts"
"""
import argparse
import json
import sys
from pathlib import Path


def coletar_videos(node, prefixo, saida):
    """Percorre a árvore de arquivos.json e coleta os caminhos dos vídeos (ignora PDFs).
    Mesma lógica de flattenEpisodios() em app.js — mantemos as duas em sincronia."""
    for arquivo in node.get('_files', []):
        if arquivo.lower().endswith('.pdf'):
            continue
        saida.append(prefixo + [arquivo])
    for chave, sub in node.items():
        if chave == '_files':
            continue
        coletar_videos(sub, prefixo + [chave], saida)
    return saida


def caminho_transcricao(caminho_video: Path) -> Path:
    """Mesma regra do app.js: troca a extensão do vídeo por .txt."""
    return caminho_video.with_suffix('.txt')


def carregar_modelo(nome_modelo):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit('faster-whisper não está instalado. Rode: pip install faster-whisper')
    print(f'Carregando modelo Whisper "{nome_modelo}"... (baixa na primeira vez, pode demorar)')
    return WhisperModel(nome_modelo, device='cpu', compute_type='int8')


def transcrever_um(modelo, caminho_video: Path, caminho_txt: Path, idioma=None):
    if not caminho_video.exists():
        sys.exit(f'Arquivo não encontrado: {caminho_video}')
    print(f'Transcrevendo: {caminho_video.name}')
    segmentos, info = modelo.transcribe(str(caminho_video), language=idioma, vad_filter=True)
    texto = ' '.join(seg.text.strip() for seg in segmentos)
    caminho_txt.write_text(texto.strip() + '\n', encoding='utf-8')
    print(f'-> salvo em {caminho_txt} (idioma detectado: {info.language})')


def main():
    parser = argparse.ArgumentParser(
        description='Gera transcrições .txt para os vídeos do catálogo (arquivos.json).'
    )
    parser.add_argument('--base', default='.',
                         help='Pasta onde estão arquivos.json e os vídeos (padrão: pasta atual)')
    parser.add_argument('--modelo', default='small',
                         help='Modelo Whisper: tiny, base, small, medium, large-v3 (padrão: small)')
    parser.add_argument('--idioma', default=None,
                         help='Código do idioma (ex: pt, en). Se omitido, detecta automaticamente por vídeo.')
    parser.add_argument('--forcar', action='store_true',
                         help='Re-transcreve mesmo os vídeos que já têm .txt')
    parser.add_argument('--arquivo', default=None,
                         help='Caminho de UM vídeo específico (relativo à --base) pra transcrever só ele, '
                              'em vez do catálogo inteiro. Ex: "AUVP/1 - Modulo 1/Aula 1.ts"')
    args = parser.parse_args()

    base = Path(args.base)

    # ---------- Modo "um vídeo só" (ex: o que está tocando agora no player) ----------
    if args.arquivo:
        caminho_video = base / args.arquivo
        caminho_txt = caminho_transcricao(caminho_video)
        if caminho_txt.exists() and not args.forcar:
            print(f'Já existe transcrição em {caminho_txt} (use --forcar pra gerar de novo).')
            return
        modelo = carregar_modelo(args.modelo)
        transcrever_um(modelo, caminho_video, caminho_txt, args.idioma)
        return

    # ---------- Modo em lote: catálogo inteiro, a partir de arquivos.json ----------
    arquivo_json = base / 'arquivos.json'
    if not arquivo_json.exists():
        sys.exit(f'Não encontrei {arquivo_json}. Rode este script na pasta do catálogo, ou use --base.')

    arvore = json.loads(arquivo_json.read_text(encoding='utf-8'))
    videos = coletar_videos(arvore, [], [])
    if not videos:
        print('Nenhum vídeo encontrado em arquivos.json.')
        return

    modelo = carregar_modelo(args.modelo)

    pendentes = []
    for caminho in videos:
        caminho_video = base.joinpath(*caminho)
        caminho_txt = caminho_transcricao(caminho_video)
        if caminho_txt.exists() and not args.forcar:
            continue
        pendentes.append((caminho_video, caminho_txt))

    print(f'{len(videos)} vídeos no catálogo, {len(pendentes)} pendente(s) de transcrição.\n')

    for i, (caminho_video, caminho_txt) in enumerate(pendentes, 1):
        if not caminho_video.exists():
            print(f'[{i}/{len(pendentes)}] AVISO: arquivo não encontrado, pulando: {caminho_video}')
            continue
        print(f'[{i}/{len(pendentes)}] ', end='')
        transcrever_um(modelo, caminho_video, caminho_txt, args.idioma)

    print('\nConcluído.')


if __name__ == '__main__':
    main()

