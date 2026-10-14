#!/usr/bin/env python3
"""Genera il sito MondoSkills a partire da sorgenti/modello.html e dati.json.

Uso, dalla cartella principale del repository:
    python3 sorgenti/genera.py

Produce: index.html, stile.css, consenso.js, categoria/<nome>/index.html, privacy/index.html,
404.html, sitemap.xml.
"""
import collections
import html
import json
import os
import re
import shutil
import unicodedata

SITO = 'https://mondoskills.it'
AGGIORNATO = '2026-10-14'
AGGIORNATO_ESTESO = '14 ottobre 2026'
# Statistiche con Google Analytics 4: si attivano solo se sono compilati entrambi i valori.
# GA4_ID è l'identificativo di misurazione (G-XXXXXXXXXX), EMAIL_PRIVACY l'indirizzo pubblicato
# nell'informativa per l'esercizio dei diritti. Con uno dei due vuoti il sito resta senza cookie.
GA4_ID = ''
EMAIL_PRIVACY = ''
STATISTICHE = bool(GA4_ID and EMAIL_PRIVACY)
assert not GA4_ID or re.fullmatch(r'G-[A-Z0-9]{4,16}', GA4_ID), 'GA4_ID non valido'
RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leggi(p):
    with open(os.path.join(RADICE, p), encoding='utf-8') as f:
        return f.read()


def scrivi(p, testo):
    p = os.path.join(RADICE, p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(testo)


def e(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def num(n):
    return f'{n:,}'.replace(',', '.')


def slug(s):
    s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def taglia(s, n):
    return s if len(s) <= n else s[:n - 1].rsplit(' ', 1)[0] + '…'


# ---------- dati ----------
D = json.loads(leggi('dati.json'))
H = D['h']
C = {k: H.index(v) for k, v in {
    'nome': 'Nome', 'desc': 'Descrizione di cosa fa', 'link': 'Link', 'cat': 'Categoria skill',
    'sub': 'Sottocategoria', 'piatt': 'Piattaforma', 'livello': 'Livello tecnico', 'costo': 'Costo',
    'lingua': 'Lingua della skill', 'ita': 'Contesto italiano', 'autore': 'Autore / editore'}.items()}
RIGHE = []
for r in D['rows']:
    RIGHE.append([(D['dict'][str(i)][v] if v >= 0 else None) if str(i) in D['dict'] else v
                  for i, v in enumerate(r)])
TOT = len(RIGHE)
PER_CAT = collections.defaultdict(list)
for i, r in enumerate(RIGHE):
    PER_CAT[r[C['cat']]].append(i)
CATEGORIE = sorted(PER_CAT, key=lambda c: -len(PER_CAT[c]))
SLUG_CAT = {c: slug(c) for c in CATEGORIE}
TECHSY = json.loads(leggi('sorgenti/techsy.json'))

MODELLO = leggi('sorgenti/modello.html')
TESTATA = MODELLO[MODELLO.index('<header'):MODELLO.index('</header>') + 9]
TESTATA_ESTERNA = re.sub(r'href="#', 'href="/#', TESTATA)
PIEDE = MODELLO[MODELLO.index('<footer>'):MODELLO.index('</footer>') + 9]
PIEDE_ESTERNO = PIEDE.replace('href="#catalogo"', 'href="/#catalogo"')

DESC_HOME = ('Catalogo gratuito di 7.600 skill per Claude e ChatGPT: filtri per categoria, piattaforma, '
             'costo e licenza, con il testo di installazione pronto da copiare.')
TITOLO_HOME = 'MondoSkills: catalogo di 7.600 skill per Claude e ChatGPT'
AUTORE = {'@type': 'Person', '@id': f'{SITO}/#autore', 'name': 'Guido Costalonga',
          'url': f'{SITO}/#chi-sono', 'sameAs': ['https://ginopizza.it/']}
SITO_LD = {'@type': 'WebSite', '@id': f'{SITO}/#sito', 'name': 'MondoSkills', 'url': f'{SITO}/',
           'inLanguage': 'it-IT', 'publisher': {'@id': f'{SITO}/#autore'}}


CONSENSO = f'<script src="/consenso.js" data-ga4="{GA4_ID}" defer></script>\n' if STATISTICHE else ''

if STATISTICHE:
    RIQUADRO_PRIVACY = f'''<div id="privacy"><h3>Privacy e cookie</h3>
        <p>MondoSkills usa Google Analytics 4 per contare le visite, <strong>solo se dai il consenso</strong> dall'avviso che compare alla prima visita. Niente pubblicità e niente profilazione. Se rifiuti, il sito funziona allo stesso modo e non salva alcun cookie di statistica.</p>
        <p>Puoi cambiare la tua scelta quando vuoi con <button type="button" class="piede-preferenze" data-consenso style="color:inherit">Preferenze cookie</button>. Tutti i dettagli sono nell'<a href="/privacy/">informativa sulla privacy e sui cookie</a>.</p></div>'''
else:
    RIQUADRO_PRIVACY = '''<div id="privacy"><h3>Privacy</h3>
        <p>MondoSkills non usa cookie, non usa strumenti di statistica o di profilazione e non raccoglie dati personali. Caratteri, immagini e dati sono ospitati sul sito stesso: la pagina non chiama servizi di terzi.</p>
        <p>Il sito è pubblicato con GitHub Pages: come indicato nell'<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">informativa di GitHub</a>, GitHub registra l'indirizzo IP dei visitatori per motivi di sicurezza. Il tasto «Copia» usa solo gli appunti del tuo dispositivo. <a href="/privacy/">Leggi l'informativa</a>.</p></div>'''


def testa(titolo, desc, percorso, ld, extra=''):
    url = SITO + percorso
    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titolo)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="author" content="Guido Costalonga">
<meta name="theme-color" content="#F2ACB9">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/caratteri/londrina-solid-900-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/caratteri/jost-400-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/caratteri/caratteri.css">
<link rel="stylesheet" href="/stile.css">
{CONSENSO}{extra}<meta property="og:type" content="website">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="MondoSkills">
<meta property="og:title" content="{e(titolo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITO}/anteprima.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="MondoSkills: trova la skill giusta. 7.600 skill per Claude e ChatGPT.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(titolo)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITO}/anteprima.jpg">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False)}</script>'''


