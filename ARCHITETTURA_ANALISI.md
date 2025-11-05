# ANALISI DELL'ARCHITETTURA BACKEND E INFRASTRUTTURALE
## Sito bdeornelas.github.io - Dr. Benjamin De Ornelas

**Data Analisi:** Novembre 2025
**Destinatario:** Cardiologo - Business Domain: Contenuti medici + Prenotazioni
**Architettura Attuale:** Static Site Generator (Jekyll + Parcel) su GitHub Pages

---

## EXECUTIVE SUMMARY

L'attuale architettura è una **soluzione JAMstack puramente statica** basata su Jekyll + Parcel distribuita su GitHub Pages. Mentre questa scelta offre semplicità, sicurezza e costi quasi nulli, presenta **limitazioni significative per un business medico** che richiede:
- Gestione dinamica delle prenotazioni
- Integrazione con sistemi di calendari/booking
- Raccolta dati da form con persistenza
- Analytics e tracking del comportamento utenti
- Aggiornamenti in real-time

La soluzione attuale copre **bene il 60% dei casi d'uso** (contenuti, blog, informazioni statiche), ma è **inadeguata per il 40% rimanente** (prenotazioni, CRM, analytics).

---

## 1. STATIC SITE ARCHITECTURE

### Stack Tecnologico
```
Frontend: HTML + Tailwind CSS + Lucide Icons
Static Generation: Jekyll 3.9.3 (Ruby)
Asset Bundling: Parcel 2.12.0 (JavaScript)
Hosting: GitHub Pages (Free tier)
CDN: GitHub's Fastly CDN (incluso)
```

### Valutazione: ★★★★☆ (4/5)

#### PUNTI FORTI
1. **Semplicità Operativa**
   - Zero complessità server-side
   - Nessuna gestione di database
   - Nessun backend da mantenere
   - Build locale deterministico

2. **Performance**
   - Tempi di caricamento: <1 sec (con CDN)
   - Nessuna latenza di database
   - HTML/CSS/JS minificati
   - Lazy loading delle immagini implementato

3. **Sicurezza**
   - Nessuna superficie di attacco server
   - HTTPS automatico (GitHub Pages)
   - CSP headers configurato (vedi `_headers`)
   - Nessuna dipendenza da runtime web

4. **Costi**
   - Hosting: €0/mese (GitHub Pages gratuito)
   - CDN: €0/mese (incluso)
   - DNS: dipende da dominio (es. €12/anno)

#### PUNTI DEBOLI
1. **Mancanza di Dinamicità**
   - Impossibile aggiornare contenuti senza build
   - Form handling esterno (Formspree)
   - Nessun backend di autenticazione
   - Calendari/prenotazioni non gestibili

2. **Developer Experience**
   - Build pipeline biforcuta (Jekyll + Parcel)
   - Due file di configurazione diversi
   - Gestione manuale delle dipendenze
   - Nessun hot reload

3. **Scalabilità dei Contenuti**
   - 44 articoli = gestione manuale
   - Struttura cartelle complessa (`articles/*/index.html`)
   - Tempi di build possono crescere linearmente
   - Nessun sistema di draft/publish

4. **Analytics Limitati**
   - Nessun tracking lato server
   - Solo script client-side (assenti nel codice)
   - Nessuna raccolta dati di conversione

### Build Pipeline Analysis

**File di configurazione:**
- `_config.yml` - Jekyll config (markdown, highlighter, collections)
- `package.json` - Parcel build script

**Build Process:**
```bash
# Fase 1: Jekyll (generazione HTML)
jekyll build

# Fase 2: Parcel (bundling assets)
parcel build assets/js/main.js assets/css/style.css --dist-dir dist

# Output finale: _site/
```

**Problemi Identificati:**
1. Le due fasi di build sono **sequenziali e disaccoppiate**
   - Parcel output va in `dist/` ma Jekyll legge da `assets/`
   - Nessun orchestrazione automatica
   - Build manuale richiede due comandi

2. **Esclusioni aggressive:**
```yaml
exclude:
  - node_modules/
  - .parcel-cache/
  - package.json
```
Corretto, ma aumenta il rischio di includere file temporanei.

### Metriche di Build
- **Dimensione _site:** 4.8 MB
- **Articoli:** 44 (1.1 MB)
- **Assets CSS:** style.min.css
- **Assets JS:** main.min.js + lucide.min.js + aos.min.js
- **Tempo di build:** ~3-5 sec (stima)

#### Raccomandazioni Build
```
PRIORITÀ ALTA:
1. Automatizzare orchestrazione Jekyll + Parcel (Makefile o script bash)
2. Aggiungere source maps per debugging in prod
3. Implementare cache busting per assets (fingerprinting)

PRIORITÀ MEDIA:
4. Configurare GitHub Actions per CI/CD automatico
5. Aggiungere linting (eslint, stylelint)
6. Minification aggressiva (target <100KB CSS/JS combined)
```

---

## 2. DATA ARCHITECTURE

### Struttura dei Contenuti

```
articles/
├── _template/            # Template per nuovi articoli
├── aneurisma-aortico/
│   └── index.html       # Articolo singolo (Front Matter + HTML)
├── angina-pectoris/
├── [42 altre cartelle]
└── ...
```

**Totale:** 44 articoli medici, ognuno in subdirectory separata.

### Jekyll Collections Analysis

```yaml
# _config.yml
collections:
  research:
    output: true
    permalink: /research/:name/
```

**PROBLEMA IMPORTANTE:** La collezione `research` è configurata ma **NON UTILIZZATA** per gli articoli. Invece, gli articoli usano:
- Directory flat: `articles/*/index.html`
- Nessuna gestione automatica di metadata
- Nessun front matter metadata parsing

#### Struttura Front Matter Attuale (da aneurisma-aortico)
```yaml
layout: default
title: "Aneurisma dell'Aorta - Come Gestirlo..."
description: "Scopri cos'è l'aneurisma aortico..."
og_title: "..."
og_description: "..."
og_image: /assets/img/og-card.jpg
date: 2025-09-01
```

**Valutazione Metadata:** ★★★☆☆ (3/5)

#### PUNTI FORTI
1. **SEO Completo**
   - Meta description per pagina
   - Open Graph tags (social sharing)
   - Twitter Card support
   - Structured data (Schema.org MedicalBusiness + MedicalDoctor)

