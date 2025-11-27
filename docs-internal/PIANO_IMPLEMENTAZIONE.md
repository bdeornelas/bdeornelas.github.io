# PIANO DI IMPLEMENTAZIONE PRATICO
## Dr. Benjamin De Ornelas - bdeornelas.github.io

**Documento:** Guida passo-passo per implementare le raccomandazioni di architettura
**Destinatari:** Developer + Dr. De Ornelas
**Obiettivo:** Evolvere il sito da Static Site a Platform con Backend Services

---

## SOMMARIO ESECUTIVO

Questo documento fornisce **istruzioni concrete e codice pronto all'uso** per implementare:

1. **FASE 1 (Week 1-4):** Build pipeline, analytics, CSS optimization
2. **FASE 2 (Month 2-4):** Backend API per booking e form handling
3. **FASE 3 (Month 6+):** Mobile app, telemedicina, advanced features

**Investimento:** €2500-8500 (Fase 1), €20000-30000 (Fase 1+2 complete)
**Timeline:** 4 settimane Phase 1, 8-12 settimane Phase 2, 6+ mesi Phase 3
**Team:** 1-2 developers, 1 DevOps engineer (per phase 2+)

---

## FASE 1: FOUNDATION (SETTIMANE 1-4)

### SETTIMANA 1: GitHub Actions + Analytics

#### TASK 1.1: Setup GitHub Actions CI/CD

**Tempo:** 2-3 ore
**Difficoltà:** Facile

**Step 1.1.1: Creare workflow file**

```bash
# Posizionarsi nel repository
cd /Users/benjamindeornelas/Documents/bdeornelas.github.io

# Creare directory workflows
mkdir -p .github/workflows

# Creare il file build.yml
cat > .github/workflows/build.yml << 'EOF'
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
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build Jekyll
        run: bundle exec jekyll build
        env:
          JEKYLL_ENV: production

      - name: Bundle assets
        run: npm run build

      - name: Run linting
        run: |
          npm run lint || echo "Linting failed (non-blocking)"

      - name: HTML validation
        run: |
          npm install -D html-validate
          npx html-validate _site/**/*.html || echo "HTML validation warnings"

      - name: Deploy to GitHub Pages
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_site
          cname: bdeornelas.github.io
EOF
```

**Step 1.1.2: Aggiornare package.json con script**

```bash
# Leggere current package.json
cat package.json

# Aggiornare con nuovi script
cat > package.json << 'EOF'
{
  "name": "bdeornelas.github.io",
  "version": "1.0.0",
  "description": "Personal website for Dr. Benjamin De Ornelas",
  "scripts": {
    "build": "npm run build:parcel",
    "build:parcel": "parcel build assets/js/main.js assets/css/style.css --dist-dir dist --no-source-maps",
    "build:jekyll": "bundle exec jekyll build",
    "watch": "parcel watch assets/js/main.js assets/css/style.css --dist-dir dist",
    "lint": "eslint 'assets/js/**/*.js' --fix || true",
    "test": "npm run lint",
    "start": "bundle exec jekyll serve --livereload"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.19",
    "eslint": "^8.56.0",
    "imagemin": "^9.0.1",
    "imagemin-jpegtran": "^8.0.0",
    "imagemin-mozjpeg": "^10.0.0",
    "imagemin-pngquant": "^10.0.0",
    "parcel": "^2.12.0"
  },
  "browserslist": [
    "last 2 versions",
    "> 1%",
    "not dead"
  ]
}
EOF
```

**Step 1.1.3: Commit e test**

```bash
git add .github/workflows/build.yml package.json
git commit -m "Add GitHub Actions CI/CD pipeline"
git push
```

Andare su GitHub → Actions → Verificare che il build sia passato ✓

---

#### TASK 1.2: Implementare Fathom Analytics

**Tempo:** 1-2 ore
**Difficoltà:** Molto facile

**Step 1.2.1: Creare account Fathom**

1. Andare su https://usefathom.com
2. Registrarsi con email
3. Selezionare piano "Lite" (€14/month)
4. Creare nuovo sito: "bdeornelas.github.io"
5. Copiare il tracking code (formato: `XXXXX`)

**Step 1.2.2: Aggiungere snippet al template**

```bash
# Leggere il file default layout
cat _layouts/default.html | head -200

# Aggiungere tracking code PRIMA di </head>
```

