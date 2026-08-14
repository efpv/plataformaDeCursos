# 📚 Minha Escola - Plataforma de Cursos

Uma plataforma simples e elegante para organizar e disponibilizar conteúdo educacional (aulas em vídeo, PDFs e materiais) através de um navegador web.

---

## 🎯 Características Principais

- ✅ **Organização Hierárquica**: Estrutura de séries → módulos → aulas
- ✅ **Suporte Múltiplos Formatos**: Vídeos (.mp4, .mkv, .mov), PDFs (.pdf), apresentações (.ts)
- ✅ **Rastreamento de Progresso**: Salva automaticamente o progresso das aulas assistidas
- ✅ **Interface Web Responsiva**: Acesso via navegador em computador ou tablet
- ✅ **Geração Automática do Catálogo**: Descobre conteúdo automaticamente ao adicionar pastas
- ✅ **Servidor Local Seguro**: Funciona totalmente offline sem necessidade de conta

---

## ⚙️ Requisitos

- **Python 3.6+** (para rodar o servidor e gerar o catálogo)
- **Google Chrome** (recomendado) ou outro navegador moderno
- Windows 7+ ou qualquer SO com Python instalado

---

## 🚀 Como Iniciar

### Opção 1: Rápida (Recomendado - Windows)

1. Clique duas vezes em **`start.bat`**
2. O navegador abrirá automaticamente em `http://localhost:8080`
3. Pronto! A plataforma está rodando

O arquivo `start.bat` faz automaticamente:
- Atualiza o catálogo de conteúdo
- Inicia o servidor local na porta 8080
- Abre o navegador

### Opção 2: Manual (Qualquer SO)

1. Abra o terminal na pasta `Cursos/`
2. Execute:
   ```bash
   python gerar_catalogo.py
   ```
   (gera o arquivo `arquivos.json` com a árvore de conteúdo)

3. Inicie o servidor:
   ```bash
   python servidor.py 8080
   ```

4. Abra o navegador e acesse:
   ```
   http://localhost:8080
   ```

5. Para parar o servidor: pressione `Ctrl+C` no terminal

---

## 📂 Como Organizar seu Conteúdo

A plataforma reconhece automaticamente as pastas. Organize assim:

```
C:\Cursos\
├── start.bat
├── servidor.py
├── gerar_catalogo.py
├── index.html
├── app.js
├── styles.css
├── mux.min.js
├── arquivos.json          (gerado automaticamente)
├── progresso.json         (criado automaticamente)
│
├── Série 1
│   ├── Módulo 1
│   │   ├── aula_01.mp4
│   │   ├── aula_02.mp4
│   │   └── material.pdf
│   ├── Módulo 2
│   │   ├── aula_03.mkv
│   │   └── slides.ts
│
├── Série 2
│   ├── Módulo A
│   │   └── video.mov
```

### Regras de Organização

1. **Nomes de Pastas**: Use nomes descritivos (ex: "1º Ano", "Matemática Básica")
2. **Formatos Aceitos**: 
   - Vídeos: `.mp4`, `.mkv`, `.mov`
   - Documentos: `.pdf`
   - Apresentações: `.ts`
3. **Números em Nomes**: Ordena automaticamente (ex: "1 - Introdução", "2 - Conceitos")
4. **Ignorar Arquivos**: Comece nomes com ponto (`.pasta`) ou use subpastas para recursos auxiliares

---

## 💾 Adicionando Novo Conteúdo

1. Crie as pastas desejadas na estrutura
2. Copie os arquivos de vídeo/PDF/apresentação
3. Execute `python gerar_catalogo.py` (ou clique em `start.bat`)
4. Recarregue a página no navegador (F5)

**A plataforma reconhecerá automaticamente o novo conteúdo!**

---

## 📊 Sistema de Progresso

- **Salvo Automaticamente**: Conforme você assiste as aulas
- **Armazenamento Duplo**: 
  - Navegador (localStorage) - instantâneo
  - Disco (progresso.json) - backup permanente