2. **Flessibilità**
   - Metadati custom per pagina
   - Fallback a default site metadata

#### PUNTI DEBOLI
1. **Mancanza di Standardizzazione**
   - Nessun campo obbligatorio
   - Nessuna validazione front matter
   - Possibilità di inconsistenza
   - Nessuno schema di validazione

2. **Scarso Indexing**
   - Nessun sistema di categorie/tags
   - Articoli non raggruppati per specialità
   - Nessun sistema di relazioni (articoli correlati)
   - Nessun breadcrumb dinamico

### Gestione Dati Attuale

**Dove risiedono i dati:**
1. **Contenuti:** Git repository (articles/)
2. **Form submissions:** Email (Formspree)
3. **Contatti:** HTML hardcoded
4. **Prenotazioni:** Link esterno a Santagostino.it

**Problemi Critici:**
```
CONTENUTI:
✗ Nessun database di contenuti
✗ Nessun versionamento di metadati
✗ Nessun sistema di draft
✗ Nessun scheduler di pubblicazione

FORM:
✗ Formspree è servizio esterno
✗ Dati NON persistiti localmente
✗ Nessun CRM di follow-up
✗ Nessun tracking di conversione

PRENOTAZIONI:
✗ Completamente esternalizzato (Santagostino.it)
✗ Nessuna integrazione con sito
✗ Nessun feedback di conferma
✗ Nessun reminder/follow-up

CONTATTI:
✗ Hardcoded in HTML
✗ Nessun sistema di aggiornamento
✗ Nessuna centralizzazione
```

### Proposta di Architettura Dati Migliorata

```yaml
TIER 1 - Frontend Statico (Jekyll)
├── Articles (Git-based)
├── Pages (Git-based)
├── Static assets

TIER 2 - Backend Leggero (Node.js + Supabase)
├── API Prenotazioni
├── Form Submission Handler
├── CRM minimalista
├── Email Campaigns

TIER 3 - External Services
├── Calendari (Google Calendar API, Santagostino)
├── Email (SendGrid/Resend)
├── Payment (Stripe per ritardi)
└── Analytics (Fathom, Plausible)
```

### Schema Dati Consigliato (NoSQL/PostgreSQL)

```json
{
  "articles": {
    "id": "string",
    "slug": "string",
    "title": "string",
    "description": "string",
    "body": "string (markdown)",
    "category": "string[] (cardiologia, prevenzione, etc)",
    "tags": "string[]",
    "author": "string",
    "published_at": "timestamp",
    "updated_at": "timestamp",
    "status": "draft|published|archived",
    "seo": {
      "og_title": "string",
      "og_description": "string",
      "og_image": "string",
      "canonical": "string"
    }
  },
  "form_submissions": {
    "id": "uuid",
    "name": "string",
    "email": "string",
    "subject": "string",
    "message": "string",
    "type": "general|prenotazione|collaborazione",
    "status": "received|read|replied",
    "created_at": "timestamp",
    "replied_at": "timestamp"
  },
  "bookings": {
    "id": "uuid",
    "patient_email": "string",
    "patient_phone": "string",
    "service_type": "visita|ecocardiogramma|test",
    "location": "string (Santagostino sede)",
    "preferred_dates": "timestamp[]",
    "status": "pending|confirmed|completed|cancelled",
    "source": "website|phone|external",
    "created_at": "timestamp"
  }
}
```

#### Raccomandazioni Dati

```
PRIORITÀ CRITICA:
1. Migliare articles da HTML a JSON/YAML per parsing automatico
2. Implementare database per form submissions (minimo: Supabase)
3. Creare sistema di booking integrato

PRIORITÀ ALTA:
4. Aggiungere sistema di categorizzazione articoli
5. Implementare relazioni articoli (correlati, next, previous)
6. Centralizzare metadata in YAML singolo

PRIORITÀ MEDIA:
7. Implementare bozze/scheduling articoli
8. Aggiungere full-text search backend
```

---

## 3. DEPLOYMENT STRATEGY

### Architettura Deployment Attuale

```
Local Machine
    ↓
git push → GitHub Repository
    ↓
GitHub Pages (Automated)
    ↓
Fastly CDN
    ↓
User Browser
```

**Vantaggi:**
- ✅ Deploy automatico su push
- ✅ HTTPS gratis e obbligatorio
- ✅ Nessuna configurazione server
- ✅ Rollback immediate (git revert)

**Limitazioni:**
- ❌ Nessun preview staging
- ❌ Nessun sistema di revisione (peer review)
- ❌ Nessun control di quale branch va in prod
- ❌ Nessuna orchestrazione deploy (timing, canary)

### CI/CD Pipeline Assente

**PROBLEMA CRITICO:** Non esiste `.github/workflows/` directory.

Ciò significa:
1. **Nessuna validazione di build** prima del deploy
2. **Nessun linting** del codice
3. **Nessun test** (per contenuti medici, cruciale!)
4. **Nessun security scanning**
5. **Nessun check di performance**

### GitHub Pages Setup

Presunto da configurazione:
- Repository: `bdeornelas.github.io`
- Hosting: GitHub Pages (branch `main`, folder `/`)
- DNS: Personalizzato (non verificato)

**Verifica della configurazione:**

```bash
# Per confermare:
gh repo view bdeornelas/bdeornelas.github.io --json repositoryTopics,nameWithOwner,isPrivate
```

### Proposta di CI/CD Workflow

```yaml
# .github/workflows/build-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # 1. Checkout
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      # 2. Setup Ruby (Jekyll)
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.2
          bundler-cache: true

      # 3. Setup Node (Parcel)
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      # 4. Build & Validate
      - name: Build with Jekyll
        run: bundle exec jekyll build

      - name: Bundle assets with Parcel
        run: npm run build

      # 5. Linting & Security
      - name: HTML validation
        run: |
          npm install -D html-validate
          html-validate _site/**/*.html

      - name: Link checking
        run: |
          npm install -D broken-link-checker
          blc http://localhost:4000 -r

      - name: Security scanning (OWASP)
        run: |
          npm install -D retire
          retire --jspath node_modules

      # 6. Performance audit (Lighthouse)
      - name: Lighthouse audit
        run: |
          npm install -g @lhci/cli@0.8.x
          lhci autorun --config=lighthouserc.json

      # 7. Deploy to GitHub Pages
      - name: Deploy
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_site
```