def link_categorie(attuale=None):
    voci = ''.join(
        f'<li><a href="/categoria/{SLUG_CAT[c]}/"{" aria-current=\"page\"" if c == attuale else ""}>'
        f'{e(c)} ({num(len(PER_CAT[c]))})</a></li>' for c in CATEGORIE)
    return f'<ul>{voci}</ul>'


def pagina(titolo, desc, percorso, ld, corpo, extra=''):
    return ('<!doctype html>\n<html lang="it">\n<head>\n' + testa(titolo, desc, percorso, ld, extra) +
            '\n</head>\n<body>\n' + TESTATA_ESTERNA + '\n' + corpo + '\n' + PIEDE_ESTERNO + '\n</body>\n</html>\n')


# ---------- home ----------
def home():
    ld = [SITO_LD | {'description': DESC_HOME}, AUTORE, {
        '@type': 'Dataset', 'name': 'Catalogo MondoSkills delle skill per Claude e ChatGPT',
        'description': DESC_HOME, 'url': f'{SITO}/', 'inLanguage': 'it-IT',
        'creator': {'@id': f'{SITO}/#autore'}, 'dateModified': AGGIORNATO, 'isAccessibleForFree': True,
        'keywords': ['skill Claude', 'skill ChatGPT', 'Agent Skills', 'SKILL.md', 'GPT personalizzati',
                     'Claude Code', 'Codex', 'intelligenza artificiale'],
        'variableMeasured': ['Categoria', 'Sottocategoria', 'Piattaforma', 'Costo', 'Licenza',
                             'Destinatario', 'Livello tecnico'],
        'distribution': {'@type': 'DataDownload', 'encodingFormat': 'application/json',
                         'contentUrl': f'{SITO}/dati.json'}}]
    voci = ''.join(f'<li><a href="/categoria/{SLUG_CAT[c]}/">{e(c)}</a>: {num(len(PER_CAT[c]))} skill</li>'
                   for c in CATEGORIE)
    nos = (f'<noscript><section style="padding:24px 16px;max-width:900px;margin:0 auto;background:#fff">'
           f'<h2>MondoSkills: il catalogo delle skill per Claude e ChatGPT</h2>'
           f'<p>MondoSkills raccoglie {num(TOT)} skill e GPT personalizzati per Claude, ChatGPT, Codex e altri '
           f'assistenti, con categoria, destinatari, costo, licenza, compatibilità e il testo pronto da copiare '
           f'per installarli. Per usare la ricerca e i filtri serve JavaScript attivo nel browser; le pagine '
           f'delle categorie qui sotto funzionano anche senza.</p><h3>Le categorie</h3><ul>{voci}</ul>'
           f'<p>Dati aggiornati al {AGGIORNATO_ESTESO}.</p></section></noscript>')
    avvio = ("fetch('/dati.json').then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })"
             ".then(inizia).catch(() => { document.getElementById('griglia').innerHTML = "
             "'<div class=\"vuoto\" style=\"grid-column:1/-1\"><div><h3>Catalogo non caricato</h3>"
             "<p>Non sono riuscito a caricare le skill. Ricarica la pagina; se il problema resta, "
             "apri le pagine delle categorie qui sopra.</p></div></div>'; });")
    t = MODELLO
    t = t.replace('__TESTA__', testa(TITOLO_HOME, DESC_HOME, '/', ld,
                                     '<link rel="preload" href="/logo.png" as="image" fetchpriority="high">\n'
                                     '<link rel="preload" href="/dati.json" as="fetch" crossorigin>\n'))
    t = t.replace('__PRIVACY__', RIQUADRO_PRIVACY)
    t = t.replace('__NOSCRIPT__', nos).replace('__LINK_CATEGORIE__', link_categorie())
    t = t.replace('__TECHSY__', json.dumps(TECHSY, ensure_ascii=False)).replace('__AVVIO__', avvio)
    if not t.rstrip().endswith('</html>'):
        t = t.rstrip() + '\n</body>\n</html>\n'
    for segnaposto in ('__TESTA__', '__PRIVACY__', '__NOSCRIPT__', '__LINK_CATEGORIE__', '__TECHSY__', '__AVVIO__'):
        assert segnaposto not in t, segnaposto
    scrivi('index.html', t)


