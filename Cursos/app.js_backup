const PALETA = ['#c9a227','#8a6d1f','#4d6b8a','#5c4a8a','#8a4a4a','#3f7a63','#7a5b12','#2f5f7a'];
let ARVORE = {};
let caminhoAtual = [];
let emPlayer = null;
let timerAutoAvancoGlobal = null;

// ---------- Progresso (salvo em progresso.json no servidor local; localStorage como reserva) ----------
const CHAVE_PROGRESSO = 'auvp_progresso_v1';
let PROGRESSO_CACHE = {};
let salvarProgressoTimer = null;

function carregarProgressoLocalStorage(){
  try{ return JSON.parse(localStorage.getItem(CHAVE_PROGRESSO) || '{}'); }
  catch(e){ return {}; }
}

async function carregarProgressoInicial(){
  // tenta o arquivo no servidor primeiro (fonte confiável); se falhar, usa o backup do navegador
  try{
    const resp = await fetch('progresso.json', { cache: 'no-store' });
    if(resp.ok){
      PROGRESSO_CACHE = await resp.json();
      return;
    }
  }catch(e){ /* servidor sem suporte a /progresso.json (ex: http.server padrão) */ }
  PROGRESSO_CACHE = carregarProgressoLocalStorage();
}

function persistirProgresso(){
  // grava sempre no localStorage na hora (rápido, nunca falha)
  try{ localStorage.setItem(CHAVE_PROGRESSO, JSON.stringify(PROGRESSO_CACHE)); }catch(e){}
  // e agenda o envio pro arquivo em disco, com um pequeno debounce
  clearTimeout(salvarProgressoTimer);
  salvarProgressoTimer = setTimeout(() => {
    fetch('progresso.json', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(PROGRESSO_CACHE)
    }).catch(() => { /* sem servidor com suporte a POST — fica só no localStorage mesmo */ });
  }, 600);
}

function chaveEpisodio(caminhoArquivo){ return caminhoArquivo.join('/'); }
function obterProgresso(caminhoArquivo){
  return PROGRESSO_CACHE[chaveEpisodio(caminhoArquivo)] || null;
}
function atualizarProgresso(caminhoArquivo, dados){
  const chave = chaveEpisodio(caminhoArquivo);
  PROGRESSO_CACHE[chave] = Object.assign({}, PROGRESSO_CACHE[chave], dados, { atualizadoEm: Date.now() });
  persistirProgresso();
}
function contarProgressoNode(node, prefixo){
  let total = 0, concluidos = 0;
  (node._files || []).forEach(a => {
    total++;
    const p = obterProgresso([...prefixo, a]);
    if(p && p.concluido) concluidos++;
  });
  for(const k in node){
    if(k === '_files') continue;
    const sub = contarProgressoNode(node[k], [...prefixo, k]);
    total += sub.total; concluidos += sub.concluidos;
  }
  return { total, concluidos };
}

function listarEmAndamento(node, prefixo, saida){
  saida = saida || [];
  (node._files || []).forEach(a => {
    if(/\.pdf$/i.test(a)) return;
    const caminho = [...prefixo, a];
    const p = obterProgresso(caminho);
    if(p && !p.concluido && p.posicao > 5){
      saida.push({ caminho, prog: p });
    }
  });
  for(const k in node){
    if(k === '_files') continue;
    listarEmAndamento(node[k], [...prefixo, k], saida);
  }
  return saida;
}
function formatarTempo(segundos){
  segundos = Math.max(0, Math.floor(segundos || 0));
  const m = Math.floor(segundos / 60);
  const s = segundos % 60;
  return `${m}:${String(s).padStart(2,'0')}`;
}

async function iniciar(){
  try{
    const [resp] = await Promise.all([
      fetch('arquivos.json'),
      carregarProgressoInicial()
    ]);
    ARVORE = await resp.json();
  }catch(e){
    document.getElementById('main').innerHTML =
      '<div class="empty">Não foi possível carregar arquivos.json.<br>Confirme que este arquivo está na mesma pasta que index.html e que você está acessando via um servidor local (ex: python servidor.py 8080), não abrindo o arquivo direto (file://).</div>';
    return;
  }
  render();
}

function corPara(nome){
  let h = 0;
  for(let i=0;i<nome.length;i++) h = (h*31 + nome.charCodeAt(i)) >>> 0;
  return PALETA[h % PALETA.length];
}

function no(caminho){
  let n = ARVORE;
  for(const p of caminho) n = n[p];
  return n;
}