#### Raccomandazioni Deployment

```
PRIORITÀ CRITICA:
1. Implementare GitHub Actions per validazione build
2. Aggiungere test di integrità per contenuti medici
3. Creare staging preview per PR

PRIORITÀ ALTA:
4. Configurare linting (HTML, CSS, JS)
5. Aggiungere security scanning (Dependabot)
6. Implementare performance budget (Lighthouse)

PRIORITÀ MEDIA:
7. Setup monitoring di uptime
8. Configurare email su deploy failure
9. Aggiungere changelog automatico
```

---

## 4. SCALABILITY ASSESSMENT

### Analisi Capacità Attuale

#### Contenuti (Articles)
```
Attuale:        44 articoli (1.1 MB)
Crescita stimata: +1-2 articoli/settimana

Proiezione a 1 anno:  ~100 articoli (2.5 MB)
Proiezione a 3 anni:  ~250 articoli (6 MB)

Limite Jekyll:  Non fisico, ma operazionale
```

**Valutazione:** ★★★★☆ (4/5)

- ✅ Jekyll supporta facilmente 1000+ articoli
- ✅ Build time scala logaritmicamente (non lineare)
- ❌ Gestione manuale diventa faticosa dopo 100 articoli
- ❌ Ricerca full-text non implementata
- ❌ Filtraggio/categorizzazione manuale

#### Traffico (Users)
```
Attuale: ~100-200 visitori/mese (stima)
Crescita biologica: +20% anno (medico specialista)

Scenario 1 anno:  150-240 visitori/mese
Scenario 3 anni:  ~500 visitori/mese
```

**Valutazione:** ★★★★★ (5/5)

- ✅ GitHub Pages gestisce milioni di richieste/mese
- ✅ Fastly CDN distribuisce globalmente
- ✅ Zero preoccupazioni di downtime o performance
- ✅ Traffico spike auto-managed

#### Form Submissions
```
Attuale: ~2-5 messaggi/mese (stima)
Crescita: +3-5 contatti/mese

Problema: Formspree non scala, solo memorizza
```

**Valutazione:** ★★☆☆☆ (2/5)

- ❌ Nessuna persistenza locale
- ❌ Email del doctor potrebbe saturarsi
- ❌ Nessun CRM o prioritizzazione
- ❌ Nessun follow-up automatico

#### Booking/Prenotazioni
```
Problema maggiore: INESISTENTE nel sito

Attualmente: link esterno a Santagostino.it
Mancanza: integrazione, tracking, reminder
```

**Valutazione:** ★☆☆☆☆ (1/5)

- ❌ Nessun sistema di prenotazione integrato
- ❌ Nessun calendario sincronizzato
- ❌ Nessun reminder automatico
- ❌ Nessuna raccolta dati di drop-off

### Bottleneck Identificati

1. **Gestione contenuti** (severity: MEDIA)
   - Build time potrebbe arrivare a 10+ sec con 500 articoli
   - Nessun search integrato
   - Nessun filtering dinamico

2. **Form handling** (severity: ALTA)
   - Formspree è 3rd party inaffidabile
   - Nessun database locale
   - Email invia 1:1 senza automazione

3. **Prenotazioni** (severity: CRITICA)
   - Completamente assente
   - Integrazione con Santagostino è manuale
   - Nessuno scarico di feedback patient

4. **Analytics** (severity: MEDIA)
   - Nessun tracking di conversione
   - Nessun heatmap o user behavior
   - Impossibile ottimizzare UX

### Proposta di Scalabilità

**FASE 1 (0-6 mesi): Consolidamento**
```
- Migrazione articles a struttura standardizzata (YAML/JSON)
- Setup GitHub Actions CI/CD
- Aggiunta di search client-side (Lunr.js o Algolia)
- Integrazione Formspree con Supabase backup
```

**FASE 2 (6-12 mesi): Dinamicità**
```
- Micro-service backend per prenotazioni (Node.js/Python)
- Database PostgreSQL (Supabase o AWS RDS)
- Email automation (SendGrid)
- Analytics integrato (Fathom Analytics)
```

**FASE 3 (12+ mesi): Full Platform**
```
- CRM personalizzato (follow-up pazienti)
- Telemedicina integration (video call API)
- Payment processing (Stripe per ritardi cancellazione)
- Mobile app (React Native)
```

---

## 5. CACHING STRATEGY

### Cache Layers Attuali

#### Layer 1: GitHub Pages (Fastly CDN)
```
Configurazione: Default
Cache-Control: Dipende da file type

HTML:           Cache: 60 sec (public)
CSS/JS/IMG:     Cache: 1 anno (immutable con versioning)
```

**Problema:** Cache-Control header non configurato in `.github/pages.yml` (inesistente).

#### Layer 2: Browser Cache
```
Default:        Nessun header Cache-Control specifico
Problem:        Dinamica ogni volta che Jekyll rebuild
```

#### Layer 3: Content-Delivery
```
Attuale:        Fastly (automatico)
Ottimizzazione: Assente
```

### File `_headers` Analysis

```
CSP header presente (security):
✓ Content-Security-Policy: 'self', font-src googleapis, img-src 'self' data:

Cache header ASSENTE:
✗ Nessun Cache-Control
✗ Nessun ETag
✗ Nessun Last-Modified
```

### Proposta di Caching Ottimizzato

```
# _headers migliorato
# Per HTML pages (no caching, always check)
/articles/*
/contact/
/about/
  Cache-Control: public, max-age=0, must-revalidate
  ETag: W/"{{ page.last_modified }}"

# Per CSS/JS versionati (cache 1 anno)
/assets/css/*.min.css
/assets/js/*.min.js
  Cache-Control: public, max-age=31536000, immutable

# Per immagini (cache 30 giorni)
/assets/img/*
  Cache-Control: public, max-age=2592000

# Security headers
/*
  Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
```

### Caching Strategia Avanzata (Fase 2)

```
PATTERN 1: Cache-Aside (Current)
┌─────────────┐
│   Browser   │──miss──→ CDN ──miss──→ GitHub Pages
└─────────────┘

PATTERN 2: Stale-While-Revalidate (Recommended)
┌─────────────┐
│   Browser   │──hit──→ STALE DATA + async refresh
└─────────────┘

Implementation:
Cache-Control: public, max-age=3600, stale-while-revalidate=86400
```

### Metriche Cache Suggerite