# ---------- pagine di categoria ----------
def scheda(i):
    r = RIGHE[i]
    etich = [r[C['piatt']], r[C['livello']], r[C['costo']], re.sub(r' \(.*\)', '', r[C['lingua']] or '')]
    if r[C['ita']] == 'Sì':
        etich.append('Contesto italiano')
    eti = ''.join(f'<span class="etichetta{" etichetta--piena" if k == 0 else ""}">{e(x)}</span>'
                  for k, x in enumerate(etich) if x)
    return (f'<li class="voce-skill"><h3>{e(r[C["nome"]])}</h3><p>{e(r[C["desc"]])}</p>'
            f'<div class="etichette">{eti}</div><div class="azioni">'
            f'<a class="pieno" href="/?skill={i}">Scheda e installazione</a>'
            f'<a href="{e(r[C["link"]])}" rel="noopener" target="_blank">Fonte</a></div></li>')


def categoria(c):
    idx = PER_CAT[c]
    n = len(idx)
    per_sub = collections.defaultdict(list)
    for i in idx:
        per_sub[RIGHE[i][C['sub']]].append(i)
    subs = sorted(per_sub, key=lambda s: (-len(per_sub[s]), s))
    gratis = sum(1 for i in idx if (RIGHE[i][C['costo']] or '').startswith('Gratuita'))
    claude = sum(1 for i in idx if 'Claude' in (RIGHE[i][C['piatt']] or '') or 'Altri agenti' in (RIGHE[i][C['piatt']] or ''))
    chatgpt = sum(1 for i in idx if (RIGHE[i][H.index('Compatibile con ChatGPT')] == 'Sì'))
    ita = sum(1 for i in idx if (RIGHE[i][C['ita']] == 'Sì'))
    sl = SLUG_CAT[c]
    titolo = f'{c}: {num(n)} skill per Claude e ChatGPT | MondoSkills'
    tre = ', '.join(s.lower() if not s[:2].isupper() else s for s in subs[:3])
    desc = taglia(f'{num(n)} skill per Claude e ChatGPT nella categoria {c}: {tre}. '
                  f'Per ognuna fonte, costo, licenza e testo di installazione.', 158)
    def v(k, uno, piu):
        return f'{num(k)} {uno if k == 1 else piu}'
    parti = [v(claude, 'funziona con Claude', 'funzionano con Claude'),
             v(chatgpt, 'è compatibile con ChatGPT', 'sono compatibili con ChatGPT'),
             v(gratis, 'è gratuita', 'sono gratuite')]
    if ita:
        parti.append(v(ita, 'riguarda norme o prassi italiane', 'riguardano norme o prassi italiane'))
    sottocat = 'una sola sottocategoria' if len(subs) == 1 else f'{len(subs)} sottocategorie'
    tutte = 'l\'unica skill' if n == 1 else f'tutte le <strong>{num(n)} skill</strong>'
    intro = (f'In questa pagina trovi {tutte} della categoria {e(c)}, divise in {sottocat}. '
             + ', '.join(parti[:-1]) + ' e ' + parti[-1] + '. '
             'Per ogni skill trovi la fonte originale e, nella scheda, il testo pronto da copiare per installarla.')
    indice = ''.join(f'<li><a href="#{slug(s)}">{e(s)} ({num(len(per_sub[s]))})</a></li>' for s in subs)
    gruppi = ''.join(
        f'<section class="gruppo-cat gutter" id="{slug(s)}"><div class="interno"><h2>{e(s)}</h2>'
        f'<p>{num(len(per_sub[s]))} skill</p><ul class="elenco">'
        + ''.join(scheda(i) for i in sorted(per_sub[s], key=lambda i: str(RIGHE[i][C['nome']]).lower()))
        + '</ul></div></section>' for s in subs)
    corpo = f'''<main>
<section class="apertura cat-apertura gutter"><div class="interno testa">
  <p class="briciole"><a href="/">MondoSkills</a> › <a href="/#categorie">Categorie</a> › {e(c)}</p>
  <h1>{e(c)}</h1>
  <p class="sottotitolo">{num(n)} skill per Claude e ChatGPT</p>
  <p class="cat-intro">{intro}</p>
  <a class="grosso" href="/?categoria={e(c)}">Filtra nel catalogo completo</a>
  <ul class="indice">{indice}</ul>
</div></section>
{gruppi}
<section class="sezione sezione--scura gutter altre-cat"><div class="interno"><nav class="pagine-cat" aria-label="Altre categorie" style="border:0;margin:0;padding:0"><h3>Le altre categorie</h3>{link_categorie(c)}</nav>
<p class="sezione__nota" style="margin-top:22px">Dati aggiornati al {AGGIORNATO_ESTESO}. MondoSkills è un archivio di skill pubblicate da altri: <a href="/#avvertenze">leggi le avvertenze</a>.</p></div></section>
</main>'''
    ld = [SITO_LD, AUTORE,
          {'@type': 'CollectionPage', 'name': titolo, 'description': desc, 'url': f'{SITO}/categoria/{sl}/',
           'inLanguage': 'it-IT', 'isPartOf': {'@id': f'{SITO}/#sito'}, 'dateModified': AGGIORNATO,
           'about': c, 'numberOfItems': n},
          {'@type': 'BreadcrumbList', 'itemListElement': [
              {'@type': 'ListItem', 'position': 1, 'name': 'MondoSkills', 'item': f'{SITO}/'},
              {'@type': 'ListItem', 'position': 2, 'name': 'Categorie', 'item': f'{SITO}/#categorie'},
              {'@type': 'ListItem', 'position': 3, 'name': c, 'item': f'{SITO}/categoria/{sl}/'}]}]
    scrivi(f'categoria/{sl}/index.html', pagina(titolo, desc, f'/categoria/{sl}/', ld, corpo))