// Acha o próximo arquivo de vídeo (pula PDFs) dentro da mesma pasta do episódio atual
// Lista, em ordem, todos os arquivos de vídeo (não-PDF) de um nó da árvore,
// entrando em subpastas na ordem em que elas aparecem (mesma ordem da tela).
function flattenEpisodios(node, prefixo, saida){
  saida = saida || [];
  for(const chave of Object.keys(node)){
    if(chave === '_files'){
      node._files.forEach(arquivo => {
        if(!/\.pdf$/i.test(arquivo)) saida.push([...prefixo, arquivo]);
      });
    } else {
      flattenEpisodios(node[chave], [...prefixo, chave], saida);
    }
  }
  return saida;
}

// Acha o próximo vídeo do curso (mesma série de topo), na ordem de exibição —
// funciona tanto quando os vídeos estão soltos na mesma pasta quanto quando
// cada aula tem sua própria subpasta (ex: "1 - Aula 1/Aula 1.mp4").
function encontrarProximoEpisodio(caminhoArquivo){
  const serieRaiz = caminhoArquivo[0];
  const nodeSerie = ARVORE[serieRaiz];
  if(!nodeSerie) return null;
  const lista = flattenEpisodios(nodeSerie, [serieRaiz]);
  const chaveAtual = chaveEpisodio(caminhoArquivo);
  const idx = lista.findIndex(c => chaveEpisodio(c) === chaveAtual);
  if(idx === -1 || idx === lista.length - 1) return null;
  return lista[idx + 1];
}

function contarEpisodios(node){
  let total = (node._files || []).length;
  for(const k in node){
    if(k === '_files') continue;
    total += contarEpisodios(node[k]);
  }
  return total;
}

function irParaInicio(){
  clearInterval(timerAutoAvancoGlobal);
  emPlayer = null; caminhoAtual = []; render();
}

function irPara(caminho){
  clearInterval(timerAutoAvancoGlobal);
  emPlayer = null; caminhoAtual = caminho; render();
}

function abrirEpisodio(caminho){
  clearInterval(timerAutoAvancoGlobal);
  emPlayer = caminho;
  render();
}

function nomeAmigavel(arquivo){
  return arquivo.replace(/\.(ts|pdf)$/i, '').replace(/_$/, '?');
}

function renderCrumbs(){
  const el = document.getElementById('crumbs');
  if(emPlayer || caminhoAtual.length === 0){ el.innerHTML = ''; return; }
  let html = '<span class="seg" onclick="irParaInicio()">Início</span>';
  caminhoAtual.forEach((p, i) => {
    const acumulado = caminhoAtual.slice(0, i+1);
    html += '<span class="sep">/</span>';
    html += `<span class="seg" onclick='irPara(${JSON.stringify(acumulado)})'>${p}</span>`;
  });
  el.innerHTML = html;
}

function render(){
  renderCrumbs();
  const main = document.getElementById('main');
  main.innerHTML = '';

  if(emPlayer){
    main.appendChild(renderPlayer(emPlayer));
    return;
  }

  const node = no(caminhoAtual);
  if(!node){ main.innerHTML = '<div class="empty">Conteúdo não encontrado.</div>'; return; }

  if(caminhoAtual.length === 0){
    main.appendChild(renderHero());
    const emAndamento = listarEmAndamento(ARVORE, [])
      .sort((a, b) => (b.prog.atualizadoEm || 0) - (a.prog.atualizadoEm || 0))
      .slice(0, 6);
    if(emAndamento.length){
      const sec = document.createElement('div');
      sec.innerHTML = `<div class="section-title"><h2>Continuar assistindo</h2><span class="count">${emAndamento.length}</span></div>`;
      const grid = document.createElement('div');
      grid.className = 'grid';
      emAndamento.forEach(item => grid.appendChild(cardContinuar(item.caminho, item.prog)));
      sec.appendChild(grid);
      main.appendChild(sec);
    }
  } else {
    const back = document.createElement('button');
    back.className = 'back-btn';
    back.textContent = '← Voltar';
    back.onclick = () => irPara(caminhoAtual.slice(0, -1));
    main.appendChild(back);

    const titulo = document.createElement('h2');
    titulo.style.margin = '4px 0 20px';
    titulo.style.fontSize = '26px';
    titulo.textContent = caminhoAtual[caminhoAtual.length - 1];
    main.appendChild(titulo);
  }

  const pastas = Object.keys(node).filter(k => k !== '_files');
  const arquivos = node._files || [];

  if(pastas.length){
    const sec = document.createElement('div');
    sec.innerHTML = `<div class="section-title"><h2>${caminhoAtual.length === 0 ? 'Séries' : 'Módulos'}</h2><span class="count">${pastas.length}</span></div>`;
    const grid = document.createElement('div');
    grid.className = 'grid';
    pastas.forEach(p => grid.appendChild(cardPasta(p, node[p])));
    sec.appendChild(grid);
    main.appendChild(sec);
  }

  if(arquivos.length){
    const sec = document.createElement('div');
    sec.innerHTML = `<div class="section-title"><h2>Episódios</h2><span class="count">${arquivos.length}</span></div>`;
    const grid = document.createElement('div');
    grid.className = 'grid';
    arquivos.forEach((a, idx) => grid.appendChild(cardEpisodio(a, idx)));
    sec.appendChild(grid);
    main.appendChild(sec);
  }

  if(!pastas.length && !arquivos.length){
    main.innerHTML += '<div class="empty">Nada por aqui ainda.</div>';
  }
}