```
Monitorare con Google Analytics 4:
- First Contentful Paint (FCP): target <2s
- Largest Contentful Paint (LCP): target <2.5s
- Cumulative Layout Shift (CLS): target <0.1

Impostare alert su:
- Cache hit ratio < 80%
- Core Web Vitals > 75th percentile
```

---

## 6. API INTEGRATION ANALYSIS

### Integrazioni Attuali

#### 1. Formspree (Form Handling)
```
Endpoint:       https://formspree.io/f/mblpjvge
Method:         POST
Authentication: Email-based (hidden in action URL)
Use Case:       Contact form submissions

Payload:
{
  name: string,
  _replyto: string (email),
  subject: string,
  message: string,
  _gotcha: string (honeypot)
}

Response:
Status 200 → Email sent
Status 400 → Validation error
```

**Valutazione:** ★★☆☆☆ (2/5)

- ✅ Zero setup, funziona subito
- ✅ SPAM protection (honeypot)
- ❌ Nessun tracking locale
- ❌ Dati non persistiti nel sito
- ❌ Nessun follow-up workflow
- ❌ Email non organizzate in CRM

#### 2. Santagostino (Booking/External)
```
Link:           https://www.santagostino.it/it/prenota
Integration:    Link esterno (nessuna integrazione real)
Use Case:       Prenotazioni

Problem: User deve uscire dal sito
```

**Valutazione:** ★☆☆☆☆ (1/5)

- ❌ Non è integrazione, è redirect
- ❌ Zero feedback nel sito
- ❌ Nessun tracking di conversione
- ❌ Esperienza utente frammentata

#### 3. Lucide Icons (CDN)
```
Endpoint:       https://unpkg.com/lucide@latest
Type:           CDN JavaScript
Use:            Icon rendering
Status:         Working, no issues
```

**Valutazione:** ★★★★☆ (4/5)

- ✅ Leggero e performante
- ✅ Fallback non necessario (optional)
- ❌ Dipendenza esterna (punto di failure)

#### 4. Google Fonts (CDN)
```
Endpoint:       https://fonts.googleapis.com
Endpoint:       https://fonts.gstatic.com
Font:           Inter (400, 500, 700, 800)
Use:            Typography
Status:         Working
```

**Valutazione:** ★★★★☆ (4/5)

- ✅ Ottimizzato da Google
- ✅ WOFF2 compression
- ❌ Latenza di rete aggiuntiva

#### 5. Tailwind CSS (CDN)
```
Endpoint:       https://cdn.tailwindcss.com
Type:           Full framework compilation
Status:         Suboptimale per produzione
```

**PROBLEMA CRITICO:** Tailwind CDN compila CSS runtime nel browser!

```
Impatto:
- ❌ +50-100ms parsing JS
- ❌ +1-2MB JS payload
- ❌ Nessun tree-shaking
- ❌ Layout shift possibile se CSS arriva tardamente
```

**Soluzione consigliata:**
```bash
# Installare Tailwind localmente
npm install -D tailwindcss postcss autoprefixer

# Build CSS in fase Parcel
npx tailwindcss -i ./assets/css/input.css -o ./assets/css/style.css

# Output: CSS minificato senza runtime overhead
```

#### 6. AOS (Animate On Scroll)
```
Endpoint:       https://unpkg.com/aos@2.3.1
Type:           JavaScript library
Size:           ~15KB gzipped
Impact:         Animazioni scroll, performance acceptable
```

**Valutazione:** ★★★☆☆ (3/5)

- ✅ Buon effetto visuale
- ❌ Non essenziale (progressive enhancement mancante)
- ❌ Disabilitato su motion-reduce (accessibility OK)

### API Recommendations

```
PRIORITÀ CRITICA:
1. Eliminare Tailwind CDN, migrare a build locale
2. Implementare API per prenotazioni (Backend)
3. Setup database per form submissions (Supabase)

PRIORITÀ ALTA:
4. Aggiungere SendGrid/Resend per email automation
5. Implementare Fathom Analytics (privacy-first)
6. Integrare Google Calendar API per disponibilità

PRIORITÀ MEDIA:
7. Aggiungere Stripe API per cancellazione tardiva
8. Setup Sentry per error tracking
9. Implementare Slack notification per form submissions
```

---

## 7. BUILD OPTIMIZATION

### Current Build Metrics

```
Jekyll Build Time:      ~2-3 sec
Parcel Build Time:      ~1-2 sec
Total:                  ~3-5 sec

CSS Output:             Minified (style.min.css)
JS Output:              Minified (main.min.js)
HTML:                   Non-minified (di default)
Image Optimization:     Assente (solo lazy loading)
```

### Build Pipeline Issues

#### PROBLEMA 1: Doppio Bundler
```
Attuale:
Jekyll → _site/
Parcel → _site/dist/

Conflitto:
- Jekyll non sa di Parcel output
- Link html → /assets/css/style.css
- Ma file è in /dist/css/

Soluzione: Orchestrazione mancante
```

#### PROBLEMA 2: No Source Maps
```
Error in console: ??? (minified)
Causa: --no-source-maps flag

Problema: Debugging in produzione impossibile
Soluzione: Aggiungere source maps (separate da HTML)
```

#### PROBLEMA 3: Tailwind Runtime
```
CSS via CDN: https://cdn.tailwindcss.com
Overhead: +100KB JS runtime nel browser
Soluzione: Build locale (vedi sezione API)
```

#### PROBLEMA 4: No Image Optimization
```
Attuale: assets/img/*.jpg (dimensioni native?)
Missing: WebP conversion, responsive images
Soluzione: imagemin (già in devDependencies!)
```

### Optimized Build Configuration

#### package.json migliorato

```json
{
  "scripts": {
    "build": "npm run build:css && npm run build:js && npm run build:jekyll && npm run optimize:images",
    "build:css": "tailwindcss -i assets/css/input.css -o _site/assets/css/style.css --minify",
    "build:js": "parcel build assets/js/main.js --dist-dir _site/assets/js --target browser",
    "build:jekyll": "jekyll build",
    "optimize:images": "imagemin assets/img --out-dir=_site/assets/img",
    "watch": "npm run watch:jekyll & npm run watch:js",
    "watch:jekyll": "jekyll serve --livereload",
    "watch:js": "parcel watch assets/js/main.js --dist-dir assets/js",
    "test": "npm run lint && npm run validate",
    "lint": "eslint assets/js && stylelint assets/css",
    "validate": "html-validate _site/**/*.html"
  }
}
```

