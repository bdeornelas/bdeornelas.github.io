# Cardiologia Divulgativa

Sito web di informazione medica cardiologica per pazienti, con articoli evidence-based e linguaggio accessibile.

🌐 **[bdeornelas.github.io](https://bdeornelas.github.io)**

## Descrizione

Repository del sito di cardiologia divulgativa contenente oltre 40 articoli medici su:
- Patologie cardiovascolari (infarto, fibrillazione atriale, scompenso cardiaco, etc.)
- Esami diagnostici (ECG, ecocardiogramma, test ergometrico, etc.)
- Prevenzione cardiovascolare (colesterolo, ipertensione, dieta mediterranea, etc.)
- Valvulopatie e aritmie

Tutti gli articoli seguono le linee guida ESC (European Society of Cardiology) più recenti e sono scritti con approccio divulgativo per rendere accessibili concetti medici complessi.

## Tecnologie

- **Static Site Generator**: Jekyll
- **Styling**: Tailwind CSS + custom CSS
- **Hosting**: GitHub Pages / Vercel
- **Analytics**: Privacy-first analytics

## Struttura Repository

```
bdeornelas.github.io/
├── _articles/              # Articoli Markdown (45+ articoli)
├── _includes/              # Componenti HTML riutilizzabili (header, footer)
├── _layouts/               # Layout Jekyll (default, article)
├── articles/               # Directory articoli compilati
├── assets/
│   ├── css/                # Tailwind e custom CSS
│   └── js/                 # Script frontend
├── about/                  # Pagina Chi Sono
├── contact/                # Pagina Contatti
├── privacy/                # Privacy Policy
├── cookie-policy/          # Cookie Policy
├── research/               # Sezione ricerca medica
├── scripts/                # Script Python di utility
├── docs-internal/          # Documentazione interna sviluppo
├── prototypes/             # Prototipi HTML (non in produzione)
└── references/             # Linee guida ESC e materiale di riferimento
```

## Setup Locale

### Requisiti
- Ruby 3.x
- Node.js 18+
- Jekyll 4.x

### Installazione

```bash
# Clone repository
git clone https://github.com/bdeornelas/bdeornelas.github.io.git
cd bdeornelas.github.io

# Install Ruby dependencies
bundle install

# Install Node.js dependencies
npm install

# Build CSS
npm run build:css

# Run Jekyll development server
bundle exec jekyll serve
```

Il sito sarà disponibile su `http://localhost:4000`

## Development Scripts

```bash
# Build Tailwind CSS (minified)
npm run build:css

# Build Tailwind CSS (development)
npm run dev:css

# Watch CSS changes
npm run watch:css

# Build per produzione
bundle exec jekyll build
```

## Deployment

Il sito è configurato per deploy automatico su:
- **GitHub Pages** (branch main)
- **Vercel** (con configurazione custom)

### Deploy Vercel
```bash
vercel --prod
```

## Content Management

### Aggiungere un Nuovo Articolo

1. Crea un file Markdown in `_articles/`:
```markdown
---
layout: article
title: "Titolo Articolo"
description: "Breve descrizione per SEO"
date: 2024-01-15
---

Contenuto articolo...
```

2. Build e verifica in locale
3. Commit e push

### Linee Guida Editoriali

- Seguire le **ESC Guidelines** più recenti
- Linguaggio divulgativo ma scientificamente accurato
- Riferimenti bibliografici quando appropriato
- Consultare `docs-internal/GUIDA-STILE-DIVULGATIVO-MEDICO.md`

## SEO & Analytics

- Sitemap automatico: `sitemap.xml`
- Robots.txt configurato
- Meta tags ottimizzati per ogni articolo
- Schema.org markup per articoli medici

## Utility Scripts

Located in `/scripts/`:
- `seo_audit.py` - SEO audit automatizzato
- `word_count_articles.py` - Conteggio parole articoli
- Altri script di analisi contenuti

## Materiale di Riferimento

Le **Linee Guida ESC** (European Society of Cardiology) 2020-2025 sono archiviate localmente in `references/esc-guidelines/` per consultazione durante la scrittura degli articoli.

## Note di Sviluppo

- `docs-internal/` contiene documentazione di sviluppo, piani implementazione, analisi
- `prototypes/` contiene esperimenti HTML non in produzione
- `references/` contiene materiale medico di riferimento (escluso da Git)

## License

MIT License - vedi [LICENSE](LICENSE)

## Contatti

Per segnalazioni o collaborazioni: [Modulo Contatti](https://bdeornelas.github.io/contact/)
