---
---
// ============================================
// ESC Guidelines Chatbot - RAG with 2-LLM Architecture
// LLM 1: Searches TOC and identifies relevant sections
// LLM 2: Generates response from extracted content
// ============================================

class ESCChatbot {
    constructor() {
        this.model = 'anthropic/claude-sonnet-4'; // Claude Sonnet 4.5
        this.tocData = null;
        this.guidelinesCache = {}; // Cache for loaded guideline files
        // All available guideline files
        this.guidelineFiles = [
            '2020_ACS_NSTE',
            '2020_Adult_Congenital_Heart_Disease',
            '2020_Atrial_Fibrillation',
            '2020_Sports_Cardiology',
            '2021_CVD_Prevention',
            '2021_Cardiac_Pacing_CRT',
            '2021_Heart_Failure',
            '2021_Valvular_Heart_Disease',
            '2022_Cardio_Oncology',
            '2022_Non_Cardiac_Surgery',
            '2022_Pulmonary_Hypertension',
            '2022_Ventricular_Arrhythmias_SCD',
            '2023_Acute_Coronary_Syndromes',
            '2023_CVD_Diabetes',
            '2023_Cardiomyopathies',
            '2023_Cardiomyopathies_Supplementary',
            '2023_Endocarditis',
            '2023_Heart_Failure_Update',
            '2024_Atrial_Fibrillation',
            '2024_Chronic_Coronary_Syndromes',
            '2024_Hypertension',
            '2024_Peripheral_Arterial_Aortic',
            '2025_Dyslipidaemias_Update',
            '2025_Mental_Health_CVD',
            '2025_Myocarditis_Pericarditis',
            '2025_Pregnancy_CVD',
            '2025_Valvular_Heart_Disease'
        ];
        this.init();
    }

    async init() {
        await this.loadTOC();
        this.setupEventListeners();
        this.enableChatbot();
    }

    async loadTOC() {
        try {
            const response = await fetch('/ESC_GUIDELINES_TOC.md');
            this.tocData = await response.text();
            console.log('TOC loaded successfully, length:', this.tocData.length);
        } catch (error) {
            console.error('Error loading TOC:', error);
        }
    }

    async loadGuidelineFile(filename) {
        if (this.guidelinesCache[filename]) {
            return this.guidelinesCache[filename];
        }
        try {
            const response = await fetch(`/claude-project-files/${filename}.md`);
            if (!response.ok) throw new Error(`File not found: ${filename}`);
            const content = await response.text();
            this.guidelinesCache[filename] = content;
            console.log(`Loaded ${filename}.md (${content.length} chars)`);
            return content;
        } catch (error) {
            console.error(`Error loading ${filename}.md:`, error);
            return null;
        }
    }