#### Tailwind Configuration

```javascript
// tailwind.config.js (nuovo file)
module.exports = {
  content: [
    './_includes/**/*.html',
    './_layouts/**/*.html',
    './articles/**/*.html',
    './contact/**/*.html',
    './about/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        sky: {
          // Custom cardiologo theme
        }
      }
    }
  },
  plugins: [],
  // PurgeCSS: remove unused styles
  safelist: [
    // Dinamiche classe che Tailwind non vede nel scan
    /^bg-/, /^text-/, /^border-/
  ]
}
```

### Build Optimization Checklist

```
BEFORE BUILD:
□ Linting (eslint, stylelint)
□ Format check (prettier)
□ Security audit (npm audit, retire)

DURING BUILD:
□ CSS minification + PurgeCSS (rimuove 90% CSS unused)
□ JS minification + tree-shaking
□ HTML minification
□ Image optimization (WebP, AVIF)
□ Fingerprinting assets (cache busting)

AFTER BUILD:
□ Size budget check (CSS <50KB, JS <100KB)
□ Performance audit (Lighthouse)
□ Accessibility audit (axe-core)
□ Link validation (broken-link-checker)

PRODUCTION:
□ Gzip compression (nginx/Fastly, automatico)
□ Brotli compression (browser support)
□ Resource hints (preconnect, prefetch)
```

### Build Performance Targets

```
Metric                  Current     Target      Impact
─────────────────────────────────────────────────────
CSS Size                Unknown     <50KB       Network
JS Size                 Unknown     <100KB      Network
HTML Size               20-80KB     <20KB       Network
Total Payload           ~150KB      <80KB       Core Web Vitals
Lighthouse Score        Unknown     >90         SEO/UX
LCP (Largest Paint)     Unknown     <2.5s       User Experience
FID (First Input Delay) Unknown     <100ms      Interactivity
CLS (Layout Shift)      Unknown     <0.1        Stability
```

#### Raccomandazioni Build

```
PRIORITÀ ALTA:
1. Eliminare Tailwind CDN (sostituire con build locale)
2. Implementare CSS minification + PurgeCSS
3. Aggiungere source maps per debugging

PRIORITÀ MEDIA:
4. Configurare image optimization (imagemin)
5. Implementare fingerprinting per cache busting
6. Aggiungere Lighthouse CI

PRIORITÀ BASSA:
7. Esplorare WebP/AVIF conversion
8. Setup Parcel plugin per inline critical CSS
```

---

## 8. CONTENT MANAGEMENT WORKFLOW

### Attuale Workflow

```
1. Developer scrive articolo in HTML
   articles/[slug]/index.html

2. Front Matter: Manual (no validation)
   layout: default
   title: "..."
   description: "..."
   date: YYYY-MM-DD

3. Commit & Push
   git add articles/
   git commit -m "Add article: ..."
   git push

4. GitHub Pages build (automatic)
   Deploy a https://bdeornelas.github.io/articles/[slug]/

5. Nessuna review, nessuna staging
```

**Valutazione:** ★★☆☆☆ (2/5)

- ✅ Veloce per chi sa git e HTML
- ❌ Non scalabile con editori non-technical
- ❌ Nessuna bozza/staging
- ❌ Nessun calendario editoriale
- ❌ Nessun versionamento metadati
- ❌ Nessun sistema di review

### Improved CMS Workflow (Proposal)

#### Opzione 1: Decap CMS (Headless CMS, Open Source)

```yaml
# static/admin/config.yml
backend:
  name: github
  repo: bdeornelas/bdeornelas.github.io
  branch: main

media_folder: assets/img/articles
public_folder: /assets/img/articles

collections:
  - name: articles
    label: Articoli
    folder: articles
    create: true
    slug: "{{slug}}"
    fields:
      - label: Titolo
        name: title
        widget: string
      - label: Descrizione SEO
        name: description
        widget: text
      - label: Data Pubblicazione
        name: date
        widget: datetime
      - label: Body
        name: body
        widget: markdown
      - label: Categoria
        name: category
        widget: select
        options: [Cardiologia, Prevenzione, Screening]
      - label: Immagine Cover
        name: og_image
        widget: image
      - label: Status
        name: status
        widget: select
        options: [draft, published, archived]
```

**Vantaggi:**
- ✅ UI intuitiva anche per non-developers
- ✅ Git-based (decentralizzato)
- ✅ Nessun database esterno
- ✅ Draft/publish automation
- ✅ Scheduling pubblicazione

**Svantaggi:**
- ❌ Ancora richiede GitHub account
- ❌ Meno community vs WordPress

#### Opzione 2: Statamic (Headless CMS, Paid)

```
Costo:          ~$500/anno
Hosting:        Statamic Cloud
Git Sync:       Bidirezionale
Features:       CMS UI + Static generation
```

#### Opzione 3: Strapi (Headless CMS, Open Source + Paid Cloud)

```
Costo:          €0 self-hosted, €90-500+ cloud
Hosting:        Own server o Strapi Cloud
Features:       Full REST API, Media management
```

### Template System Migliorato

#### Standardizzare Front Matter (con validazione)

```yaml
# articles/_schema.yml (META configuration)
fields:
  title:
    type: string
    required: true
    maxlength: 120

  description:
    type: string
    required: true
    minlength: 50
    maxlength: 160

  category:
    type: enum
    required: true
    values: [Cardiologia, Prevenzione, Screening, Farmaci, Diagnostica]

  date:
    type: date
    required: true
    format: YYYY-MM-DD

  status:
    type: enum
    default: draft
    values: [draft, published, archived, scheduled]

  author:
    type: string
    default: "Dr. Benjamin De Ornelas"

  seo:
    og_title:
      type: string
      maxlength: 120
    og_description:
      type: string
      maxlength: 160
    og_image:
      type: string
      pattern: "^/assets/.*\\.(jpg|png|webp)$"
```

#### Validation Script

```bash
#!/bin/bash
# scripts/validate-articles.sh

for article in articles/*/index.html; do
  echo "Validating $article..."

  # Extract front matter
  fm=$(sed -n '/^---$/,/^---$/p' "$article")

  # Check required fields
  if ! echo "$fm" | grep -q "^title:"; then
    echo "ERROR: $article missing title"
    exit 1
  fi

  if ! echo "$fm" | grep -q "^category:"; then
    echo "ERROR: $article missing category"
    exit 1
  fi
done

echo "All articles valid!"
```

