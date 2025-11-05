#!/usr/bin/env node
/**
 * UpToDate Scraper - Usa sessione esistente
 * ==========================================
 *
 * Usa i cookie della tua sessione Chrome già autenticata.
 *
 * SETUP:
 * 1. Installa: npm install puppeteer
 * 2. Vai su UpToDate nel tuo Chrome ed esegui in Console:
 *    JSON.stringify(document.cookie.split(';').map(c => {
 *      const [name, value] = c.trim().split('=');
 *      return {name, value, domain: '.uptodate.com'};
 *    }))
 * 3. Copia l'output e salvalo in uptodate/cookies.json
 * 4. Esegui: node scraper-with-cookies.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const ARTICLES_FILE = 'articoli_uptodate.json';
const COOKIES_FILE = 'uptodate/cookies.json';
const OUTPUT_DIR = 'uptodate/articles_real';

class CookieBasedScraper {
  constructor() {
    this.browser = null;
    this.page = null;
  }

  async init() {
    console.log('\n' + '='.repeat(60));
    console.log('UPTODATE SCRAPER - COOKIE-BASED');
    console.log('='.repeat(60) + '\n');

    // Crea directory output
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Avvia browser
    console.log('🚀 Avvio browser...');
    this.browser = await puppeteer.launch({
      headless: false, // Mostra browser per debug
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      defaultViewport: { width: 1920, height: 1080 }
    });

    this.page = await this.browser.newPage();
    console.log('✅ Browser avviato');

    // Carica cookies se esistono
    if (fs.existsSync(COOKIES_FILE)) {
      console.log('🍪 Caricamento cookies...');
      const cookies = JSON.parse(fs.readFileSync(COOKIES_FILE, 'utf8'));
      await this.page.setCookie(...cookies);
      console.log(`✅ ${cookies.length} cookies caricati`);
    } else {
      console.log('⚠️  File cookies.json non trovato');
      console.log('\n📋 PER CREARE IL FILE COOKIES:');
      console.log('1. Apri Chrome e vai su uptodate.com (già loggato)');
      console.log('2. Apri Console DevTools (F12)');
      console.log('3. Esegui questo comando:\n');
      console.log(`copy(JSON.stringify(document.cookie.split(';').map(c => {
  const [name, ...rest] = c.trim().split('=');
  return {name, value: rest.join('='), domain: '.uptodate.com', path: '/'};
}), null, 2))`);
      console.log('\n4. Incolla in uptodate/cookies.json');
      console.log('5. Riesegui lo script\n');
    }
  }

  async downloadArticle(article, index, total) {
    const title = article.title;
    const url = article.url_it || article.url_en;

    console.log(`\n[${index}/${total}] ${title}`);
    console.log(`   URL: ${url}`);

    try {
      await this.page.goto(url, {
        waitUntil: 'networkidle0',
        timeout: 30000
      });

      // Attendi contenuto
      await this.page.waitForTimeout(4000);

      // Estrai tutto
      const content = await this.page.evaluate(() => {
        const main = document.querySelector('main') ||
                     document.querySelector('article') ||
                     document.querySelector('[role="main"]') ||
                     document.body;

        return {
          html: main.innerHTML,
          text: main.textContent,
          title: document.querySelector('h1')?.textContent || document.title
        };
      });

      // Salva HTML
      const filename = this.sanitize(title) + '.html';
      const filepath = path.join(OUTPUT_DIR, filename);

      const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>${content.title}</title>
<meta name="url" content="${url}">
<meta name="category" content="${article.category}">
<meta name="topic" content="${article.topic}">
<meta name="downloaded" content="${new Date().toISOString()}">
</head>
<body>
${content.html}
</body>
</html>`;

      fs.writeFileSync(filepath, html, 'utf8');

      // Salva TXT
      const txtpath = filepath.replace('.html', '.txt');
      fs.writeFileSync(txtpath, content.text, 'utf8');

      const size = Math.round(html.length / 1024);
      console.log(`   ✅ ${size}KB salvati`);

      return true;

    } catch (err) {
      console.error(`   ❌ ${err.message}`);
      return false;
    }
  }

  sanitize(str) {
    return str.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_').substring(0, 100);
  }

  async run() {
    try {
      await this.init();

      if (!fs.existsSync(COOKIES_FILE)) {
        console.log('❌ Impossibile continuare senza cookies');
        return;
      }

      // Carica articoli
      const data = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'));
      const articles = data.articles;

      console.log(`\n📥 Scaricamento ${articles.length} articoli...\n`);

      let ok = 0, fail = 0;

      for (let i = 0; i < articles.length; i++) {
        if (await this.downloadArticle(articles[i], i + 1, articles.length)) {
          ok++;
        } else {
          fail++;
        }
        await this.page.waitForTimeout(2000);
      }

      console.log('\n' + '='.repeat(60));
      console.log(`✅ Successo: ${ok}/${articles.length}`);
      console.log(`❌ Falliti: ${fail}`);
      console.log(`📁 ${path.resolve(OUTPUT_DIR)}`);

    } catch (err) {
      console.error('❌', err);
    } finally {
      if (this.browser) {
        await this.browser.close();
        console.log('✅ Browser chiuso\n');
      }
    }
  }
}

(async () => {
  const scraper = new CookieBasedScraper();
  await scraper.run();
})();