function renderHero(){
  const wrap = document.createElement('div');
  const totalSeries = Object.keys(ARVORE).length;
  const prog = contarProgressoNode(ARVORE, []);
  const fraseProgresso = prog.concluidos > 0
    ? ` Você já concluiu ${prog.concluidos} de ${prog.total}.`
    : '';
  wrap.innerHTML = `
    <div class="hero">
      <div class="eyebrow">Catálogo local</div>
      <h1>Sua trilha de estudos, do seu jeito</h1>
      <p>${totalSeries} séries e ${prog.total} aulas organizadas por módulo.${fraseProgresso} Escolha uma série abaixo para começar.</p>
    </div>
  `;
  return wrap;
}

function cardContinuar(caminhoArquivo, prog){
  const arquivo = caminhoArquivo[caminhoArquivo.length - 1];
  const amigavel = nomeAmigavel(arquivo);
  const cor = corPara(arquivo);
  const fracao = prog.duracao ? Math.min(1, prog.posicao / prog.duracao) : 0;
  const card = document.createElement('div');
  card.className = 'card episode';
  card.innerHTML = `
    <div class="tile" style="background: linear-gradient(135deg, ${cor}, #0b0e14 140%);">
      <span class="num">${caminhoArquivo.slice(0, -1).join(' › ')}</span>
      <span>${amigavel}</span>
      <div class="play"><div class="dot">▶</div></div>
      <div class="progresso-barra"><i style="width:${Math.round(fracao*100)}%"></i></div>
    </div>
    <div class="meta">
      <div class="title">${amigavel}</div>
      <div class="sub">Continuar em ${formatarTempo(prog.posicao)}</div>
    </div>
  `;
  card.onclick = () => abrirEpisodio(caminhoArquivo);
  return card;
}

function cardPasta(nome, node){
  const card = document.createElement('div');
  card.className = 'card';
  const cor = corPara(nome);
  const eps = contarEpisodios(node);
  const subpastas = Object.keys(node).filter(k => k !== '_files').length;
  const prog = contarProgressoNode(node, [...caminhoAtual, nome]);
  const tudoConcluido = prog.total > 0 && prog.concluidos === prog.total;
  const progTexto = prog.concluidos > 0 ? ` · ${prog.concluidos}/${prog.total} concluídas` : '';
  card.innerHTML = `
    <div class="tile" style="background: linear-gradient(135deg, ${cor}, #0b0e14 130%);">
      <span class="num">${subpastas ? 'SÉRIE' : 'MÓDULO'}</span>
      <span>${nome}</span>
      <span class="icon">📁</span>
      ${tudoConcluido ? `<span class="concluido-badge">✓</span>` : ''}
    </div>
    <div class="meta">
      <div class="title">${nome}</div>
      <div class="sub">${subpastas ? subpastas + ' módulos · ' : ''}${eps} aula${eps===1?'':'s'}${progTexto}</div>
    </div>
  `;
  card.onclick = () => irPara([...caminhoAtual, nome]);
  return card;
}