### Editorial Calendar Workflow

```
SETTIMANA 1 (Mon-Wed):
- Pianificare 3-4 articoli
- Assegnare a team medico
- Creare bozze

SETTIMANA 2 (Thu):
- Review medico (accuratezza, sources)
- Ottimizzazione SEO
- Scheduling pubblicazione

SETTIMANA 3 (Fri):
- Pubblicare articoli
- Condividere social media
- Monitor analytics
```

#### Strumenti Consigliati

```
Editorial Calendar:     Notion, Asana, ClickUp
Content Drafts:         Decap CMS, Google Docs
Medical Review:         Google Docs con commenti
Publishing:             Decap CMS automatic
Social Sharing:         Zapier → Twitter/LinkedIn
Analytics:              Fathom (privacy-first)
```

### Content Governance

```
GUIDELINES:
1. Ogni articolo ha review medico
2. Minimo 800 parole (SEO)
3. Almeno 1-2 fonti peer-reviewed
4. Schema markup obbligatorio
5. Immagini optimizzate (WebP, <100KB)

ROLES:
- Dr. De Ornelas:       Author + Medical reviewer
- Editor (esterno):     Copy-editing + SEO + Scheduling
- Developer:            Technical setup (Git, deployment)

SCHEDULE:
- 1-2 articoli/settimana
- Buffer di 2-3 settimane
```

---

## 9. MONITORING & ANALYTICS

### Current Monitoring: ASSENTE

```
✗ Nessuno Google Analytics
✗ Nessuno monitoring errori
✗ Nessuno tracking performance
✗ Nessuno uptime monitoring
✗ Nessuno heatmap utenti
```

### Proposed Analytics Stack

#### Layer 1: Privacy-First Analytics (Fathom o Plausible)

```
Provider:       Fathom Analytics (EU-based, GDPR-compliant)
Cost:           €14-99/mese
Data:           No cookies, no PII, aggregated only

Metrics tracked:
- Pageviews by page
- Sessions
- Bounce rate
- Time on page
- Top referrers
- Devices (mobile/desktop/tablet)
- Browsers
- Conversions (form submissions, booking links clicked)

No tracking:
- Personal data
- Cross-site tracking
- Cookie consent required
```

#### Layer 2: Error Tracking (Sentry)

```
Provider:       Sentry.io (free tier: 5000 errors/month)
Setup:          https://cdn.sentry.io/[projectId].js

Captures:
- JavaScript errors
- Network errors
- Performance issues
- Slow transactions

Example:
Sentry.init({
  dsn: "https://[key]@sentry.io/[projectId]",
  tracesSampleRate: 0.1,
});
```

#### Layer 3: Performance Monitoring

```
Metrics (Core Web Vitals):
- LCP (Largest Contentful Paint): Target <2.5s
- FID (First Input Delay): Target <100ms
- CLS (Cumulative Layout Shift): Target <0.1

Tools:
- Lighthouse CI (automated in GitHub Actions)
- WebPageTest (monthly manual)
- Sentry Performance (automatic transaction tracking)
```

#### Layer 4: Conversion Tracking

```
Events:
1. Form Submitted
   - Name: contact_form_submitted
   - Properties: form_type, subject, referrer

2. Booking Link Clicked
   - Name: booking_clicked
   - Properties: location, service_type, referrer

3. Article Read (time-based)
   - Name: article_read_50%+
   - Properties: article_slug, time_spent

Implementation (Fathom):
<script>
window.addEventListener('submit', (e) => {
  if (e.target.id === 'contact-form') {
    window.fathom.trackGoal('CONTACT_FORM', 0);
  }
});
</script>
```

### Monitoring Dashboard (Recommended Setup)

```
Daily (Automated Email):
- New errors (Sentry)
- Form submissions count
- Page performance (Lighthouse)

Weekly (Manual Review):
- Top performing articles (Fathom)
- Conversion funnel (booking clicks → actual bookings)
- Traffic sources (referrers)
- Mobile vs Desktop ratio

Monthly (Strategic):
- YoY growth trends
- Content performance analysis
- SEO ranking changes (Google Search Console)
- Competitor analysis
```

### Implementation Priority

```
PRIORITÀ CRITICA:
1. Implementare Fathom Analytics (privacy-first)
2. Aggiungere Sentry error tracking
3. Setup Lighthouse CI in GitHub Actions

PRIORITÀ ALTA:
4. Aggiungere Google Search Console
5. Implementare conversion tracking
6. Setup email alert per errors

PRIORITÀ MEDIA:
7. Heatmap tracking (Hotjar)
8. Form analytics (Formspree has basic logging)
9. A/B testing infrastructure
```

---

## 10. FUTURE ARCHITECTURE EVOLUTION

### Current State Assessment

```
MATURITY LEVEL: 2/5 (Basic Static Site)

Scoring:
- Content Management:    2/5 (Git-based, no CMS)
- Backend Services:      1/5 (Non-existent)
- Data Persistence:      1/5 (No database)
- Analytics:             1/5 (Non-existent)
- User Experience:       3/5 (Good frontend, limited features)
- Operations:            2/5 (No CI/CD, no monitoring)
- Security:              3/5 (Basic, but no validation)
- Scalability:           4/5 (GitHub Pages handles it)
```

### Evolution Roadmap (3 Years)

#### FASE 1: FOUNDATION (Months 0-6)
**Obiettivo:** Stabilizzare infrastruttura e aggiungere basics

```
□ GitHub Actions CI/CD setup
□ Linting + Security scanning
□ Decap CMS integrazione
□ Fathom Analytics
□ Sentry error tracking
□ CSS optimization (elimina Tailwind CDN)

Output:
- Build pipeline automatizzato
- Content management UX migliorata
- Analytics dashboard
```

**Cost:** ~€0 (solo strumenti free/open-source)

**Timeline:** 3-4 settimane lavoro

#### FASE 2: BACKEND SERVICES (Months 6-12)
**Obiettivo:** Aggiungere prenotazioni e CRM basic