# ---------- privacy ----------
def privacy():
    hosting = ('<p>Il sito è pubblicato con GitHub Pages, servizio di GitHub, Inc. Come indicato nell\'<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">informativa di GitHub</a>, '
               'GitHub registra l\'indirizzo IP dei visitatori per motivi di sicurezza del servizio. Caratteri, immagini e dati del catalogo sono ospitati sul sito stesso. '
               'Il tasto «Copia» usa solo gli appunti del tuo dispositivo e non invia nulla.</p>')
    if not STATISTICHE:
        testo = f'''<h2>In breve</h2>
<p>MondoSkills non usa cookie, non usa strumenti di statistica o di profilazione e non raccoglie dati personali.</p>
<h2>Pubblicazione del sito</h2>
{hosting}
<p>Per segnalazioni puoi usare la <a href="https://github.com/GuidoCostalonga/mondoskills/issues/new">pagina delle segnalazioni</a> del progetto.</p>'''
    else:
        testo = f'''<h2>In breve</h2>
<ul>
<li>Uso <strong>Google Analytics 4</strong> per contare le visite e capire quali pagine sono più utili, <strong>solo se dai il consenso</strong>.</li>
<li>Prima del tuo «sì» non viene salvato alcun cookie di statistica e non viene caricato alcun codice di Google.</li>
<li>Niente pubblicità, niente profilazione, nessuna vendita di dati.</li>
<li>Puoi cambiare idea in ogni momento: <button type="button" class="piede-preferenze" data-consenso style="color:inherit">apri le preferenze cookie</button>.</li>
</ul>

<h2>1. Titolare del trattamento</h2>
<p>Guido Costalonga, Roveredo in Piano (Pordenone). Per qualsiasi richiesta sulla privacy scrivi a <a href="mailto:{e(EMAIL_PRIVACY)}">{e(EMAIL_PRIVACY)}</a>.</p>

<h2>2. Quali dati e perché</h2>
<p><strong>Dati di navigazione.</strong> {hosting[3:-4]}</p>
<p><strong>Statistiche di visita, solo con il tuo consenso.</strong> Google Analytics 4 raccoglie: un identificativo casuale salvato nei cookie, le pagine visitate e il tempo di permanenza, la pagina di provenienza, il tipo di dispositivo, il sistema operativo e il programma di navigazione, la lingua, il paese e la città approssimativa ricavati dall'indirizzo IP. Secondo Google, Google Analytics 4 non registra e non conserva gli indirizzi IP. Uso questi dati solo in forma aggregata, per sapere quante persone visitano il sito e quali contenuti servono di più.</p>
<p>Ho disattivato Google Signals e la personalizzazione degli annunci: i dati non servono a fini pubblicitari e non vengono collegati al tuo eventuale account Google.</p>

<h2>3. Base giuridica</h2>
<p>Il tuo consenso, ai sensi dell'articolo 6, paragrafo 1, lettera a), del RGPD (Regolamento generale sulla protezione dei dati, Regolamento UE 2016/679) e dell'articolo 122 del Codice in materia di protezione dei dati personali (decreto legislativo 30 giugno 2003, n. 196). Il consenso è facoltativo: se rifiuti, il sito funziona allo stesso modo.</p>

<h2>4. Cookie e strumenti usati</h2>
<div class="tabella-scorre"><table>
<thead><tr><th>Nome</th><th>Fornitore</th><th>A cosa serve</th><th>Durata</th><th>Consenso</th></tr></thead>
<tbody>
<tr><td><code>ms-consenso</code> (memoria locale del programma di navigazione)</td><td>MondoSkills</td><td>Ricorda la tua scelta sull'avviso, per non riproportelo a ogni pagina</td><td>6 mesi</td><td>Non serve: è tecnico</td></tr>
<tr><td><code>_ga</code></td><td>Google</td><td>Distingue i visitatori con un identificativo casuale</td><td>6 mesi</td><td>Sì</td></tr>
<tr><td><code>_ga_{e(GA4_ID[2:])}</code></td><td>Google</td><td>Conserva lo stato della visita in corso</td><td>6 mesi</td><td>Sì</td></tr>
</tbody></table></div>
<p>Dopo 6 mesi l'avviso ti viene riproposto, sia che tu abbia accettato sia che tu abbia rifiutato.</p>

<h2>5. Chi riceve i dati</h2>
<p>Google Ireland Limited, Gordon House, Barrow Street, Dublino 4, Irlanda, che fornisce Google Analytics come responsabile del trattamento. I dati possono essere trasferiti negli Stati Uniti a Google LLC, che aderisce al Quadro UE USA per la protezione dei dati personali (EU U.S. Data Privacy Framework), riconosciuto adeguato dalla Commissione europea con la decisione di esecuzione (UE) 2023/1795 del 10 luglio 2023. Informazioni di Google: <a href="https://policies.google.com/privacy?hl=it">informativa sulla privacy</a> e <a href="https://policies.google.com/technologies/partner-sites?hl=it">uso dei dati sui siti che usano i servizi Google</a>.</p>
<p>Non cedo né vendo i dati a nessuno.</p>

<h2>6. Per quanto tempo</h2>
<p>I dati di Google Analytics collegati all'identificativo del visitatore sono conservati per <strong>2 mesi</strong>, poi vengono cancellati automaticamente; restano solo i totali aggregati e anonimi. I cookie durano al massimo 6 mesi.</p>

<h2>7. I tuoi diritti</h2>
<p>Puoi chiedere in ogni momento l'accesso ai tuoi dati, la rettifica, la cancellazione, la limitazione del trattamento, la portabilità e opporti al trattamento (articoli dal 15 al 22 del RGPD), scrivendo a <a href="mailto:{e(EMAIL_PRIVACY)}">{e(EMAIL_PRIVACY)}</a>. Puoi revocare il consenso quando vuoi dalle <button type="button" class="piede-preferenze" data-consenso style="color:inherit">preferenze cookie</button>: la revoca non rende illecito quanto fatto prima (articolo 7, paragrafo 3, del RGPD). Se ritieni che i tuoi dati siano trattati in modo non corretto, puoi presentare reclamo al <a href="https://www.garanteprivacy.it/">Garante per la protezione dei dati personali</a> (articolo 77 del RGPD).</p>
<p>Puoi anche bloccare Google Analytics su tutti i siti con il <a href="https://tools.google.com/dlpage/gaoptout?hl=it">componente aggiuntivo di Google</a> per il programma di navigazione.</p>'''
    corpo = f'''<main>
<section class="apertura cat-apertura gutter"><div class="interno testa">
  <p class="briciole"><a href="/">MondoSkills</a> › Privacy</p>
  <h1>Privacy e cookie</h1>
  <p class="sottotitolo">Informativa ai sensi dell'articolo 13 del RGPD</p>
</div></section>
<section class="testo-legale gutter"><div class="interno">
{testo}
<p class="sezione__nota" style="margin-top:28px">Ultimo aggiornamento: {AGGIORNATO_ESTESO}.</p>
</div></section>
</main>'''
    titolo = 'Privacy e cookie | MondoSkills'
    desc = 'Informativa sulla privacy e sui cookie di MondoSkills: quali dati raccoglie il sito, perché e come cambiare le tue scelte.'
    ld = [SITO_LD, {'@type': 'WebPage', 'name': titolo, 'description': desc, 'url': f'{SITO}/privacy/',
                    'inLanguage': 'it-IT', 'isPartOf': {'@id': f'{SITO}/#sito'}, 'dateModified': AGGIORNATO}]
    scrivi('privacy/index.html', pagina(titolo, desc, '/privacy/', ld, corpo))