function cardEpisodio(arquivo, idx){
  const card = document.createElement('div');
  card.className = 'card episode';
  const cor = corPara(arquivo + idx);
  const amigavel = nomeAmigavel(arquivo);
  const ehPdf = /\.pdf$/i.test(arquivo);
  const caminhoArquivo = [...caminhoAtual, arquivo];
  const prog = obterProgresso(caminhoArquivo);
  const concluido = !!(prog && prog.concluido);
  const fracao = (prog && prog.duracao) ? Math.min(1, (prog.posicao || 0) / prog.duracao) : 0;
  const emAndamento = !concluido && fracao > 0.02;

  card.innerHTML = `
    <div class="tile" style="background: linear-gradient(135deg, ${cor}, #0b0e14 140%);">
      <span class="num">EP ${String(idx+1).padStart(2,'0')}</span>
      <span>${amigavel}</span>
      ${ehPdf ? '' : `<div class="play"><div class="dot">▶</div></div>`}
      <span class="icon">${ehPdf ? '📄' : ''}</span>
      ${concluido ? `<span class="concluido-badge">✓</span>` : ''}
      ${emAndamento ? `<div class="progresso-barra"><i style="width:${Math.round(fracao*100)}%"></i></div>` : ''}
    </div>
    <div class="meta">
      <div class="title">${amigavel}</div>
      <div class="sub">${ehPdf ? (concluido ? '✓ PDF aberto' : 'Material em PDF') : (concluido ? 'Concluída' : (emAndamento ? `Continuar em ${formatarTempo(prog.posicao)}` : 'Aula em vídeo'))}</div>
    </div>
  `;
  card.onclick = () => {
    if(ehPdf){
      window.open(caminhoArquivo.map(encodeURIComponent).join('/'), '_blank');
      if(!concluido){
        atualizarProgresso(caminhoArquivo, { concluido: true });
        render(); // atualiza o card com o selo de concluído e o contador da pasta
      }
    } else {
      abrirEpisodio(caminhoArquivo);
    }
  };
  return card;
}

