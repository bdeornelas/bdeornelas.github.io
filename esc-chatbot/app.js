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
            // Use individual guideline files from references folder (like /esc command does)
            const response = await fetch(`/references/esc-guidelines-md/${filename}.md`);
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
                // Extract relevant section using LINE NUMBER (like /esc does)
                const section = this.extractRelevantSection(
                    content,
                    fileInfo.searchTerms || [question],
                    fileInfo.filename,
                    fileInfo.lineNumber || 0  // Pass line number for precise extraction
                );
                if (section) {
                    const sourceInfo = fileInfo.lineNumber
                        ? `Section ${fileInfo.section || 'N/A'}, p.${fileInfo.page || 'N/A'}, L${fileInfo.lineNumber}`
                        : fileInfo.filename;
                    extractedContent += `\n\n--- FROM: ${fileInfo.filename}.md (${sourceInfo}) ---\n${section}`;
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
        // This is the key improvement: LLM extracts LINE NUMBERS from TOC (like /esc does)
        const systemPrompt = `Sei un sistema di ricerca per le Linee Guida ESC. Devi trovare le sezioni esatte nel TOC.

ISTRUZIONI CRITICHE:
1. Analizza la domanda e cerca nel TOC le sezioni rilevanti
2. ESTRAI IL NUMERO DI LINEA (L####) da ogni voce del TOC - QUESTO È FONDAMENTALE
3. Il formato TOC è: "Sezione Titolo *(p. XX, LNNNN)*" dove LNNNN è il numero di linea

FILE DISPONIBILI:
${this.guidelineFiles.map(f => `- ${f}.md`).join('\n')}

RISPONDI SOLO con JSON valido in questo formato:
{
  "reasoning": "breve spiegazione della scelta",
  "sections": [
    {
      "filename": "NOME_FILE_SENZA_ESTENSIONE",
      "section": "Numero e titolo sezione",
      "page": 123,
      "lineNumber": 7414,
      "relevance": "perché questa sezione è rilevante"
    }
  ]
}

ESEMPIO di voce TOC:
"9.2.2.4 Aortic root and ascending aortic disease *(p. 67, L7414)*"
→ filename: "2024_Peripheral_Arterial_Aortic", section: "9.2.2.4", page: 67, lineNumber: 7414

⚠️ IMPORTANTE:
- Cerca SEMPRE il numero L#### nel TOC e includilo nel JSON
- Se non trovi L####, usa lineNumber: 0 e il sistema cercherà con keywords
- Massimo 3 sezioni per risposta`;

        const userPrompt = `DOMANDA CLINICA: ${question}

TOC COMPLETO DELLE LINEE GUIDA ESC:
${this.tocData.substring(0, 40000)}

Trova le sezioni rilevanti, ESTRAI I NUMERI DI LINEA (L####), e rispondi con JSON.`;

        try {
            const response = await this.callOpenRouter(systemPrompt, userPrompt, 1500);
            console.log('Raw LLM search response:', response);

            // Parse JSON from response
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const parsed = JSON.parse(jsonMatch[0]);
                console.log('Parsed search result:', parsed);

                // Convert to expected format with lineNumber support
                if (parsed.sections) {
                    parsed.files = parsed.sections.map(s => ({
                        filename: s.filename,
                        lineNumber: s.lineNumber || 0,
                        section: s.section,
                        page: s.page,
                        searchTerms: [s.section, question.split(' ').slice(0, 3).join(' ')]
                    }));
                }
                return parsed;
            }
        } catch (error) {
            console.error('Error in LLM search:', error);
        }

        // Fallback: return empty
        return { files: [], sections: [] };
    }

    extractRelevantSection(content, searchTerms, filename, lineNumber = 0) {
        const lines = content.split('\n');

        // KEY IMPROVEMENT: Use line number directly if provided (like /esc does)
        if (lineNumber > 0) {
            // Direct extraction using line number from TOC - PRECISE like /esc
            const startLine = Math.max(0, lineNumber - 1); // TOC uses 1-based line numbers
            const endLine = Math.min(lines.length, startLine + 150);

            const section = lines.slice(startLine, endLine).join('\n');
            console.log(`✓ PRECISE extraction from ${filename}: lines ${startLine + 1}-${endLine} (L${lineNumber}), ${section.length} chars`);

            return section;
        }

        // Fallback: keyword search (less precise, used when line number not found)
        console.log(`⚠ Fallback: keyword search for ${filename}`);
        const contentLower = content.toLowerCase();

        let bestPosition = 0;
        let bestScore = 0;

        for (const term of searchTerms) {
            const termLower = term.toLowerCase();
            let pos = contentLower.indexOf(termLower);

            while (pos !== -1) {
                let score = 1;
                const nearbyContent = content.substring(Math.max(0, pos - 200), pos + 500).toLowerCase();

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

        const charPosition = bestPosition;
        let foundLine = content.substring(0, charPosition).split('\n').length - 1;

        const startLine = Math.max(0, foundLine - 20);
        const endLine = Math.min(lines.length, foundLine + 130);

        const section = lines.slice(startLine, endLine).join('\n');
        console.log(`Fallback extracted from ${filename}: lines ${startLine}-${endLine}, ${section.length} chars`);

        return section;
    }

    async llmGenerateResponse(question, extractedContent, searchResult) {
        // Build section info for prompt
        const sectionInfo = searchResult.files.map(f =>
            f.lineNumber
                ? `- ${f.filename}.md, Sezione ${f.section || 'N/A'}, p.${f.page || 'N/A'}, L${f.lineNumber}`
                : `- ${f.filename}.md`
        ).join('\n');

        const systemPrompt = `Sei un assistente esperto per le Linee Guida ESC (European Society of Cardiology).

**ISTRUZIONI CRITICHE - WORKFLOW LOCATE → READ → CITE:**

Ti viene fornito il CONTENUTO REALE estratto dalle linee guida ESC con numeri di linea precisi.
Usa SOLO questo contenuto per rispondere. Non inventare nulla.

**REGOLE PER LE CITAZIONI:**
1. **Copia esattamente** il testo dal contenuto fornito - usa virgolette
2. **Indica sempre Classe e Livello**: Class I/IIa/IIb/III, Level A/B/C
3. **Verifica topic-quote match**: la citazione deve corrispondere all'argomento discusso
4. **Includi la fonte esatta**: filename, sezione, pagina, numero di linea (L####)

**FORMATO RISPOSTA RICHIESTO:**

## Raccomandazione ESC

**[Classe X, Livello Y]**: [Sintesi in italiano]

> "[Citazione ESATTA dal testo fornito, in inglese se così nel documento]"

## Contesto Clinico
- **Soglia/Criterio**: [valore specifico se presente]
- **Indicazione**: [quando applicare]
- **Follow-up**: [intervallo se specificato]

## Fonte
**Guideline**: [anno_nome_guideline].md
**Sezione**: [numero e titolo]
**Pagina**: [numero]

**⚠️ REGOLA CRITICA**: MAI separare una citazione dal suo argomento.
Ogni quote DEVE essere sotto l'intestazione corretta.

Rispondi SEMPRE in italiano, ma mantieni le citazioni nella lingua originale del documento.`;

        const userPrompt = `**DOMANDA CLINICA:**
${question}

**SEZIONI IDENTIFICATE:**
${sectionInfo}

**RAGIONAMENTO:**
${searchResult.reasoning || 'N/A'}

**CONTENUTO ESTRATTO (con numeri di linea):**
${extractedContent}

---
Rispondi usando SOLO il contenuto sopra. Cita ESATTAMENTE dal testo. Indica la fonte precisa.`;

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
