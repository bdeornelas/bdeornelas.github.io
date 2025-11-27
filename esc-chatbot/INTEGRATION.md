# Guida Integrazione Chatbot ESC nel Sito

## 🎯 Obiettivo

Integrare il chatbot ESC Guidelines nella home page del sito per dare visibilità al nuovo tool AI.

## 📋 Passi di Integrazione

### 1. Aggiungere Sezione alla Homepage

**File da modificare**: `index.html`

**Dove inserire**: Dopo la sezione "Articoli" (circa linea 38)

**Codice da aggiungere**:

```html
<!-- Copia il contenuto da chatbot-section.html -->
```

Oppure usa un include Jekyll:

```html
{% include esc-chatbot-section.html %}
```

E crea il file `_includes/esc-chatbot-section.html` con il contenuto da `chatbot-section.html`.

### 2. Aggiungere Link al Menu di Navigazione

**File da modificare**: `_layouts/default.html` o il file che contiene il menu

**Esempio**:

```html
<nav>
  <a href="/">Home</a>
  <a href="/articles/">Articoli</a>
  <a href="/esc-chatbot/">🤖 ESC Chatbot</a> <!-- NUOVO -->
  <a href="/about/">Chi Sono</a>
  <a href="/contact/">Contatti</a>
</nav>
```

### 3. Verificare Path Relativi

Assicurati che tutti i link funzionino:

- `/esc-chatbot/` → Pagina chatbot
- `/esc-chatbot/README.md` → Documentazione (opzionale, può redirigere a GitHub)
- `../ESC_GUIDELINES_TOC.md` → TOC file (verificare path in app.js)

### 4. Testare Localmente

```bash
# Se usi Jekyll
bundle exec jekyll serve

# Naviga a http://localhost:4000/esc-chatbot/
```

### 5. Deploy su GitHub Pages

```bash
git add esc-chatbot/
git commit -m "Add: ESC Guidelines AI Chatbot"
git push origin main
```

GitHub Pages ricostruirà automaticamente il sito in ~2-3 minuti.

## 🎨 Personalizzazione Styling

### Opzione A: Usa Stili Esistenti del Sito

Se il tuo sito usa già Tailwind CSS (come sembra dall'index.html), puoi:

1. Aprire `esc-chatbot/style.css`
2. Rimuovere gli stili che confliggono
3. Aggiungere classi Tailwind all'HTML del chatbot

### Opzione B: Mantieni Stili Separati

Lo stile attuale è self-contained e non dovrebbe confliggere. Testare visivamente.

### Opzione C: Unifica Variabili CSS

Sincronizza le variabili CSS tra il sito e il chatbot:

```css
/* In esc-chatbot/style.css - allinea con il tema del sito */
:root {
    --primary-color: #0ea5e9; /* sky-500 del sito */
    --secondary-color: #8b5cf6; /* violet-500 del sito */
}
```

## 🧪 Testing Checklist

Prima di rilasciare, verifica:

- [ ] La pagina `/esc-chatbot/` si carica correttamente
- [ ] Il TOC viene caricato (controlla console browser)
- [ ] Il modal settings funziona
- [ ] Puoi salvare l'API key
- [ ] I bottoni esempio funzionano
- [ ] L'input textarea funziona (Enter, Shift+Enter)
- [ ] La chiamata OpenRouter funziona (con API key valida)
- [ ] Le risposte sono formattate correttamente
- [ ] Il design è responsive (mobile, tablet, desktop)
- [ ] Nessun errore nella console JavaScript

## 📱 Responsiveness

Il chatbot è già responsive, ma verifica su:

- **Desktop** (>1024px): Sidebar visibile
- **Tablet** (768px-1024px): Sidebar ristretta
- **Mobile** (<768px): Sidebar nascosta

## 🔐 Configurazione OpenRouter

Gli utenti dovranno:

1. Visitare https://openrouter.ai/keys
2. Creare account (se non ce l'hanno)
3. Generare API key
4. Inserirla nel chatbot

**Costo stimato**: ~$0.02-0.10 per conversazione complessa con Claude 3.5 Sonnet.

## 📊 Analytics (Opzionale)

Se vuoi tracciare l'uso del chatbot:

```javascript
// Aggiungi in app.js dopo sendMessage()
if (window.gtag) {
    gtag('event', 'esc_chatbot_query', {
        'question_length': message.length,
        'model': this.model
    });
}
```

## 🚀 Feature Flags (Opzionale)

Per rilasciare il chatbot gradualmente:

```javascript
// In app.js
const CHATBOT_ENABLED = true; // Cambia a false per disabilitare

if (!CHATBOT_ENABLED) {
    document.querySelector('.chat-input-container').innerHTML = `
        <div class="text-center p-8">
            <p>Il chatbot è temporaneamente non disponibile. Riprova più tardi.</p>
        </div>
    `;
}
```

## 📝 SEO Optimization

Aggiungi meta tags in `esc-chatbot/index.html`:

```html
<head>
    <!-- ... existing tags ... -->

    <!-- SEO -->
    <meta name="description" content="Chatbot AI per interrogare le Linee Guida ESC con citazioni automatiche. Oltre 50 guidelines ESC 2020-2025.">
    <meta name="keywords" content="ESC Guidelines, Linee Guida ESC, Cardiologia, AI Chatbot, Claude, OpenRouter">

    <!-- Open Graph -->
    <meta property="og:title" content="ESC Guidelines AI Assistant">
    <meta property="og:description" content="Interroga le Linee Guida ESC con un assistente AI intelligente">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://bdeornelas.github.io/esc-chatbot/">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="ESC Guidelines AI Assistant">
    <meta name="twitter:description" content="Interroga le Linee Guida ESC con citazioni automatiche">
</head>
```

## 🐛 Troubleshooting Comune

### Problema: TOC non viene caricato

**Causa**: Path errato in `app.js`

**Fix**:

```javascript
// In app.js, loadTOC()
const response = await fetch('/ESC_GUIDELINES_TOC.md'); // Prova vari path
```

### Problema: CORS error sul TOC

**Causa**: GitHub Pages potrebbe bloccare fetch locale

**Fix**: Converti TOC in JSON e include come modulo:

```bash
# Crea uno script per convertire TOC in JSON
node scripts/toc-to-json.js
```

### Problema: OpenRouter API non funziona

**Causa**: API key non valida o credito esaurito

**Fix**:

1. Verifica API key su OpenRouter
2. Controlla credito account
3. Vedi Network tab in DevTools per dettagli errore

## 🎁 Bonus Features da Aggiungere

### 1. Condividi Conversazione

```javascript
// In app.js
shareConversation() {
    const messages = Array.from(document.querySelectorAll('.message'));
    const text = messages.map(m => m.innerText).join('\n\n');
    navigator.clipboard.writeText(text);
    alert('Conversazione copiata negli appunti!');
}
```

### 2. Export PDF

```javascript
// Usa libreria jsPDF
exportToPDF() {
    const doc = new jsPDF();
    const messages = this.getConversationText();
    doc.text(messages, 10, 10);
    doc.save('esc-conversation.pdf');
}
```

### 3. Voice Input

```javascript
// Web Speech API
startVoiceInput() {
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'it-IT';
    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById('chat-input').value = text;
    };
    recognition.start();
}
```

## 📞 Supporto

Per problemi o domande:

- **GitHub Issues**: [bdeornelas.github.io/issues](https://github.com/bdeornelas/bdeornelas.github.io/issues)
- **Email**: Via GitHub profile

---

**Buona integrazione! 🚀**
