"""
Servidor local para a plataforma Minha Escola.
Igual ao `python -m http.server`, mas com um endpoint extra que grava
o progresso de aulas assistidas em progresso.json (no disco), em vez
de depender só do localStorage do navegador.

Uso: python servidor.py 8080
"""
import http.server
import json
import os
import subprocess
import sys
import threading

ARQUIVO_PROGRESSO = 'progresso.json'

# Evita disparar duas transcrições do mesmo vídeo em paralelo se o usuário
# clicar no botão mais de uma vez antes da primeira terminar.
EM_ANDAMENTO = set()
TRAVA_EM_ANDAMENTO = threading.Lock()


def caminho_transcricao_relativo(partes):
    """Mesma convenção do app.js/transcrever.py: troca a extensão do último item por .txt."""
    partes = list(partes)
    nome_base, _ext = os.path.splitext(partes[-1])
    partes[-1] = nome_base + '.txt'
    return partes


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/progresso.json':
            self._responder_progresso()
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/progresso.json':
            self._salvar_progresso()
            return
        if self.path == '/transcrever':
            self._iniciar_transcricao()
            return
        self.send_error(404, 'Rota nao encontrada')

    def _responder_progresso(self):
        dados = {}
        if os.path.exists(ARQUIVO_PROGRESSO):
            try:
                with open(ARQUIVO_PROGRESSO, encoding='utf-8') as f:
                    dados = json.load(f)
            except (json.JSONDecodeError, OSError):
                dados = {}
        corpo = json.dumps(dados, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _salvar_progresso(self):
        try:
            tamanho = int(self.headers.get('Content-Length', 0))
            corpo = self.rfile.read(tamanho)
            dados = json.loads(corpo.decode('utf-8'))
        except (ValueError, json.JSONDecodeError):
            self.send_error(400, 'JSON invalido')
            return

        # grava em arquivo temporario e substitui, pra evitar corromper
        # o progresso.json se a escrita for interrompida no meio
        tmp = ARQUIVO_PROGRESSO + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(tmp, ARQUIVO_PROGRESSO)

        corpo_resposta = b'{"ok":true}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo_resposta)))
        self.end_headers()
        self.wfile.write(corpo_resposta)

    def _iniciar_transcricao(self):
        try:
            tamanho = int(self.headers.get('Content-Length', 0))
            corpo = self.rfile.read(tamanho)
            dados = json.loads(corpo.decode('utf-8'))
            caminho = dados['caminho']
            if not isinstance(caminho, list) or not caminho:
                raise ValueError('caminho vazio')
        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_error(400, 'corpo invalido: espera {"caminho": ["pasta", ..., "arquivo.mp4"]}')
            return

        caminho_txt = os.path.join(*caminho_transcricao_relativo(caminho))
        chave = os.path.join(*caminho)

        if os.path.exists(caminho_txt):
            status = 'pronta'
        else:
            with TRAVA_EM_ANDAMENTO:
                if chave in EM_ANDAMENTO:
                    status = 'em_andamento'
                else:
                    EM_ANDAMENTO.add(chave)
                    threading.Thread(target=self._rodar_transcricao, args=(caminho, chave), daemon=True).start()
                    status = 'iniciada'

        corpo_resposta = json.dumps({'status': status}, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(corpo_resposta)))
        self.end_headers()
        self.wfile.write(corpo_resposta)

    def _rodar_transcricao(self, caminho, chave):
        """Roda numa thread separada, então NÃO deve mexer em self.wfile — a resposta
        HTTP já foi enviada antes desta thread começar a rodar."""
        caminho_relativo = os.path.join(*caminho)
        with open('transcricao.log', 'a', encoding='utf-8') as log:
            log.write(f'\n=== Solicitado pelo player: {caminho_relativo} ===\n')
            log.flush()
            try:
                subprocess.run(
                    [sys.executable, '-X', 'utf8', '-u', 'transcrever.py', '--arquivo', caminho_relativo],
                    stdout=log, stderr=subprocess.STDOUT
                )
            finally:
                with TRAVA_EM_ANDAMENTO:
                    EM_ANDAMENTO.discard(chave)

    def log_message(self, formato, *args):
        pass  # silencia o log padrao no console


def main():
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    servidor = http.server.ThreadingHTTPServer(('', porta), Handler)
    print(f'Servindo Minha Escola em http://localhost:{porta}')
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
