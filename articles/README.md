# Linee guida articoli (stile allineato)

Queste indicazioni garantiscono che i nuovi articoli rispettino lo stesso stile/struttura degli articoli già pubblicati.

## Struttura dei file
- Ogni articolo in una propria cartella con `index.html`, es.: `articles/infarto-miocardico/index.html`.
- Front matter Jekyll in testa, con: `layout`, `title`, `description`, `og_*`.
- Usa il template pronto: `articles/_template/index.html`.

## Come creare un nuovo articolo
1) Copia la cartella `articles/_template` e rinominala, es.: `articles/fibrillazione-atriale`.
2) Apri `articles/fibrillazione-atriale/index.html` e aggiorna:
   - Front matter: `title`, `description`, `og_title`, `og_description`.
   - Breadcrumb: ultimo elemento (sottotitolo breve).
   - Hero: etichetta categoria (testo e colore), titolo su due righe, intro, metadati (data, lettura, tag).
   - Sezioni H2 con icona lucide: mantieni lo stesso pattern (icona + colore coerente).
   - Box: `highlight-box`, `warning-box`, `info-step` già stilizzati inline come negli articoli esistenti.
   - Disclaimer finale obbligatorio.

Suggerimenti colori per coerenza:
- Prevenzione: sky/emerald
- Diagnostica: violet/sky
- Ipertensione/arterie: pink/orange
- Valvole: violet
- Aritmie: pink/violet

## Aggiornare la lista in `articles/index.html`
- Aggiungi un nuovo `<li>` copiando uno già presente e modifica:
  - `href`: link alla cartella dell’articolo
  - Bordo/colore e icona coerenti con la categoria
  - Titolo, descrizione breve, data, tempo di lettura, tag

Esempio snippet list item:

```html
<li>
  <a href="/articles/slug-articolo/" class="block px-6 py-4 rounded-lg glass-card border-l-4 border-sky-400 hover:border-sky-300 hover:bg-slate-800/50 transition group">
    <div class="flex items-center gap-3">
      <i data-lucide="heart" class="w-5 h-5 text-sky-400 group-hover:text-sky-300"></i>
      <div>
        <h3 class="font-bold text-white group-hover:text-sky-100">Titolo Articolo</h3>
        <p class="text-sm text-slate-400 mt-1">Descrizione breve (1 riga)</p>
        <div class="flex items-center gap-4 mt-2 text-xs text-slate-500">
          <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3 h-3"></i> 20 ottobre 2025</span>
          <span class="flex items-center gap-1"><i data-lucide="clock" class="w-3 h-3"></i> 9 min lettura</span>
          <span class="flex items-center gap-1"><i data-lucide="tag" class="w-3 h-3"></i> Tag1, Tag2</span>
        </div>
      </div>
    </div>
  </a>
  </li>
```

## Tono e contenuti
- Linguaggio accessibile (B1–B2), empatico, non allarmistico.
- Struttura coerente: definizione → cause → sintomi → diagnosi → terapie → prevenzione → quando chiamare 118 → messaggio finale → disclaimer.
- Evita tecnicismi non necessari; quando servono, spiega in breve.

## QA rapido
- Titolo H1 su due righe con `gradient-text`.
- Sezioni con H2 + icona lucide e colori coerenti.
- `glass-card` per hero e corpo.
- Box `highlight-box`/`warning-box`/`info-step` presenti dove utili.
- Breadcrumb, data, tempo lettura, tag compilati.
- Disclaimer presente a fondo pagina.