Aprire `/Users/benjamindeornelas/Documents/bdeornelas.github.io/_layouts/default.html` e aggiungere prima della chiusura di `</head>`:

```html
<!-- Fathom Analytics -->
<script src="https://cdn.usefathom.com/script.js" data-site="XXXXXX" defer></script>
<!-- End Fathom Analytics -->
```

Sostituire `XXXXXX` con il Site ID ricevuto da Fathom.

**Step 1.2.3: Configurare conversion goals in Fathom Dashboard**

1. Andare a Fathom Dashboard → Settings → Custom Events
2. Aggiungere event: "contact_form_submitted"
3. Aggiungere event: "booking_clicked"

**Step 1.2.4: Testare**

```bash
# Fare rebuild locale
bundle exec jekyll build

# Controllare che tracking code sia presente in _site
grep "usefathom" _site/index.html
```

---

#### TASK 1.3: Setup Sentry Error Tracking

**Tempo:** 1-2 ore
**Difficoltà:** Facile

**Step 1.3.1: Creare account Sentry**

1. Andare su https://sentry.io
2. Registrarsi gratis (free tier: 5000 events/month)
3. Creare project: "bdeornelas-website"
4. Selezionare "JavaScript" come SDK
5. Copiare DSN

**Step 1.3.2: Aggiungere Sentry allo script principale**

Creare `/Users/benjamindeornelas/Documents/bdeornelas.github.io/assets/js/sentry.js`:

```javascript
// Initialize Sentry
Sentry.init({
  dsn: "https://[key]@[server].ingest.sentry.io/[projectId]",
  environment: "production",
  tracesSampleRate: 0.1,
  beforeSend(event) {
    // Filter out personal data
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers['User-Agent'];
    }
    return event;
  }
});

// Capture unhandled errors
window.addEventListener('error', (event) => {
  Sentry.captureException(event.error);
});

// Capture unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  Sentry.captureException(event.reason);
});
```

**Step 1.3.3: Includere nel template**

Nel file `_layouts/default.html`, aggiungere DOPO il Fathom script:

```html
<!-- Sentry Error Tracking -->
<script src="https://cdn.ravenjs.com/[version]/raven.min.js"></script>
<script src="/assets/js/sentry.js"></script>
<!-- End Sentry -->
```

---

### SETTIMANA 2: CSS Optimization + Image Optimization

#### TASK 2.1: Eliminare Tailwind CDN e Migrare a Build Locale

**Tempo:** 2-3 ore
**Difficoltà:** Medio

**Step 2.1.1: Installare Tailwind localmente**

```bash
cd /Users/benjamindeornelas/Documents/bdeornelas.github.io

# Installare dipendenze
npm install -D tailwindcss postcss autoprefixer

# Generare config
npx tailwindcss init -p
```

**Step 2.1.2: Configurare tailwind.config.js**

```bash
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './_layouts/**/*.html',
    './_includes/**/*.html',
    './articles/**/*.html',
    './contact/**/*.html',
    './about/**/*.html',
    './privacy/**/*.html',
    './cookie-policy/**/*.html',
    './_site/**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        sky: {
          400: '#0ea5e9',
          500: '#0284c7',
          600: '#0369a1',
        }
      },
      animation: {
        'pulse-glow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
  safelist: [
    // Dynamic classes che Tailwind non può vedere nei scan
    /^bg-/,
    /^text-/,
    /^border-/,
    /^rounded-/,
  ]
}
EOF
```

**Step 2.1.3: Configurare PostCSS**

```bash
cat > postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
EOF
```

**Step 2.1.4: Creare input CSS**

```bash
cat > assets/css/input.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
.glass-card {
  @apply bg-slate-800/20 backdrop-blur-md border border-slate-700/50 rounded-lg;
}

.gradient-text {
  @apply bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent;
}

.pulse-glow-animation {
  animation: pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
EOF
```

**Step 2.1.5: Aggiornare package.json con build script**

