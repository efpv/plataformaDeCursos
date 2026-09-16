@echo off
cd C:\Cursos

REM Atualiza o catalogo (reconhece pastas/cursos novos automaticamente)
echo Atualizando catalogo...
python gerar_catalogo.py

REM Inicia o servidor local (salva progresso.json em disco tambem)
start "" python servidor.py 8080

REM Aguarda alguns segundos para garantir que o servidor suba
timeout /t 3 /nobreak >nul

REM Abre o navegador Google Chrome no endereço localhost:8080
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" http://localhost:8080