function renderPlayer(caminhoArquivo){
  const wrap = document.createElement('div');
  wrap.className = 'player-wrap';

  const back = document.createElement('button');
  back.className = 'back-btn';
  back.textContent = '← Voltar';
  back.onclick = () => irPara(caminhoAtual);
  wrap.appendChild(back);

  const arquivo = caminhoArquivo[caminhoArquivo.length - 1];
  const src = caminhoArquivo.map(encodeURIComponent).join('/');

  const titulo = document.createElement('h1');
  titulo.textContent = nomeAmigavel(arquivo);
  wrap.appendChild(titulo);

  const caminhoTexto = document.createElement('div');
  caminhoTexto.className = 'path';
  caminhoTexto.textContent = caminhoArquivo.join(' / ');
  wrap.appendChild(caminhoTexto);

  const video = document.createElement('video');
  video.controls = true;
  wrap.appendChild(video);

  const loading = document.createElement('div');
  loading.className = 'loading-ts';
  loading.innerHTML = `<span class="spinner"></span><span>Preparando o vídeo (convertendo .ts no navegador)…</span>`;
  wrap.appendChild(loading);

  const fallback = document.createElement('div');
  fallback.className = 'fallback';
  fallback.innerHTML = `
    Não foi possível reproduzir este arquivo direto no navegador.<br><br>
    Opções:<br>
    • Abra o arquivo direto em um player local como <strong>VLC</strong> (funciona sem conversão).<br>
    • Ou tente abrir em uma nova aba: <a href="${src}" target="_blank">${arquivo}</a>.
  `;
  wrap.appendChild(fallback);

  // ---------- Controle de "concluída" + retomar de onde parou ----------
  const progAtual = obterProgresso(caminhoArquivo) || {};
  const btnConcluido = document.createElement('button');
  btnConcluido.className = 'marcar-concluido' + (progAtual.concluido ? ' ativo' : '');
  btnConcluido.textContent = progAtual.concluido ? '✓ Aula concluída' : 'Marcar como concluída';
  btnConcluido.onclick = () => {
    const novoEstado = !btnConcluido.classList.contains('ativo');
    atualizarProgresso(caminhoArquivo, { concluido: novoEstado });
    btnConcluido.classList.toggle('ativo', novoEstado);
    btnConcluido.textContent = novoEstado ? '✓ Aula concluída' : 'Marcar como concluída';
  };

  // ---------- Velocidade de reprodução (lembra a última escolhida) ----------
  const VELOCIDADES = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2];
  const velocidadeSalva = parseFloat(localStorage.getItem('auvp_velocidade')) || 1;
  video.playbackRate = velocidadeSalva;

  const velocidadeWrap = document.createElement('div');
  velocidadeWrap.className = 'velocidade-wrap';
  velocidadeWrap.innerHTML = '<span class="velocidade-label">Velocidade</span>' +
    VELOCIDADES.map(v => `<button type="button" class="velocidade-btn${v === velocidadeSalva ? ' ativo' : ''}" data-v="${v}">${v}x</button>`).join('');
  velocidadeWrap.querySelectorAll('.velocidade-btn').forEach(btn => {
    btn.onclick = () => {
      const v = parseFloat(btn.dataset.v);
      video.playbackRate = v;
      try{ localStorage.setItem('auvp_velocidade', v); }catch(e){}
      velocidadeWrap.querySelectorAll('.velocidade-btn').forEach(b => b.classList.toggle('ativo', b === btn));
    };
  });
  // reaplica a velocidade sempre que uma nova fonte é carregada (o navegador reseta pra 1x às vezes)
  video.addEventListener('loadedmetadata', () => { video.playbackRate = velocidadeSalva; });

  const controles = document.createElement('div');
  controles.className = 'player-controles';
  controles.appendChild(btnConcluido);
  controles.appendChild(velocidadeWrap);

  const proximoCaminho = encontrarProximoEpisodio(caminhoArquivo);
  if(proximoCaminho){
    const btnProximo = document.createElement('button');
    btnProximo.className = 'btn-proximo';
    btnProximo.textContent = 'Próxima aula ⏭';
    btnProximo.onclick = () => abrirEpisodio(proximoCaminho);
    controles.appendChild(btnProximo);
  }
  wrap.appendChild(controles);

  // ---------- Auto-avanço pra próxima aula, com contagem regressiva cancelável ----------
  const autoAvanco = document.createElement('div');
  autoAvanco.className = 'auto-avanco';
  wrap.appendChild(autoAvanco);

  let timerAutoAvanco = null;
  function dispararAutoAvanco(){
    if(!proximoCaminho){ return; }
    let restante = 5;
    const nomeProximo = nomeAmigavel(proximoCaminho[proximoCaminho.length - 1]);
    function atualizarTexto(){
      autoAvanco.innerHTML = `
        Próxima aula em ${restante}s — <strong>${nomeProximo}</strong>
        <button type="button" class="btn-cancelar-avanco">Cancelar</button>
      `;
      autoAvanco.querySelector('.btn-cancelar-avanco').onclick = () => {
        clearInterval(timerAutoAvanco);
        autoAvanco.classList.remove('show');
      };
    }
    autoAvanco.classList.add('show');
    atualizarTexto();
    timerAutoAvanco = setInterval(() => {
      restante--;
      if(restante <= 0){
        clearInterval(timerAutoAvanco);
        abrirEpisodio(proximoCaminho);
        return;
      }
      atualizarTexto();
    }, 1000);
    timerAutoAvancoGlobal = timerAutoAvanco;
  }

  let posicaoRetomar = (progAtual.posicao && !progAtual.concluido) ? progAtual.posicao : 0;
  let jaRetomou = false;
  let ultimoSalvo = 0;

  function tentarRetomar(){
    if(jaRetomou || posicaoRetomar < 5) { jaRetomou = true; return; }
    if(video.buffered.length && video.buffered.end(video.buffered.length - 1) >= posicaoRetomar){
      video.currentTime = posicaoRetomar;
      jaRetomou = true;
    }
  }

  video.addEventListener('progress', tentarRetomar);
  video.addEventListener('loadedmetadata', tentarRetomar);

  video.addEventListener('timeupdate', () => {
    const agora = Date.now();
    if(agora - ultimoSalvo < 4000) return; // salva no máximo a cada 4s
    ultimoSalvo = agora;
    const dados = { posicao: video.currentTime };
    if(video.duration && isFinite(video.duration)) dados.duracao = video.duration;
    atualizarProgresso(caminhoArquivo, dados);
  });

  video.addEventListener('ended', () => {
    atualizarProgresso(caminhoArquivo, { concluido: true, posicao: 0 });
    btnConcluido.classList.add('ativo');
    btnConcluido.textContent = '✓ Aula concluída';
    dispararAutoAvanco();
  });

  const ehTs = /\.ts$/i.test(arquivo);
  if(ehTs){
    tocarTS(video, src, fallback, loading);
  } else {
    video.src = src;
    video.addEventListener('error', () => fallback.classList.add('show'));
  }

  return wrap;
}