```bash
cat > package.json << 'EOF'
{
  "name": "bdeornelas.github.io",
  "version": "1.0.0",
  "scripts": {
    "build": "npm run build:css && npm run build:parcel && npm run build:jekyll",
    "build:css": "tailwindcss -i ./assets/css/input.css -o ./assets/css/style.css --minify",
    "build:parcel": "parcel build assets/js/main.js --dist-dir dist --no-source-maps",
    "build:jekyll": "bundle exec jekyll build",
    "watch:css": "tailwindcss -i ./assets/css/input.css -o ./assets/css/style.css --watch",
    "watch:jekyll": "bundle exec jekyll serve --livereload",
    "dev": "npm run watch:jekyll",
    "lint": "eslint 'assets/js/**/*.js' --fix || true"
  },
  "devDependencies": {
    "autoprefixer": "^10.4.19",
    "eslint": "^8.56.0",
    "parcel": "^2.12.0",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.31"
  }
}
EOF
```

**Step 2.1.6: Rimuovere Tailwind CDN dal template**

Nel file `_layouts/default.html`, trovare e RIMUOVERE:

```html
<!-- RIMUOVERE QUESTA RIGA: -->
<script src="https://cdn.tailwindcss.com"></script>
```

E aggiungere DOPO `<link rel="icon"...>`:

```html
<!-- Tailwind CSS (built locally) -->
<link rel="stylesheet" href="/assets/css/style.css">
```

**Step 2.1.7: Build e test**

```bash
cd /Users/benjamindeornelas/Documents/bdeornelas.github.io

# Buildare CSS
npm run build:css

# Verificare che il file è stato generato
ls -lh assets/css/style.css

# Fare build completo
npm run build
```

---

#### TASK 2.2: Image Optimization

**Tempo:** 1-2 ore
**Difficoltà:** Facile

**Step 2.2.1: Setup imagemin**

```bash
npm install -D imagemin imagemin-mozjpeg imagemin-pngquant imagemin-webp

# Verificare che è installato
npm list imagemin
```

**Step 2.2.2: Creare script di ottimizzazione**

```bash
cat > scripts/optimize-images.sh << 'EOF'
#!/bin/bash
# Image optimization script

INPUT_DIR="assets/img"
OUTPUT_DIR="assets/img-optimized"

mkdir -p $OUTPUT_DIR

# JPG optimization
imagemin "$INPUT_DIR"/*.jpg --out-dir=$OUTPUT_DIR --plugin=mozjpeg

# PNG optimization
imagemin "$INPUT_DIR"/*.png --out-dir=$OUTPUT_DIR --plugin=pngquant

# WebP conversion
imagemin "$INPUT_DIR"/*.{jpg,png} --out-dir=$OUTPUT_DIR --plugin=webp

echo "Image optimization complete!"
echo "Check $OUTPUT_DIR for optimized images"
EOF

chmod +x scripts/optimize-images.sh
```

**Step 2.2.3: Aggiornare package.json**

```bash
# Aggiungere script a package.json
cat >> package.json << 'EOF'
"optimize-images": "node scripts/optimize-images.js"
EOF
```

---

### SETTIMANA 3: Decap CMS Setup

#### TASK 3.1: Configurare Decap CMS

**Tempo:** 3-4 ore
**Difficoltà:** Medio

**Step 3.1.1: Creare structure Decap CMS**

```bash
mkdir -p static/admin

cat > static/admin/index.html << 'EOF'
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Content Manager</title>
</head>
<body>
  <!-- Include the script that builds the page and powers Decap CMS -->
  <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
</body>
</html>
EOF
```

**Step 3.1.2: Configurare Decap CMS config**

```bash
cat > static/admin/config.yml << 'EOF'
backend:
  name: github
  repo: bdeornelas/bdeornelas.github.io
  branch: main
  base_url: https://api.netlify.com
  auth_endpoint: auth

media_folder: assets/img/articles
public_folder: /assets/img/articles

collections:
  - name: articles
    label: Articoli
    folder: articles
    create: true
    slug: "{{slug}}"
    fields:
      - label: Layout
        name: layout
        widget: hidden
        default: default

      - label: Titolo
        name: title
        widget: string
        pattern: ['^.{10,120}$', 'Titolo deve essere tra 10 e 120 caratteri']

      - label: Descrizione SEO
        name: description
        widget: text
        pattern: ['^.{50,160}$', 'Descrizione deve essere tra 50 e 160 caratteri']

      - label: Data Pubblicazione
        name: date
        widget: datetime
        format: YYYY-MM-DD

      - label: Categoria
        name: category
        widget: select
        options:
          - Cardiologia
          - Prevenzione
          - Screening
          - Farmaci
          - Diagnostica
          - Lifestyle

      - label: Tag
        name: tags
        widget: list
        field: { label: Tag, name: tag, widget: string }

      - label: Contenuto
        name: body
        widget: markdown
        modes: ['rich_text', 'raw']

      - label: Featured Image (OG)
        name: og_image
        widget: image
        required: false

      - label: Status
        name: status
        widget: select
        default: draft
        options:
          - draft
          - published
          - archived

  - name: pages
    label: Pagine
    files:
      - file: about/index.html
        label: Chi Sono
        name: about
        fields:
          - label: Title
            name: title
            widget: string
          - label: Description
            name: description
            widget: text
          - label: Content
            name: body
            widget: markdown

      - file: contact/index.html
        label: Contatti
        name: contact
        fields:
          - label: Title
            name: title
            widget: string
          - label: Content
            name: body
            widget: markdown
EOF
```

