@echo off
REM Script portável - funciona em qualquer pasta/máquina/usuário
REM Não altera o diretório porque já está na pasta correta

REM Atualiza o catalogo (reconhece pastas/cursos novos automaticamente)
echo Atualizando catalogo...
python gerar_catalogo.py

REM Inicia o servidor local (salva progresso.json em disco tambem)
echo Iniciando servidor...
start "" python servidor.py 8080

REM Aguarda alguns segundos para garantir que o servidor suba
timeout /t 3 /nobreak >nul

REM Abre o navegador padrão no endereço localhost:8080
echo Abrindo navegador...
start http://localhost:8080