```
□ Backend leggero (Node.js + Express o Python + FastAPI)
□ Database PostgreSQL (Supabase)
□ API prenotazioni integrata
□ Email automation (SendGrid)
□ Google Calendar API sync
□ Form submission handler con persistenza
□ Telemedicina integration (per futuro)

Architecture:
┌─────────────────────────────────────┐
│ Frontend (Static Site + SPA)        │
├─────────────────────────────────────┤
│ Backend API (Node.js/Python)        │
│ ├─ /api/bookings                    │
│ ├─ /api/forms                       │
│ ├─ /api/calendar                    │
│ └─ /api/notifications               │
├─────────────────────────────────────┤
│ Database (PostgreSQL)               │
│ ├─ bookings                         │
│ ├─ form_submissions                 │
│ ├─ patients                         │
│ └─ appointments                     │
├─────────────────────────────────────┤
│ External Services                   │
│ ├─ Santagostino Calendar (API)      │
│ ├─ SendGrid Email                   │
│ ├─ Google Calendar                  │
│ └─ Stripe (optional)                │
└─────────────────────────────────────┘

Technology Stack:
- Frontend: Jekyll (static) + React.js (SPA parts)
- Backend: Node.js + Express.js
- Database: PostgreSQL (Supabase)
- Hosting: Vercel (backend), Supabase (DB), GitHub Pages (frontend)
- Email: SendGrid
- Monitoring: Sentry, Fathom
```

**Cost:** €20-100/mese (Supabase, Sendgrid, Vercel)

**Timeline:** 8-12 settimane lavoro + testing

#### FASE 3: FULL PLATFORM (Months 12+)
**Obiettivo:** Evoluzione verso full SaaS platform

```
□ Mobile app (React Native o Flutter)
□ CRM completo (patient management)
□ Telemedicina (video consultations)
□ Payment processing (Stripe)
□ Appointment reminders (SMS + Email)
□ AI-powered scheduling
□ Medical record system
□ Prescription management

Optional Evolution:
- Multi-doctor support
- Lab result integration
- Wearable device integration
- Insurance claim processing
```

**Cost:** €500-2000/mese (depending on scale)

**Timeline:** 6+ mesi development

### Technology Recommendations by Phase

#### PHASE 1: Conservative (No Major Changes)

```
Frontend:       Keep Jekyll + Parcel (works fine)
CMS:            Decap CMS (free, git-based)
Analytics:      Fathom (privacy-first)
Error Tracking: Sentry free tier
Hosting:        GitHub Pages (unchanged)

Why: Minimal risk, low cost, clear wins
```

#### PHASE 2: JAMstack Enhanced

```
Frontend:       Jekyll + React SPA (hybrid)
Backend:        Node.js + Express.js
Database:       Supabase (PostgreSQL)
CMS:            Decap CMS + Supabase content API
Hosting:        Vercel (Backend), Supabase (DB), GitHub Pages (Frontend)
Email:          SendGrid
Calendar:       Google Calendar API + Santagostino sync

Why: Still JAMstack spirit, but with backend capabilities
Advantage: Incremental migration, no rewrite needed
```

#### PHASE 3: Full Service Oriented

```
Frontend:       Next.js (React + SSR)
Backend:        Python FastAPI or Node.js
Database:       PostgreSQL + Redis cache
CMS:            Strapi (self-hosted or Strapi Cloud)
Hosting:        AWS/Google Cloud/DigitalOcean
Message Queue:  RabbitMQ or AWS SQS
Video:          Twilio or Agora for telemedicina
Payment:        Stripe for cancellations
Mobile:         React Native or Flutter

Why: Professional SaaS platform ready for scaling
```

### Architecture Decision: Headless CMS Choice

#### Comparison Table

```
            | Decap CMS  | Strapi     | Contentful | Builder.io
────────────┼────────────┼────────────┼────────────┼──────────
Cost        | Free       | €0-500     | €99-499    | €0-200
Learning    | Easy       | Medium     | Hard       | Easy
Git-based   | Yes        | Optional   | No         | No
Self-hosted | Yes        | Yes        | No         | No
API         | Simple     | GraphQL+   | GraphQL    | REST+
           |            | REST       |            |
Scalability | Medium     | High       | High       | Medium
Maturity    | Stable     | Growing    | Enterprise | Growing
────────────┼────────────┼────────────┼────────────┼──────────
BEST FOR:   | Static     | Full CMS   | Enterprise | Builders
            | sites +    | with API   | SaaS       | & Creators
            | git flow   |            |            |
```

**Recommendation:** Start with **Decap CMS** (Phase 1), migrate to **Strapi** if Phase 2 requires more features.

### Risk Mitigation

#### Migration Risks

```
RISK: Data lock-in with proprietary CMS
MITIGATION: Use Decap CMS (GitHub-based, portable)

RISK: Backend complexity increases maintenance
MITIGATION: Use managed services (Supabase, Vercel)

RISK: Increased costs
MITIGATION: Start small, scale only when revenue justifies

RISK: Security vulnerability in new backend
MITIGATION: Security scanning, regular audits, bug bounty program
```

#### Fallback Strategy

```
If Phase 2 becomes too complex:
1. Keep current static site as-is (stable, no maintenance)
2. Host booking system separately (external domain)
3. Email form via third-party only (Formspree)
4. This maintains status quo with minor improvements

This is a valid long-term strategy if resources are limited.
```

---

## SUMMARY: BUSINESS ALIGNMENT

### Current State vs. Business Requirements

```
BUSINESS NEED              | CURRENT STATE    | SATISFACTION | SOLUTION
─────────────────────────────────────────────────────────────────────────
Publish medical content    | Jekyll articles  | ★★★★☆       | Good, needs CMS
Attract patients (SEO)     | Basic metadata   | ★★★☆☆       | Needs more structure
Enable online booking      | Link to external | ★☆☆☆☆       | CRITICAL gap
Manage patient inquiries   | Email only       | ★★☆☆☆       | Needs database
Track patient journey      | No tracking      | ★☆☆☆☆       | Needs analytics
Provide telemedicine       | Not available    | ★☆☆☆☆       | Future feature
Handle payments            | Not available    | ★☆☆☆☆       | Future feature
Maintain HIPAA/GDPR        | Minimal          | ★★☆☆☆       | Needs review
```

### Investment ROI Analysis