    setupEventListeners() {
        const form = document.getElementById('chat-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        const textarea = document.getElementById('chat-input');
        textarea.addEventListener('input', () => this.autoResize(textarea));
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });

        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                textarea.value = btn.dataset.question;
                this.autoResize(textarea);
                form.dispatchEvent(new Event('submit'));
            });
        });
    }

    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    enableChatbot() {
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-button');
        input.disabled = false;
        sendBtn.disabled = false;
        input.placeholder = 'Fai una domanda sulle linee guida ESC...';

        const statusBadge = document.getElementById('status-badge');
        statusBadge.innerHTML = '<span class="badge-dot"></span> Pronto';
        statusBadge.className = 'badge badge-success';
    }

    async sendMessage() {
        const textarea = document.getElementById('chat-input');
        const message = textarea.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        textarea.value = '';
        this.autoResize(textarea);
        textarea.disabled = true;
        document.getElementById('send-button').disabled = true;

        const loadingId = this.addLoadingMessage();

        try {
            const response = await this.queryESCGuidelines(message);
            this.removeMessage(loadingId);
            this.addMessage(response, 'assistant');
        } catch (error) {
            console.error('Error:', error);
            this.removeMessage(loadingId);
            this.addMessage('Errore: ' + error.message, 'assistant');
        } finally {
            textarea.disabled = false;
            document.getElementById('send-button').disabled = false;
            textarea.focus();
        }
    }

    async queryESCGuidelines(question) {
        console.log('=== Starting 2-LLM RAG query ===');
        console.log('Question:', question);

        // ========================================
        // PHASE 1: LLM searches TOC to find relevant sections
        // ========================================
        console.log('Phase 1: LLM searching TOC...');
        this.updateLoadingMessage('Analizzo la domanda e cerco nelle linee guida...');

        const searchResult = await this.llmSearchTOC(question);
        console.log('LLM search result:', searchResult);

        if (!searchResult.files || searchResult.files.length === 0) {
            return "Non ho trovato sezioni rilevanti nelle linee guida ESC per questa domanda. Prova a riformulare la domanda con termini più specifici.";
        }

        // ========================================
        // PHASE 2: Load identified files and extract content
        // ========================================
        console.log('Phase 2: Loading files:', searchResult.files);
        this.updateLoadingMessage('Estraggo il contenuto rilevante...');

        let extractedContent = '';
        for (const fileInfo of searchResult.files) {
            const content = await this.loadGuidelineFile(fileInfo.filename);
            if (content) {
                // Extract relevant section based on search terms
                const section = this.extractRelevantSection(content, fileInfo.searchTerms || [question], fileInfo.filename);
                if (section) {
                    extractedContent += `\n\n--- FROM: ${fileInfo.filename}.md ---\n${section}`;
                }
            }
        }

        if (!extractedContent) {
            return "Ho identificato le linee guida rilevanti ma non sono riuscito a estrarre il contenuto. Riprova.";
        }

        // Limit content to avoid token limits
        if (extractedContent.length > 20000) {
            extractedContent = extractedContent.substring(0, 20000) + '\n\n[...contenuto troncato...]';
        }

        console.log('Extracted content length:', extractedContent.length);

        // ========================================
        // PHASE 3: LLM generates response from extracted content
        // ========================================
        console.log('Phase 3: LLM generating response...');
        this.updateLoadingMessage('Genero la risposta...');

        const response = await this.llmGenerateResponse(question, extractedContent, searchResult);
        return response;
    }

    async llmSearchTOC(question) {
        const systemPrompt = `Sei un sistema di ricerca per le Linee Guida ESC (European Society of Cardiology).

Il tuo compito è analizzare la domanda dell'utente e identificare quali file delle linee guida contengono informazioni rilevanti.

FILE DISPONIBILI:
${this.guidelineFiles.map(f => `- ${f}.md`).join('\n')}

ISTRUZIONI:
1. Analizza la domanda e identifica l'argomento principale
2. Identifica i file più rilevanti (massimo 3)
3. Per ogni file, indica i termini chiave da cercare

RISPONDI SOLO con JSON valido in questo formato:
{
  "reasoning": "breve spiegazione della scelta",
  "files": [
    {"filename": "NOME_FILE_SENZA_ESTENSIONE", "searchTerms": ["termine1", "termine2"]}
  ]
}

ESEMPI:
- "mavacamten" → 2023_Cardiomyopathies (farmaco per HCM)
- "fibrillazione atriale" → 2024_Atrial_Fibrillation (più recente)
- "scompenso cardiaco" → 2021_Heart_Failure, 2023_Heart_Failure_Update`;

        const userPrompt = `DOMANDA: ${question}

TOC DELLE LINEE GUIDA:
${this.tocData.substring(0, 30000)}

Identifica i file rilevanti e rispondi SOLO con JSON valido.`;

        try {
            const response = await this.callOpenRouter(systemPrompt, userPrompt, 1000);

            // Parse JSON from response
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const parsed = JSON.parse(jsonMatch[0]);
                console.log('Parsed search result:', parsed);
                return parsed;
            }
        } catch (error) {
            console.error('Error in LLM search:', error);
        }

        // Fallback: return empty
        return { files: [] };
    }

    extractRelevantSection(content, searchTerms, filename) {
        const lines = content.split('\n');
        const contentLower = content.toLowerCase();

        // Find the best starting position based on search terms
        let bestPosition = 0;
        let bestScore = 0;

        for (const term of searchTerms) {
            const termLower = term.toLowerCase();
            let pos = contentLower.indexOf(termLower);

            while (pos !== -1) {
                // Score based on context (prefer starts of sections)
                let score = 1;
                const nearbyContent = content.substring(Math.max(0, pos - 200), pos + 500).toLowerCase();

                // Bonus for being near recommendation markers
                if (nearbyContent.includes('class i') || nearbyContent.includes('class ii') || nearbyContent.includes('level')) {
                    score += 5;
                }
                if (nearbyContent.includes('recommendation')) {
                    score += 3;
                }

                if (score > bestScore) {
                    bestScore = score;
                    bestPosition = pos;
                }

                pos = contentLower.indexOf(termLower, pos + 1);
            }
        }

        // Extract ~300 lines around the best position
        const charPosition = bestPosition;
        let lineNumber = content.substring(0, charPosition).split('\n').length - 1;

        const startLine = Math.max(0, lineNumber - 50);
        const endLine = Math.min(lines.length, lineNumber + 250);

        const section = lines.slice(startLine, endLine).join('\n');
        console.log(`Extracted from ${filename}: lines ${startLine}-${endLine}, ${section.length} chars`);

        return section;
    }

    async llmGenerateResponse(question, extractedContent, searchResult) {
        const systemPrompt = `Sei un assistente esperto per le Linee Guida ESC (European Society of Cardiology).

**ISTRUZIONI CRITICHE:**

Ti viene fornito il CONTENUTO REALE estratto dalle linee guida ESC. Usa SOLO questo contenuto per rispondere.

1. **Cita esattamente**: Usa citazioni dirette dal testo fornito
2. **Indica classe e livello**: Classe di Raccomandazione (I/IIa/IIb/III) e Livello di Evidenza (A/B/C)
3. **Specifica la fonte**: Anno, sezione, pagina

**FORMATO RISPOSTA:**

## Raccomandazione ESC

**[Classe X, Livello Y]**: [Sintesi]

> "[Citazione esatta dal testo]"

## Dettagli Clinici
- **Criteri/Soglie**: [valori specifici]
- **Indicazioni**: [quando applicare]
- **Follow-up**: [intervalli di sorveglianza]

## Fonte
**Linea Guida**: [anno e titolo]

**IMPORTANTE**: Rispondi SEMPRE in italiano. Se il contenuto fornito non contiene informazioni sufficienti, indicalo chiaramente.`;

        const userPrompt = `**DOMANDA CLINICA:**
${question}

**FILE IDENTIFICATI:**
${searchResult.files.map(f => f.filename).join(', ')}

**RAGIONAMENTO DELLA RICERCA:**
${searchResult.reasoning || 'N/A'}

**CONTENUTO ESTRATTO DALLE LINEE GUIDA ESC:**
${extractedContent}

---
Rispondi alla domanda usando ESCLUSIVAMENTE il contenuto sopra. Cita esattamente dal testo.`;

        return await this.callOpenRouter(systemPrompt, userPrompt, 2500);
    }

    async callOpenRouter(systemPrompt, userPrompt, maxTokens = 2500) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: this.model,
                messages: [
                    { role: 'system', content: systemPrompt },
                    { role: 'user', content: userPrompt }
                ],
                temperature: 0.2,
                max_tokens: maxTokens
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'API request failed');
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }

    updateLoadingMessage(text) {
        const loadingMsg = document.querySelector('.loading-message .message-text span');
        if (loadingMsg) {
            loadingMsg.textContent = text;
        }
    }

    addMessage(content, role) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageId = 'msg-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.id = messageId;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'assistant'
            ? '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
            : '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `
            <div class="message-header">
                <span class="message-author">${role === 'assistant' ? 'ESC Assistant' : 'Tu'}</span>
                <span class="message-time">${new Date().toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}</span>
            </div>
            <div class="message-text">${this.formatMessage(content)}</div>
        `;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageId;
    }

    addLoadingMessage() {
        const messagesContainer = document.getElementById('chat-messages');
        const messageId = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message loading-message';
        messageDiv.id = messageId;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-header"><span class="message-author">ESC Assistant</span></div>
                <div class="message-text">
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                    <span style="color:#9ca3af;font-size:0.875rem;margin-left:8px">Cerco nelle linee guida...</span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return messageId;
    }

    removeMessage(messageId) {
        document.getElementById(messageId)?.remove();
    }

    formatMessage(content) {
        return content
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^### (.*$)/gim, '<h4>$1</h4>')
            .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ESCChatbot();
});
