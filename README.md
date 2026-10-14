# MondoSkills.it

Catalogo di 7.600 skill per Claude e ChatGPT, con filtri su ogni colonna e il testo di installazione da copiare.
Pubblicato con GitHub Pages sul dominio https://mondoskills.it.

## Struttura

| Percorso | Contenuto |
|---|---|
| `index.html` | Pagina principale con ricerca e filtri (generata) |
| `dati.json` | Le 7.600 skill, caricate dalla pagina principale |
| `categoria/<nome>/` | Una pagina statica per ciascuna delle 26 categorie (generate) |
| `404.html`, `sitemap.xml` | Pagina di errore e mappa del sito (generate) |
| `stile.css`, `caratteri/`, `logo.png`, `sigillo.png` | Grafica; i caratteri sono ospitati sul sito |
| `sorgenti/modello.html`, `sorgenti/stile-base.css` | Modello della pagina principale e foglio di stile |
| `sorgenti/genera.py` | Generatore del sito |
| `sorgenti/techsy.json` | Pagine delle singole skill di Techsy, per i testi di installazione |

## Aggiornare il sito

1. Sostituisci `dati.json` con i dati nuovi (stesso formato).
2. Aggiorna le date in `sorgenti/genera.py` (`AGGIORNATO` e `AGGIORNATO_ESTESO`).
3. Esegui `python3 sorgenti/genera.py` dalla cartella principale.
4. Pubblica le modifiche sul ramo `main`.

I caratteri Jost, Londrina Solid e JetBrains Mono sono distribuiti con licenza SIL Open Font License 1.1.

MondoSkills è un archivio: raccoglie skill pubblicate da altri, con il collegamento alla fonte originale.