def errore404():
    corpo = f'''<main>
<section class="apertura errore404 gutter"><div class="interno testa">
  <span class="aggiornato">Errore 404</span>
  <h1>Questa pagina non c'è</h1>
  <p class="sottotitolo">Ma le skill sì</p>
  <p class="sotto">L'indirizzo che hai aperto non esiste o è stato spostato. Riparti dal catalogo completo oppure da una categoria.</p>
  <a class="grosso" href="/">Torna al catalogo</a>
</div></section>
<section class="sezione sezione--scura gutter"><div class="interno"><nav class="pagine-cat" style="border:0;margin:0;padding:0" aria-label="Categorie"><h3>Le categorie</h3>{link_categorie()}</nav></div></section>
</main>'''
    t = pagina('Pagina non trovata | MondoSkills', 'Questa pagina di MondoSkills non esiste.', '/404.html', [SITO_LD], corpo)
    t = t.replace('content="index, follow, max-image-preview:large, max-snippet:-1"', 'content="noindex"')
    scrivi('404.html', t)


def sitemap():
    voci = ([('/', '1.0')] + [(f'/categoria/{SLUG_CAT[c]}/', '0.8') for c in CATEGORIE]
            + [('/privacy/', '0.3')])
    righe = ''.join(f'  <url><loc>{SITO}{p}</loc><lastmod>{AGGIORNATO}</lastmod><priority>{pr}</priority></url>\n'
                    for p, pr in voci)
    scrivi('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + righe + '</urlset>\n')
    return [SITO + p for p, _ in voci]


if __name__ == '__main__':
    shutil.copyfile(os.path.join(RADICE, 'sorgenti/stile-base.css'), os.path.join(RADICE, 'stile.css'))
    shutil.copyfile(os.path.join(RADICE, 'sorgenti/consenso.js'), os.path.join(RADICE, 'consenso.js'))
    home()
    for c in CATEGORIE:
        categoria(c)
    privacy()
    errore404()
    urls = sitemap()
    print(f'Generate {len(urls)} pagine indicizzabili, 404.html e sitemap.xml')