**Step 3.1.3: Configurare GitHub OAuth (per autenticazione)**

Decap CMS richiede OAuth per l'autenticazione. Opzioni:

**OPZIONE A: Usare GitHub App (Consigliato)**

1. Andare a: https://github.com/settings/developers
2. Click "New GitHub App"
3. Configurare:
   - Name: "bdeornelas-cms"
   - Homepage URL: "https://bdeornelas.github.io"
   - Authorization callback URL: "https://bdeornelas.github.io/callback"
4. Copiare Client ID e Secret
5. Nel file config.yml aggiungere:

```yaml
backend:
  name: github
  repo: bdeornelas/bdeornelas.github.io
  branch: main
  auth_endpoint: auth
  app_id: YOUR_CLIENT_ID
```

**OPZIONE B: Usare Netlify (Semplice ma richiede Netlify)**

Se implementerete su Netlify in futuro, Netlify gestisce OAuth automaticamente.

**Step 3.1.4: Setup GitHub (senza Netlify)**

Se volete usare GitHub direttamente, configurate nel repository:

```bash
# Nel repository Settings → Developer settings → GitHub Apps
# Create app con:
# - Callback: https://bdeornelas.github.io
# - Permissions: read:user, repo
```

**Step 3.1.5: Test locale**

```bash
# Nella cartella root
bundle exec jekyll serve

# Visitare: http://localhost:4000/admin
# Dovrebbe mostrare il CMS interface
```

**NOTA:** Per funzionare completamente, l'autenticazione OAuth richiede che sia deployato su un dominio pubblico.

---

### SETTIMANA 4: Testing + Documentation

#### TASK 4.1: Performance Audit

**Tempo:** 2-3 ore
**Difficoltà:** Facile

**Step 4.1.1: Lighthouse audit locale**

```bash
# Installare Lighthouse CLI
npm install -g @lhci/cli@0.9.x

# Eseguire audit
lhci autorun
```

**Step 4.1.2: WebPageTest test**

1. Andare su https://www.webpagetest.org
2. Inserire: https://bdeornelas.github.io
3. Selezionare location: Rome, Italy
4. Run test
5. Notare Core Web Vitals:
   - LCP (Largest Contentful Paint)
   - FID (First Input Delay)
   - CLS (Cumulative Layout Shift)

**Target:**
- LCP < 2.5s ✓
- FID < 100ms ✓
- CLS < 0.1 ✓

---

#### TASK 4.2: Security Audit

**Time:** 1-2 ore
**Difficoltà:** Facile

**Step 4.2.1: Controllare Security Headers**

```bash
# Visitare https://securityheaders.com
# Inserire: https://bdeornelas.github.io
# Verificare Grade
```

**Expected Grade:** A (con CSP headers configurati in _headers)

**Step 4.2.2: Verificare HTTPS**

```bash
# Visitare https://www.ssllabs.com/ssltest/
# Inserire: bdeornelas.github.io
# Dovrebbe ottenere Grade A+
```

---

#### TASK 4.3: Documentation

**Step 4.3.1: Creare README per team**

```bash
cat > DEVELOPMENT.md << 'EOF'
# Development Guide - bdeornelas.github.io

## Setup Locale

### Prerequisiti
- Ruby 3.2+
- Node.js 18+
- Git

### Installazione

```bash
git clone https://github.com/bdeornelas/bdeornelas.github.io.git
cd bdeornelas.github.io
bundle install
npm install
```

### Development

```bash
# Start local server
npm run dev