// Remuxa MPEG-TS -> fragmented MP4 no navegador (via mux.js) e alimenta via MediaSource Extensions,
// lendo o arquivo em pedaços (streaming) em vez de baixar tudo de uma vez — reduz o tempo até começar
// a tocar e evita picos de memória/travadas em arquivos grandes.
function tocarTS(video, url, fallback, loading){
  function falhar(){
    fallback.classList.add('show');
    loading.classList.remove('show');
  }

  if(!window.muxjs || !window.MediaSource){
    falhar();
    return;
  }

  const candidatos = [
    'video/mp4; codecs="avc1.64001f, mp4a.40.2"',
    'video/mp4; codecs="avc1.4d401f, mp4a.40.2"',
    'video/mp4; codecs="avc1.42e01e, mp4a.40.2"',
    'video/mp4; codecs="avc1.64001f"'
  ];
  const mime = candidatos.find(c => MediaSource.isTypeSupported(c));
  if(!mime){ falhar(); return; }

  loading.classList.add('show');

  const mediaSource = new MediaSource();
  // Buffer de segurança: mantém bastante mídia decodificável adiante para evitar engasgos
  mediaSource.addEventListener('sourceopen', function onOpen(){
    mediaSource.removeEventListener('sourceopen', onOpen);

    let sourceBuffer;
    try{
      sourceBuffer = mediaSource.addSourceBuffer(mime);
    }catch(e){ falhar(); return; }

    const fila = [];
    let leituraTerminada = false;
    let jaExibiuVideo = false;
    const ALVO_BUFFER_SEGUNDOS = 30; // quanto tentar manter "adiantado" antes de pausar novas leituras

    function concatenar(a, b){
      const out = new Uint8Array(a.byteLength + b.byteLength);
      out.set(a, 0); out.set(b, a.byteLength);
      return out;
    }

    function bufferAdiantadoSegundos(){
      if(!sourceBuffer.buffered.length) return 0;
      const fimBuffer = sourceBuffer.buffered.end(sourceBuffer.buffered.length - 1);
      return fimBuffer - (video.currentTime || 0);
    }

    function processarFila(){
      if(sourceBuffer.updating || fila.length === 0) return;
      const seg = fila.shift();
      try{ sourceBuffer.appendBuffer(seg); }
      catch(e){
        if(e && e.name === 'QuotaExceededError'){
          // memória cheia: espera o player consumir um pouco antes de tentar de novo
          fila.unshift(seg);
          setTimeout(processarFila, 500);
        } else {
          falhar();
        }
      }
    }

    sourceBuffer.addEventListener('updateend', function(){
      if(!jaExibiuVideo){ jaExibiuVideo = true; loading.classList.remove('show'); }
      if(leituraTerminada && fila.length === 0 && mediaSource.readyState === 'open'){
        try{ mediaSource.endOfStream(); }catch(e){}
      } else {
        processarFila();
        controlarLeitura();
      }
    });

    const transmuxer = new muxjs.mp4.Transmuxer();
    transmuxer.on('data', function(segmento){
      const dados = (segmento.initSegment && segmento.initSegment.byteLength)
        ? concatenar(segmento.initSegment, segmento.data)
        : segmento.data;
      fila.push(dados);
      processarFila();
    });
    transmuxer.on('done', function(){
      // "done" aqui é por flush parcial; o fim real do arquivo é sinalizado depois do loop de leitura
    });

    let controladorLeitura = null;
    function controlarLeitura(){
      if(controladorLeitura) controladorLeitura();
    }

    fetch(url).then(resposta => {
      if(!resposta.ok || !resposta.body) throw new Error('fetch falhou');
      const reader = resposta.body.getReader();
      let pausadoPorBuffer = false;

      function lerProximoPedaco(){
        if(bufferAdiantadoSegundos() > ALVO_BUFFER_SEGUNDOS){
          pausadoPorBuffer = true;
          return; // espera o 'updateend' chamar controlarLeitura() de novo
        }
        pausadoPorBuffer = false;
        reader.read().then(({ done, value }) => {
          if(done){
            leituraTerminada = true;
            transmuxer.flush();
            processarFila();
            return;
          }
          transmuxer.push(value);
          lerProximoPedaco();
        }).catch(falhar);
      }

      controladorLeitura = function(){
        if(pausadoPorBuffer) lerProximoPedaco();
      };

      lerProximoPedaco();
    }).catch(falhar);
  });

  video.src = URL.createObjectURL(mediaSource);
  video.addEventListener('error', falhar, { once:true });
}

iniciar();