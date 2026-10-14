#!/usr/bin/env python3
"""Genera il sito MondoSkills a partire da sorgenti/modello.html e dati.json.

Uso, dalla cartella principale del repository:
    python3 sorgenti/genera.py

Produce: index.html, stile.css, categoria/<nome>/index.html, 404.html, sitemap.xml.
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
{extra}<meta property="og:type" content="website">
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
                                     '<link rel="preload" href="/dati.json" as="fetch" crossorigin>\n'))
    t = t.replace('__NOSCRIPT__', nos).replace('__LINK_CATEGORIE__', link_categorie())
    t = t.replace('__TECHSY__', json.dumps(TECHSY, ensure_ascii=False)).replace('__AVVIO__', avvio)
    if not t.rstrip().endswith('</html>'):
        t = t.rstrip() + '\n</body>\n</html>\n'
    for segnaposto in ('__TESTA__', '__NOSCRIPT__', '__LINK_CATEGORIE__', '__TECHSY__', '__AVVIO__'):
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
    voci = [('/', '1.0')] + [(f'/categoria/{SLUG_CAT[c]}/', '0.8') for c in CATEGORIE]
    righe = ''.join(f'  <url><loc>{SITO}{p}</loc><lastmod>{AGGIORNATO}</lastmod><priority>{pr}</priority></url>\n'
                    for p, pr in voci)
    scrivi('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + righe + '</urlset>\n')
    return [SITO + p for p, _ in voci]


if __name__ == '__main__':
    shutil.copyfile(os.path.join(RADICE, 'sorgenti/stile-base.css'), os.path.join(RADICE, 'stile.css'))
    home()
    for c in CATEGORIE:
        categoria(c)
    errore404()
    urls = sitemap()
    print(f'Generate {len(urls)} pagine indicizzabili, 404.html e sitemap.xml')
