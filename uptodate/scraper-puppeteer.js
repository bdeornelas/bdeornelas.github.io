#!/usr/bin/env node
/**
 * UpToDate Scraper with Puppeteer
 * ================================
 *
 * Scarica articoli patient education da UpToDate usando autenticazione.
 *
 * Requisiti:
 * npm install puppeteer
 *
 * Uso:
 * node scraper-puppeteer.js [--headless]
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Configurazione
const CONFIG_FILE = 'config.json';
const ARTICLES_FILE = 'articoli_uptodate.json';
const OUTPUT_DIR = 'uptodate/articles_authenticated';

class UpToDateScraper {
  constructor(headless = false) {
    this.headless = headless;
    this.browser = null;
    this.page = null;
    this.config = null;
    this.authenticated = false;
  }

  async init() {
    console.log('\n' + '='.repeat(60));
    console.log('UPTODATE PUPPETEER SCRAPER');
    console.log('='.repeat(60) + '\n');

    // Carica configurazione
    this.config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    console.log('✅ Configurazione caricata');

    // Crea directory output
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // Avvia browser
    console.log('🚀 Avvio browser...');
    this.browser = await puppeteer.launch({
      headless: this.headless ? 'new' : false,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1920,1080'
      ],
      defaultViewport: {
        width: 1920,
        height: 1080
      }
    });

    this.page = await this.browser.newPage();

    // Imposta user agent
    await this.page.setUserAgent(this.config.user_agent);

    // Rimuovi flag webdriver
    await this.page.evaluateOnNewDocument(() => {
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      });
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
      });
      Object.defineProperty(navigator, 'languages', {
        get: () => ['it-IT', 'it', 'en-US', 'en']
      });
    });

    console.log('✅ Browser avviato');
  }

  async login() {
    console.log('\n🔐 Autenticazione UpToDate...');

    try {
      const loginUrl = this.config.institution_login_url || 'https://www.uptodate.com/login';
      console.log(`   → Navigazione a: ${loginUrl}`);

      await this.page.goto(loginUrl, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      // Screenshot della pagina di login per debug
      await this.page.screenshot({ path: 'uptodate/login_page.png' });
      console.log('   📸 Screenshot salvato: login_page.png');

      // Attendi che la pagina carichi completamente
      await this.page.waitForTimeout(2000);

      // Cerca campi di login con diversi selettori
      console.log('   → Ricerca campi di login...');

      // Prova diversi selettori comuni per username
      const usernameSelectors = [
        'input[name="username"]',
        'input[name="email"]',
        'input[type="email"]',
        'input[id*="username" i]',
        'input[id*="email" i]',
        'input[placeholder*="email" i]',
        'input[placeholder*="username" i]'
      ];

      let usernameField = null;
      for (const selector of usernameSelectors) {
        try {
          usernameField = await this.page.$(selector);
          if (usernameField) {
            console.log(`   ✓ Campo username trovato: ${selector}`);
            break;
          }
        } catch (e) {
          continue;
        }
      }

      if (!usernameField) {
        console.log('   ⚠️  Campo username non trovato con selettori standard');
        console.log('   → Provo a cercare tutti gli input...');

        // Trova tutti gli input e mostra i loro attributi
        const inputs = await this.page.$$('input');
        console.log(`   → Trovati ${inputs.length} input nella pagina`);

        // Usa il primo input di tipo text o email
        for (const input of inputs) {
          const type = await input.evaluate(el => el.type);
          if (type === 'text' || type === 'email') {
            usernameField = input;
            console.log(`   ✓ Uso primo input tipo ${type}`);
            break;
          }
        }
      }

      if (!usernameField) {
        throw new Error('Campo username non trovato');
      }

      // Inserisci username
      await usernameField.click({ clickCount: 3 });
      await usernameField.type(this.config.username, { delay: 50 });
      console.log('   ✓ Username inserito');

      // Cerca campo password
      const passwordSelectors = [
        'input[name="password"]',
        'input[type="password"]',
        'input[id*="password" i]'
      ];

      let passwordField = null;
      for (const selector of passwordSelectors) {
        try {
          passwordField = await this.page.$(selector);
          if (passwordField) {
            console.log(`   ✓ Campo password trovato: ${selector}`);
            break;
          }
        } catch (e) {
          continue;
        }
      }

      if (!passwordField) {
        // Cerca tutti gli input password
        const inputs = await this.page.$$('input[type="password"]');
        if (inputs.length > 0) {
          passwordField = inputs[0];
          console.log('   ✓ Uso primo input type=password');
        }
      }

      if (!passwordField) {
        throw new Error('Campo password non trovato');
      }

      // Inserisci password
      await passwordField.click({ clickCount: 3 });
      await passwordField.type(this.config.password, { delay: 50 });
      console.log('   ✓ Password inserita');

      // Screenshot prima del submit
      await this.page.screenshot({ path: 'uptodate/before_submit.png' });

      // Cerca bottone submit
      const submitSelectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Log in")',
        'button:has-text("Sign in")',
        'button[class*="login" i]',
        'button[class*="submit" i]'
      ];

      let submitButton = null;
      for (const selector of submitSelectors) {
        try {
          submitButton = await this.page.$(selector);
          if (submitButton) {
            console.log(`   ✓ Bottone submit trovato: ${selector}`);
            break;
          }
        } catch (e) {
          continue;
        }
      }

      if (!submitButton) {
        // Cerca tutti i button
        const buttons = await this.page.$$('button');
        if (buttons.length > 0) {
          submitButton = buttons[buttons.length - 1]; // Prendi ultimo button
          console.log('   ✓ Uso ultimo button della pagina');
        }
      }

      if (!submitButton) {
        throw new Error('Bottone submit non trovato');
      }

      // Click submit
      console.log('   → Invio form...');
      await Promise.all([
        this.page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 }).catch(() => {}),
        submitButton.click()
      ]);

      await this.page.waitForTimeout(3000);

      // Verifica login
      const currentUrl = this.page.url();
      console.log(`   → URL corrente: ${currentUrl}`);

      if (!currentUrl.includes('login')) {
        console.log('✅ Login completato!');
        this.authenticated = true;
        await this.page.screenshot({ path: 'uptodate/after_login.png' });
        return true;
      } else {
        console.log('   ⚠️  Possibile fallimento login');
        await this.page.screenshot({ path: 'uptodate/login_failed.png' });
        return false;
      }

    } catch (error) {
      console.error(`   ❌ Errore durante login: ${error.message}`);
      await this.page.screenshot({ path: 'uptodate/login_error.png' });
      return false;
    }
  }

  async downloadArticle(article, index, total) {
    const title = article.title;
    const url = article.url_it || article.url_en;

    console.log(`\n[${index}/${total}] ${title}`);
    console.log(`   URL: ${url}`);

    try {
      // Naviga all'articolo
      await this.page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 30000
      });

      // Attendi che il contenuto carichi
      await this.page.waitForTimeout(3000);

      // Attendi elemento main o article
      try {
        await this.page.waitForSelector('main, article', { timeout: 10000 });
      } catch (e) {
        console.log('   ⚠️  Timeout attesa contenuto');
      }

      // Estrai contenuto
      const content = await this.page.evaluate(() => {
        // Prova main
        let contentEl = document.querySelector('main');
        if (!contentEl) {
          contentEl = document.querySelector('article');
        }
        if (!contentEl) {
          contentEl = document.querySelector('body');
        }

        return {
          html: contentEl ? contentEl.innerHTML : document.body.innerHTML,
          title: document.querySelector('h1') ? document.querySelector('h1').textContent : document.title,
          textContent: contentEl ? contentEl.textContent : document.body.textContent
        };
      });

      // Salva file
      const filename = this.sanitizeFilename(title) + '.html';
      const filepath = path.join(OUTPUT_DIR, filename);

      const html = `<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>${content.title}</title>
    <meta name="source" content="UpToDate Patient Education">
    <meta name="url" content="${url}">
    <meta name="download_date" content="${new Date().toISOString()}">
    <meta name="category" content="${article.category}">
</head>
<body>
<h1>${content.title}</h1>
<p><em>Fonte: <a href="${url}">${url}</a></em></p>
<p><em>Categoria: ${article.category}</em></p>
<p><em>Scaricato: ${new Date().toLocaleString('it-IT')}</em></p>
<hr>
${content.html}
</body>
</html>`;

      fs.writeFileSync(filepath, html, 'utf8');

      // Salva anche il testo puro per analisi
      const textFilepath = filepath.replace('.html', '.txt');
      fs.writeFileSync(textFilepath, content.textContent, 'utf8');

      console.log(`   ✅ Salvato: ${filename} (${Math.round(html.length / 1024)}KB)`);

      // Pausa tra richieste
      await this.page.waitForTimeout(this.config.delay_between_requests * 1000);

      return true;

    } catch (error) {
      console.error(`   ❌ Errore: ${error.message}`);
      return false;
    }
  }

  async downloadAllArticles() {
    // Carica lista articoli
    const articlesData = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'));
    const articles = articlesData.articles;

    console.log(`\n📥 Download di ${articles.length} articoli...\n`);

    let successful = 0;
    let failed = 0;

    for (let i = 0; i < articles.length; i++) {
      const success = await this.downloadArticle(articles[i], i + 1, articles.length);
      if (success) {
        successful++;
      } else {
        failed++;
      }
    }

    console.log('\n' + '='.repeat(60));
    console.log(`✅ Completati: ${successful}/${articles.length}`);
    console.log(`❌ Falliti: ${failed}`);
    console.log(`📁 Directory: ${path.resolve(OUTPUT_DIR)}`);
    console.log('='.repeat(60));
  }

  sanitizeFilename(title) {
    return title
      .replace(/[<>:"/\\|?*]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 100);
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      console.log('\n✅ Browser chiuso');
    }
  }

  async run() {
    try {
      await this.init();

      if (!await this.login()) {
        console.log('\n❌ Login fallito. Impossibile continuare.');
        return;
      }

      await this.downloadAllArticles();

    } catch (error) {
      console.error(`\n❌ Errore: ${error.message}`);
      console.error(error.stack);
    } finally {
      await this.close();
    }
  }
}

// Main
(async () => {
  const headless = process.argv.includes('--headless');
  const scraper = new UpToDateScraper(headless);
  await scraper.run();
})();
