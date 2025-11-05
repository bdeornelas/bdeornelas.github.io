#!/usr/bin/env node
/**
 * UpToDate Scraper - Usa il tuo Chrome dove sei già loggato
 * ==========================================================
 *
 * Usa direttamente il tuo profilo Chrome esistente.
 * CHIUDI CHROME prima di eseguire questo script!
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const os = require('os');

const ARTICLES_FILE = 'articoli_uptodate.json';
const OUTPUT_DIR = 'uptodate/articles_real';

// Path profilo Chrome su macOS
const CHROME_USER_DATA = path.join(os.homedir(), 'Library/Application Support/Google/Chrome');

class UserProfileScraper {
  async run() {
    console.log('\n' + '='.repeat(60));
    console.log('UPTODATE SCRAPER - USA TUO PROFILO CHROME');
    console.log('='.repeat(60) + '\n');

    // Verifica che Chrome sia chiuso
    console.log('⚠️  IMPORTANTE: Chiudi Chrome completamente prima di continuare!');
    console.log('   Premi CTRL+C per annullare, o attendi 5 secondi...\n');

    await new Promise(resolve => setTimeout(resolve, 5000));

    // Crea output dir
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    let browser, page;

    try {
      console.log('🚀 Avvio Chrome con tuo profilo...');
      browser = await puppeteer.launch({
        headless: false,
        userDataDir: CHROME_USER_DATA,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-blink-features=AutomationControlled'
        ],
        defaultViewport: { width: 1920, height: 1080 }
      });

      page = await browser.newPage();
      console.log('✅ Browser avviato con tua sessione\n');

      // Test accesso UpToDate
      console.log('🔍 Verifica accesso UpToDate...');
      await page.goto('https://www.uptodate.com', {waitUntil: 'networkidle0'});
      await new Promise(resolve => setTimeout(resolve, 2000));

      const isLoggedIn = await page.evaluate(() => {
        // Cerca segni di autenticazione
        return !document.body.textContent.includes('Log in') ||
               document.body.textContent.includes('My Account') ||
               document.querySelector('[data-test*="user"]') !== null;
      });

      if (!isLoggedIn) {
        console.log('⚠️  Potrebbe non essere autenticato. Verifica manualmente.');
        console.log('   Browser rimarrà aperto - fai login se necessario.');
        console.log('   Poi premi INVIO qui per continuare...\n');
        await new Promise(resolve => process.stdin.once('data', resolve));
      } else {
        console.log('✅ Sessione autenticata!\n');
      }

      // Carica lista articoli
      const data = JSON.parse(fs.readFileSync(ARTICLES_FILE, 'utf8'));
      const articles = data.articles;

      console.log(`📥 Download ${articles.length} articoli...\n`);

      let success = 0, failed = 0;

      for (let i = 0; i < articles.length; i++) {
        const article = articles[i];
        // Usa sempre URL inglese perché quello italiano non funziona
        const url = article.url_en;

        console.log(`[${i+1}/${articles.length}] ${article.title}`);

        try {
          await page.goto(url, {waitUntil: 'networkidle0', timeout: 30000});
          await new Promise(resolve => setTimeout(resolve, 3000));

          // Estrai contenuto
          const content = await page.evaluate(() => {
            const main = document.querySelector('main') ||
                         document.querySelector('article') ||
                         document.querySelector('[role="main"]') ||
                         document.body;

            return {
              html: main.innerHTML,
              text: main.innerText,
              title: document.querySelector('h1')?.innerText || document.title
            };
          });

          // Verifica che ci sia contenuto significativo
          if (content.text.length < 100) {
            throw new Error('Contenuto troppo breve - possibile errore');
          }

          // Salva
          const filename = article.title.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, '_').substring(0, 100);

          const htmlPath = path.join(OUTPUT_DIR, filename + '.html');
          const txtPath = path.join(OUTPUT_DIR, filename + '.txt');

          const html = `<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>${content.title}</title>
<meta name="source-url" content="${url}">
<meta name="category" content="${article.category}">
<meta name="topic" content="${article.topic}">
<meta name="downloaded" content="${new Date().toISOString()}">
</head>
<body>
<h1>${content.title}</h1>
<p><em>Fonte: <a href="${url}">${url}</a></em></p>
<p><em>Categoria: ${article.category} | Topic: ${article.topic}</em></p>
<hr>
${content.html}
</body>
</html>`;

          fs.writeFileSync(htmlPath, html, 'utf8');
          fs.writeFileSync(txtPath, content.text, 'utf8');

          console.log(`  ✅ ${Math.round(content.text.length/1024)}KB\n`);
          success++;

        } catch (err) {
          console.log(`  ❌ ${err.message}\n`);
          failed++;
        }

        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      console.log('='.repeat(60));
      console.log(`✅ Successo: ${success}/${articles.length}`);
      console.log(`❌ Falliti: ${failed}`);
      console.log(`📁 Directory: ${path.resolve(OUTPUT_DIR)}`);
      console.log('='.repeat(60) + '\n');

    } catch (err) {
      console.error('❌ Errore:', err.message);
    } finally {
      if (browser) {
        await browser.close();
        console.log('✅ Browser chiuso\n');
      }
    }
  }
}

(async () => {
  const scraper = new UserProfileScraper();
  await scraper.run();
})();
