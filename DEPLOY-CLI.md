# Deploy CLI - Vercel

Questo documento spiega come fare deploy manuali del sito su Vercel usando la CLI.

## Prerequisiti

1. Account Vercel collegato
2. Node.js installato
3. Autorizzazioni sul progetto benjamindeornelas.github.io

## Metodi di Deploy

### Opzione A - Interattivo (Semplice)

```bash
# 1. Login su Vercel (se necessario)
npx vercel login

# 2. Deploy in produzione
npx vercel --prod
```

### Opzione B - Non Interattivo (Con Token)

```bash
# 1. Creare token da Vercel Dashboard
# Account → Settings → Personal Access Tokens → Create Token

# 2. Esportare il token
export VERCEL_TOKEN="il_tuo_token"

# 3. Deploy forzato
npx vercel --prod --yes --token "$VERCEL_TOKEN"
```

## Script NPM Disponibili

```bash
# Deploy standard (interattivo)
npm run vercel-deploy

# Deploy forzato (non interattivo)
npm run vercel-deploy:force

# Build Jekyll + assets
npm run vercel-build
```

## Verifica del Deploy

Dopo il deploy, controlla:

- **Homepage**: https://benjamindeornelas.it
- **Articoli**: https://benjamindeornelas.it/articles/
- **Articolo esempio**: https://benjamindeornelas.it/articles/aneurisma-aortico/

## Risoluzione Problemi

### Build Fallisce

1. Controlla `vercel.json` per RUBY_VERSION=2.7.6
2. Verifica che `jekyll-paginate-v2` sia installato
3. Controlla che la collection `articles` sia configurata correttamente

### Articoli Non Visibili

1. Verifica che i file .md siano in `articles/`
2. Controlla che abbiano il front matter completo
3. Assicurati che la paginazione sia configurata in `_config.yml`

### CLI Non Trovata

```bash
# Installa Vercel CLI globalmente
npm i -g vercel

# O usa npx senza installazione
npx vercel --version
```

## Deploy Automatico vs Manuale

- **Automatico**: `git push main` triggera automaticamente il deploy
- **Manuale**: CLI per deploy immediati o forzatati
- **Vercel Dashboard**: Per monitorare build e deploy