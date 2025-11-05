# Guida Deployment su Vercel

Questa guida ti accompagna nel deployment del sito su Vercel in modo semplice e veloce.

## Prerequisiti

- Account Vercel già creato ✓
- Git repository configurato
- Ruby e Bundler installati (per Jekyll)
- Node.js installato (per Parcel)

## Metodo 1: Deployment via Vercel Dashboard (Più Semplice)

### Passo 1: Collega il Repository

1. Vai su [vercel.com](https://vercel.com) e fai login
2. Clicca su **"Add New Project"**
3. Importa il repository GitHub:
   - Se il repo è già su GitHub: selezionalo dalla lista
   - Se non è su GitHub: prima fai push su GitHub (vedi sezione sotto)

### Passo 2: Configura il Progetto

Vercel rileverà automaticamente la configurazione dal file `vercel.json`.

**Settings da verificare:**

- **Framework Preset**: None (lascia vuoto)
- **Build Command**: `bundle install && bundle exec jekyll build && npm run build`
- **Output Directory**: `_site`
- **Install Command**: `gem install bundler && bundle install && npm install`

### Passo 3: Variabili d'Ambiente (Opzionali)

Se hai variabili d'ambiente, aggiungile in **"Environment Variables"**:

```
RUBY_VERSION=2.7.6
NODE_VERSION=18
```

### Passo 4: Deploy

1. Clicca su **"Deploy"**
2. Attendi il completamento del build (circa 2-3 minuti)
3. Il tuo sito sarà live su `https://[nome-progetto].vercel.app`

---

## Metodo 2: Deployment via CLI Vercel (Per Sviluppatori)

### Installazione CLI

```bash
npm install -g vercel
```

### Login

```bash
vercel login
```

### Deploy dal Progetto

```bash
# Prima volta (configura il progetto)
vercel

# Deploy in produzione
vercel --prod
```

La CLI ti farà alcune domande la prima volta:
- **Set up and deploy**: Y
- **Which scope**: seleziona il tuo account
- **Link to existing project**: N (prima volta)
- **Project name**: [scegli un nome]
- **In which directory**: ./

Vercel userà automaticamente `vercel.json` per la configurazione.

---

## Push su GitHub (se necessario)

Se il repository non è ancora su GitHub:

```bash
# Crea un nuovo repository su github.com
# Poi:

git remote add origin https://github.com/[username]/[repo-name].git
git branch -M main
git push -u origin main
```

---

## Configurazione Dominio Custom (Opzionale)

### Aggiungi Dominio su Vercel

1. Vai nel progetto su Vercel Dashboard
2. Settings → Domains
3. Aggiungi il tuo dominio (es. `bdeornelas.it`)
4. Segui le istruzioni per configurare i DNS:

**Opzione A - Nameservers Vercel (Consigliato)**
```
ns1.vercel-dns.com
ns2.vercel-dns.com
```

**Opzione B - Record A/CNAME**
```
A     @     76.76.21.21
CNAME www   cname.vercel-dns.com
```

### Aggiorna URL nel _config.yml

```yaml
url: "https://tuodominio.com"
baseurl: ""
```

Poi commit e push:

```bash
git add _config.yml
git commit -m "Update domain in config"
git push
```

Vercel farà automaticamente il re-deploy.

---

## Workflow Continuo

Una volta configurato, il workflow è automatico:

```bash
# 1. Modifica i file localmente
# 2. Testa in locale (opzionale)
npm run dev

# 3. Commit
git add .
git commit -m "Update content"

# 4. Push su GitHub
git push

# 5. Vercel fa il deploy automatico! 🚀
```

Ogni push su `main` triggera un deploy automatico.
I branch secondari creano deploy di preview.

---

## Troubleshooting

### Build Fails: "Jekyll not found"

Vercel potrebbe non installare correttamente Ruby. Soluzione:

1. Aggiungi file `.ruby-version` nella root:
   ```
   2.7.6
   ```

2. O specifica nel `vercel.json`:
   ```json
   "build": {
     "env": {
       "RUBY_VERSION": "2.7.6"
     }
   }
   ```

### Build Fails: "Bundle install error"

Prova a rimuovere il `Gemfile.lock` e fai rebuild:

```bash
git rm Gemfile.lock
git commit -m "Remove Gemfile.lock"
git push
```

### Assets non caricati correttamente

Verifica che in `_config.yml` il `baseurl` sia vuoto:

```yaml
baseurl: ""
```

### Preview Deploy vs Production

- **Preview**: ogni branch o PR crea un deploy di preview
- **Production**: solo i commit su `main` vanno in produzione

Per specificare il branch di produzione:
Settings → Git → Production Branch → `main`

---

## Monitoring e Analytics

### Performance Monitoring

Vercel fornisce automaticamente:
- **Web Vitals**: Core Web Vitals metrics
- **Real User Monitoring**: tempi di caricamento reali
- **Lighthouse scores**: automatici su ogni deploy

Accedi da: Dashboard → Analytics

### Edge Logs

Per debug in produzione:
Dashboard → Deployments → [seleziona deploy] → Function Logs

---

## Ottimizzazioni Avanzate

### Edge Functions per Redirect Dinamici

Crea `/api/redirect.js`:

```javascript
export default function handler(request) {
  return Response.redirect('https://newurl.com', 301)
}
```

### ISR (Incremental Static Regeneration)

Per articoli che cambiano raramente, configura cache:

```json
{
  "headers": [
    {
      "source": "/articles/:slug",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "s-maxage=3600, stale-while-revalidate=86400"
        }
      ]
    }
  ]
}
```

### Image Optimization

Vercel ottimizza automaticamente le immagini se usi:

```html
<img src="/assets/img/photo.jpg" />
```

Diventa automaticamente servito tramite Vercel Image Optimization.

---

## Best Practices

1. **Branch Strategy**:
   - `main` → Produzione
   - `develop` → Staging
   - Feature branches → Preview deploys

2. **Environment Variables**:
   - Mai committare secrets
   - Usa Vercel Environment Variables

3. **Performance**:
   - Comprimi immagini prima dell'upload
   - Usa webp quando possibile
   - Minimizza CSS/JS (già fatto con Parcel)

4. **SEO**:
   - Sitemap già configurato
   - robots.txt già presente
   - Verifica su Google Search Console dopo deploy

---

## Link Utili

- [Vercel Dashboard](https://vercel.com/dashboard)
- [Vercel Docs - Jekyll](https://vercel.com/docs/frameworks/jekyll)
- [Vercel CLI Docs](https://vercel.com/docs/cli)
- [Vercel Analytics](https://vercel.com/analytics)

---

## Supporto

Se hai problemi:
1. Controlla i logs su Vercel Dashboard
2. Verifica che il build locale funzioni: `npm run vercel-build`
3. Consulta la [Vercel Community](https://github.com/vercel/vercel/discussions)