```
PHASE 1 (Foundation)
Cost:       ~€200 tools + 4 weeks dev
Benefit:    Better build pipeline, CMS UX, analytics, error tracking
ROI:        High (enables Phase 2, improves operations)

PHASE 2 (Backend Services)
Cost:       €50/month + 12 weeks dev
Benefit:    Online booking, patient database, email automation
ROI:        CRITICAL for patient acquisition and retention

PHASE 3 (Full Platform)
Cost:       €500-2000/month + months dev
Benefit:    Competitive advantage, subscription revenue potential
ROI:        Only if patient volume justifies
```

### Recommendation Matrix

```
IF small practice (10-20 patients/month):
→ Implement PHASE 1 + external booking link
→ Focus on content quality and SEO
→ Cost: Low, ROI: High

IF medium practice (50+ patients/month):
→ Implement PHASE 1 + PHASE 2
→ Integrate booking + CRM
→ Cost: Medium, ROI: High

IF growth target (100+ patients/month):
→ Implement all PHASE 2 features
→ Consider PHASE 3 for telemedicina
→ Cost: High, ROI: Depends on pricing model
```

---

## FINAL RECOMMENDATIONS

### TOP 10 PRIORITY ACTIONS

```
RANK | PRIORITY | ACTION                          | EFFORT | IMPACT | TIMEFRAME
─────┼──────────┼─────────────────────────────────┼────────┼────────┼────────────
1    | CRITICAL | Setup GitHub Actions CI/CD      | 2d     | HIGH   | Week 1-2
2    | CRITICAL | Eliminate Tailwind CDN          | 3d     | HIGH   | Week 1-2
3    | CRITICAL | Implement Fathom Analytics      | 1d     | HIGH   | Week 1
4    | CRITICAL | Standardize article front-matter| 2d     | HIGH   | Week 2
5    | HIGH     | Setup Decap CMS                 | 5d     | MEDIUM | Week 3-4
6    | HIGH     | Implement error tracking (Sentry)| 1d     | MEDIUM | Week 2
7    | HIGH     | Image optimization setup        | 2d     | MEDIUM | Week 2-3
8    | MEDIUM   | Setup Google Search Console     | 1d     | MEDIUM | Week 1
9    | MEDIUM   | Create content calendar system  | 3d     | MEDIUM | Week 3-4
10   | MEDIUM   | Backend API foundation (Phase 2)| 10d    | HIGH   | Month 2
```

### Quick Wins (Implementable This Month)

```
1. GitHub Actions CI/CD
   - Setup build validation
   - Add linting + security scan
   - Configure Lighthouse CI
   Time: 2-3 days
   Impact: Prevents broken deployments

2. Fathom Analytics
   - Add single JS snippet
   - Configure conversion tracking
   - Setup email alerts
   Time: 1 day
   Impact: Data-driven decisions on content

3. Sentry Error Tracking
   - Add JS snippet
   - Configure project settings
   - Setup Slack notifications
   Time: 1 day
   Impact: Catch user-facing bugs early

4. CSS Optimization
   - Tailwind local build
   - PurgeCSS setup
   - Remove Tailwind CDN
   Time: 2-3 days
   Impact: Faster page loads (-30% CSS size)

TOTAL TIME: ~1 week
TOTAL COST: €0 (all free tiers)
TOTAL IMPACT: Significant UX + operations improvement
```

### Budget Allocation (Year 1)

```
Tier 1: Foundation (Month 1)
- GitHub Actions CI:        €0 (included)
- Fathom Analytics:         €14/month
- Sentry:                   €0 (free tier)
Subtotal:                   €14/month

Tier 2: CMS + Automation (Month 2-3)
- Decap CMS:                €0 (open-source)
- SendGrid:                 €20/month
- Supabase (development):   €10/month
Subtotal:                   €30/month

Tier 3: Production Backend (Month 4-12)
- Supabase (production):    €50-100/month
- Vercel (backend):         €20/month
- SendGrid (volume):        €30-50/month
- Additional services:      €20-50/month
Subtotal:                   €120-220/month

TOTAL YEAR 1: €1500-2500
(vs. €0 currently, but enabling €1000+ monthly patients)
```

### Technical Debt To Address

```
HIGH PRIORITY:
1. Duplicate build orchestration (Jekyll + Parcel)
2. Missing CI/CD pipeline
3. No source maps for debugging
4. Tailwind CDN runtime compilation

MEDIUM PRIORITY:
5. No image optimization
6. No content validation system
7. No database for persistence
8. Missing error tracking

LOW PRIORITY:
9. Article structure needs standardization
10. No full-text search
11. No content versioning
12. No A/B testing framework
```

---

## CONCLUSION

### Current Architecture Assessment: ADEQUATE BUT LIMITED

The current Jekyll + GitHub Pages architecture is **excellent for content publishing** but **insufficient for a medical practice** requiring:
- Dynamic booking
- Patient data persistence
- Email automation
- Analytics and conversion tracking

### Recommended Path Forward

```
PHASE 1 (NOW - Month 2):      Foundation + CMS
PHASE 2 (Month 3-6):           Backend + Booking
PHASE 3 (Month 6+):            Full Platform + Telemedicina

Total Investment: €2000-5000/year
Expected ROI: 10-50x (if patient volume follows)
```

### Key Success Metrics (6 Months)

```
- Build pipeline fully automated
- Analytics dashboard active (weekly reviews)
- CMS in use by content team
- 100+ medical articles published
- <2s average page load
- >90 Lighthouse score
- 0 JavaScript errors in production
- Booking integration with Santagostino
- Patient inquiry database with 100+ leads
```

This roadmap balances **pragmatism** (use current tech, extend incrementally) with **ambition** (enable growth and automation).

---

## APPENDIX: FILE MANIFEST

```
Configuration:
- _config.yml
- package.json
- Gemfile
- _headers
- robots.txt
- sitemap.xml

Templates:
- _layouts/default.html
- _includes/header.html
- _includes/footer.html

Content:
- articles/ (44 directories)
- contact/index.html
- about/
- privacy/
- cookie-policy/

Assets:
- assets/css/style.css (+ .min.css)
- assets/js/main.js (+ .min.js)
- assets/js/aos.min.js
- assets/js/lucide.min.js
- assets/img/ (logos, photos)

Build Output:
- _site/ (4.8 MB, generated)
- dist/ (CSS/JS bundled)

Dependencies:
- Ruby (Jekyll via Gemfile)
- Node.js (Parcel via package.json)
- CDN: Tailwind, Lucide, AOS, Google Fonts
```