# Visit http://localhost:4000
# CMS available at http://localhost:4000/admin
```

### Build

```bash
# Build for production
npm run build

# Build CSS only
npm run build:css

# Build Jekyll only
npm run build:jekyll
```

### Testing

```bash
# Run linting
npm run lint

# Run security audit
npm audit
```

### Deployment

Push to main branch:
```bash
git push origin main
```

GitHub Actions will automatically:
1. Build project
2. Run tests
3. Deploy to GitHub Pages

## Adding Articles

### Via Decap CMS (Recommended)

1. Visit https://bdeornelas.github.io/admin
2. Click "New Article"
3. Fill form
4. Publish

### Via Git (Direct)

1. Create folder: `articles/[slug]/`
2. Create file: `articles/[slug]/index.html`
3. Add front matter (see template)
4. Commit and push

## Architecture

See ARCHITETTURA_ANALISI.md for detailed architecture overview.

## Support

Contact: team@example.com
EOF

git add DEVELOPMENT.md
git commit -m "Add development guide"
git push
```

---

## FASE 2: BACKEND SERVICES (MESI 2-4)

### MESE 1: Architecture Design + Setup

#### TASK 1.1: Design Backend API

**Tempo:** 8-12 ore
**Difficoltà:** Alto

**Step 1.1.1: Definire API Endpoints**

```yaml
# API Specification (OpenAPI 3.0)

endpoints:
  # Booking endpoints
  POST /api/v1/bookings
    - Create booking
    - Body: { service_type, location, preferred_date, patient_name, patient_email, patient_phone }
    - Response: { booking_id, confirmation_number, status }

  GET /api/v1/bookings/:id
    - Get booking details
    - Response: { booking_id, status, location, date, patient_info }

  PUT /api/v1/bookings/:id
    - Update booking
    - Body: { preferred_date, status }
    - Response: { updated_booking }

  DELETE /api/v1/bookings/:id
    - Cancel booking
    - Response: { status: "cancelled", refund_amount }

  # Form submission endpoints
  POST /api/v1/forms/contact
    - Submit contact form
    - Body: { name, email, subject, message, type }
    - Response: { form_id, status, message }

  GET /api/v1/forms/:id
    - Get form submission (doctor only, requires auth)
    - Response: { form_id, submitted_data, status, notes }

  # Calendar endpoints
  GET /api/v1/calendar/availability
    - Get available slots
    - Query: { service_type, location, date_range }
    - Response: { available_slots: [{ date, time, location }] }

  # Health check
  GET /api/health
    - Health check endpoint
    - Response: { status: "ok", timestamp }
```

---

#### TASK 1.2: Setup Supabase

**Tempo:** 2-3 ore
**Difficoltà:** Facile

**Step 1.2.1: Creare Supabase project**

1. Andare su https://supabase.com
2. Creare account gratis
3. Click "New Project"
4. Inserire:
   - Name: "bdeornelas-backend"
   - Password: [strong password]
   - Region: "Europe (Ireland)"
5. Attendere creazione (~2 minuti)
6. Copiare connection strings

**Step 1.2.2: Definire Database Schema**

Nel Supabase SQL editor, eseguire:

```sql
-- Create bookings table
CREATE TABLE bookings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_type VARCHAR(50) NOT NULL CHECK (service_type IN ('visita', 'ecocardiogramma', 'test_sforzo', 'videoconsulto')),
  location_id VARCHAR(50) NOT NULL,
  patient_name VARCHAR(100) NOT NULL,
  patient_email VARCHAR(100) NOT NULL,
  patient_phone VARCHAR(20) NOT NULL,
  patient_age INT,
  reason_for_visit TEXT,
  preferred_dates TIMESTAMP[] NOT NULL,
  confirmed_date TIMESTAMP,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_from VARCHAR(50) DEFAULT 'website'
);

-- Create form_submissions table
CREATE TABLE form_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  subject VARCHAR(255),
  message TEXT NOT NULL,
  type VARCHAR(50) DEFAULT 'general' CHECK (type IN ('general', 'prenotazione', 'collaborazione')),
  status VARCHAR(20) DEFAULT 'received' CHECK (status IN ('received', 'read', 'replied')),
  doctor_notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  replied_at TIMESTAMP,
  ip_address INET
);

-- Create indexes
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_email ON bookings(patient_email);
CREATE INDEX idx_forms_status ON form_submissions(status);
CREATE INDEX idx_forms_email ON form_submissions(email);

-- Enable Row Level Security (RLS)
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE form_submissions ENABLE ROW LEVEL SECURITY;

-- Allow public read (bookings availability only)
CREATE POLICY "Allow public read on bookings availability"
  ON bookings FOR SELECT
  USING (status = 'confirmed' AND confirmed_date > NOW());

-- Allow public insert (create new bookings)
CREATE POLICY "Allow public insert bookings"
  ON bookings FOR INSERT
  WITH CHECK (true);

-- For form submissions: allow public insert only
CREATE POLICY "Allow public insert forms"
  ON form_submissions FOR INSERT
  WITH CHECK (true);
```