- **Sincronização**: Se reiniciar o navegador ou computador, seu progresso é recuperado

---

## 🎨 Personalização

### Cores (Paleta)
Edite a constante `PALETA` no início de `app.js`:
```javascript
const PALETA = ['#c9a227','#8a6d1f','#4d6b8a', ...];
```

### Título e Branding
Edite o arquivo `index.html` ou `styles.css` para customizar aparência

---

## 🛠️ Solução de Problemas

### ❌ "Não foi possível carregar arquivos.json"
- Certifique-se de estar usando o `start.bat` ou rodando o `servidor.py`
- Não abra `index.html` direto no explorador (use `http://localhost:8080`)
- Rode `python gerar_catalogo.py` para gerar o catálogo

### ❌ Progresso não salva
- Se usar apenas `localStorage`: os dados se perdem ao limpar cache
- Use o servidor (`servidor.py`) para persistência em disco

### ❌ Arquivos não aparecem
- Verifique a extensão do arquivo (deve estar em `.mp4`, `.pdf`, `.mkv`, `.mov`, `.ts`)
- Execute `python gerar_catalogo.py` novamente
- Recarregue a página (F5)

### ❌ Erro "Porta já em uso"
O servidor está rodando de uma execução anterior. Abra `http://localhost:8080` no navegador ou finalize o processo:
```bash
netstat -ano | findstr :8080     # Windows
kill -9 $(lsof -ti:8080)          # Mac/Linux
```

---

## 📋 Arquivos do Projeto

| Arquivo | Função |
|---------|--------|
| `index.html` | Página principal da aplicação |
| `app.js` | Lógica da plataforma (navegação, player, progresso) |
| `styles.css` | Estilos visuais |
| `mux.min.js` | Biblioteca para reprodução de vídeo |
| `servidor.py` | Servidor HTTP com suporte a salvamento de progresso |
| `gerar_catalogo.py` | Script que varre pastas e gera `arquivos.json` |
| `start.bat` | Atalho para iniciar tudo automaticamente |
| `arquivos.json` | Catálogo gerado (hierarquia de conteúdo) |
| `progresso.json` | Histórico de aulas assistidas |

---

## 🔧 Para Desenvolvedores

### Adicionar uma Nova Porta
```bash
python servidor.py 9090
```

### Debug do Catálogo
```bash
python gerar_catalogo.py
# Inspecione arquivos.json gerado
```

### Estrutura de Dados
- `ARVORE`: Objeto JSON com hierarquia de pastas/arquivos
- `PROGRESSO_CACHE`: Dicionário com progresso por episódio
- Chave de progresso: `serie/modulo/arquivo`

---

## 📝 Exemplo Prático Completo

1. Crie a estrutura:
   ```
   C:\Cursos\
   ├── 1º Ano
   │   ├── Português
   │   │   ├── 01 - Alfabeto.mp4
   │   │   └── exercicios.pdf
   │   └── Matemática
   │       └── 01 - Números.mp4
   ```

2. Rode `start.bat` → navegador abre automaticamente

3. Clique em "1º Ano" → "Português" → "01 - Alfabeto.mp4"

4. Confira o progresso salvo em "Aulas em Andamento"

---

## 💡 Dicas

- 🎥 Use player integrado para vídeos (não baixe o arquivo)
- 📌 Mantenha nomes simples e descritivos
- 🔄 Sempre rode `gerar_catalogo.py` após adicionar conteúdo
- 💾 Faça backup de `progresso.json` periodicamente
- 📱 Acesse de qualquer dispositivo na rede local: `http://[seu-ip]:8080`

---

## 📞 Suporte

Consulte os comentários no código:
- `app.js` - Lógica da interface
- `servidor.py` - API de progresso
- `gerar_catalogo.py` - Geração do catálogo

---

**Versão**: 1.0  
**Última Atualização**: 2026  
**Licença**: Livre para uso pessoal e educacional