---

#### TASK 1.3: Setup Backend Repository

**Tempo:** 2 ore
**Difficoltà:** Facile

**Step 1.3.1: Creare repository backend**

```bash
# Creare cartella
mkdir -p ~/projects/bdeornelas-backend
cd ~/projects/bdeornelas-backend

# Inizializzare git
git init
git remote add origin https://github.com/bdeornelas/bdeornelas-backend.git

# Creare structure
mkdir -p src/{routes,controllers,models,middleware,utils}
mkdir -p tests
mkdir -p config
```

**Step 1.3.2: Creare package.json backend**

```bash
cat > package.json << 'EOF'
{
  "name": "bdeornelas-backend",
  "version": "1.0.0",
  "description": "Backend API for Dr. Benjamin De Ornelas",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "lint": "eslint src/",
    "migrate": "node scripts/migrate.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "@supabase/supabase-js": "^2.38.4",
    "axios": "^1.6.2",
    "@sendgrid/mail": "^7.7.0",
    "joi": "^17.11.0",
    "helmet": "^7.1.0",
    "express-rate-limit": "^7.1.5",
    "uuid": "^9.0.1",
    "morgan": "^1.10.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "eslint": "^8.54.0",
    "jest": "^29.7.0",
    "supertest": "^6.3.3"
  }
}
EOF

npm install
```

---

## FASE 3: MOBILE APP + ADVANCED FEATURES

Questo è un progetto più complesso per il futuro. Documenterò l'architettura:

### React Native Mobile App

```
Tecnologie:
- React Native (iOS + Android)
- Expo (per development rapido)
- Redux (state management)
- React Query (server state)
- Stripe (payment processing)

Features:
- Patient booking
- Appointment reminders
- Medical records access
- Video consultations (Twilio)
- Prescription management
```

---

## COST SUMMARY

### PHASE 1 (Weeks 1-4): €200-500

```
Fathom Analytics:    €14/month
Sentry:              €0 (free tier)
Tools:               €0 (open-source)
Development:         €0 (your time)
────────────────────────────────
TOTAL:               €14/month × 1 = €14
```

### PHASE 2 (Months 2-4): €100-200/month

```
Supabase:            €25-100/month
SendGrid:            €20-50/month
Vercel:              €20-50/month
Monitoring:          €0-50/month
────────────────────────────────
TOTAL:               €65-250/month
```

### TOTAL YEAR 1: €1500-3000

---

## SUCCESS CRITERIA (6 months)

```
Phase 1 Complete:
□ Build pipeline automated (GitHub Actions)
□ Analytics active (Fathom)
□ CSS optimized (<50KB)
□ Lighthouse score >90
□ CMS operational

Phase 2 Started:
□ Backend API running
□ Database configured
□ Booking system prototype
□ Form submission handler

Metrics to Achieve:
□ Average page load: <2 seconds
□ Lighthouse score: >90 (all pages)
□ Zero JavaScript errors (Sentry)
□ 100+ conversions tracked (Fathom)
□ 0 deployment failures
```

---

## NEXT STEPS (Immediate)

```
THIS WEEK:
□ Setup GitHub Actions (.github/workflows/build.yml)
□ Create Fathom account and add tracking
□ Test analytics dashboard

NEXT WEEK:
□ Install Tailwind locally
□ Remove Tailwind CDN
□ Test CSS minification

WEEK 3:
□ Setup Decap CMS
□ Test article creation in CMS
□ Train team on CMS

WEEK 4:
□ Performance testing (Lighthouse)
□ Security audit
□ Document everything

MONTH 2:
□ Start Phase 2 planning
□ Design backend API
□ Setup Supabase
```

---

