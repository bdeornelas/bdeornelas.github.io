---
---
// ============================================
// ESC Guidelines Chatbot - RAG Implementation
// ============================================

class ESCChatbot {
    constructor() {
        this.model = 'anthropic/claude-3.5-sonnet';
        this.tocData = null;
        this.guidelinesCache = {}; // Cache for loaded guideline files
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
            console.log('TOC loaded successfully');
        } catch (error) {
            console.error('Error loading TOC:', error);
        }
    }

    async loadGuidelineFile(year) {
        if (this.guidelinesCache[year]) {
            return this.guidelinesCache[year];
        }
        try {
            const response = await fetch(`/claude-project-files/ESC_${year}.md`);
            if (!response.ok) throw new Error(`File not found for year ${year}`);
            const content = await response.text();
            this.guidelinesCache[year] = content.split('\n');
            console.log(`Loaded ESC_${year}.md (${this.guidelinesCache[year].length} lines)`);
            return this.guidelinesCache[year];
        } catch (error) {
            console.error(`Error loading ESC_${year}.md:`, error);
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
        // Phase 1: LOCATE - Find relevant sections in TOC
        let tocMatches = this.searchTOC(question);
        console.log('TOC matches:', tocMatches);

        // Phase 1b: ALWAYS do direct content search for specific terms (drugs, values)
        // TOC only has section headers, not detailed content locations
        const directMatches = await this.searchContentDirectly(question);
        if (directMatches.length > 0) {
            // Prioritize direct matches (they find actual content, not just section headers)
            tocMatches = [...directMatches, ...tocMatches].slice(0, 5);
            console.log('Direct content matches:', directMatches.length);
        }

        // Phase 2: READ - Extract actual content from MD files
        const extractedContent = await this.extractContent(tocMatches);
        console.log('Extracted content length:', extractedContent.length);

        // Phase 3: CITE - Query LLM with real content
        const systemPrompt = this.buildSystemPrompt();
        const userPrompt = this.buildUserPrompt(question, extractedContent, tocMatches);

        return await this.callOpenRouter(systemPrompt, userPrompt);
    }

    async searchContentDirectly(question) {
        const keywords = this.extractKeywords(question);
        const questionWords = question.toLowerCase().split(/\s+/).filter(w => w.length > 4);
        const matches = [];
        const years = ['2024', '2023', '2025', '2022', '2021', '2020'];

        for (const year of years) {
            const lines = await this.loadGuidelineFile(year);
            if (!lines) continue;

            let bestMatch = null;
            let bestScore = 0;

            // Search for keyword matches in content
            for (let i = 0; i < lines.length; i += 30) {
                const chunk = lines.slice(i, i + 80).join(' ').toLowerCase();

                // Count keyword matches
                let matchScore = keywords.filter(kw => chunk.includes(kw.toLowerCase())).length;

                // Bonus for exact question words (like drug names)
                questionWords.forEach(word => {
                    if (chunk.includes(word)) matchScore += 2;
                });

                if (matchScore > bestScore) {
                    bestScore = matchScore;

                    // Find the nearest page marker
                    let page = null;
                    for (let j = i; j >= Math.max(0, i - 50); j--) {
                        const pageMatch = lines[j].match(/^### Page (\d+)/);
                        if (pageMatch) {
                            page = parseInt(pageMatch[1]);
                            break;
                        }
                    }

                    bestMatch = {
                        tocLine: `Direct match in ESC_${year}.md`,
                        year: year,
                        startLine: i + 1,
                        page: page,
                        score: matchScore
                    };
                }
            }

            // Only add if we found a reasonably good match
            if (bestMatch && bestScore >= 3) {
                matches.push(bestMatch);
            }
        }

        matches.sort((a, b) => b.score - a.score);
        return matches.slice(0, 3);
    }

    searchTOC(question) {
        if (!this.tocData) return [];

        const keywords = this.extractKeywords(question);
        const lines = this.tocData.split('\n');
        const matches = [];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const lineLower = line.toLowerCase();

            // Check if line matches any keyword
            const matchScore = keywords.filter(kw => lineLower.includes(kw)).length;
            if (matchScore === 0) continue;

            // Extract year from context (look backwards for year/section header)
            let year = null;
            for (let j = i; j >= Math.max(0, i - 100); j--) {
                // Match: ### <a name="2023-cardiomyopathies"></a>
                const anchorMatch = lines[j].match(/###.*<a name="(202[0-5])-/);
                if (anchorMatch) {
                    year = anchorMatch[1];
                    break;
                }
                // Match: ### 2023 or ## 2023
                const yearMatch = lines[j].match(/^##+ (202[0-5])/);
                if (yearMatch) {
                    year = yearMatch[1];
                    break;
                }
                // Match: **File:** `2023_Cardiomyopathies.pdf`
                const fileMatch = lines[j].match(/\*\*File:\*\*.*`(202[0-5])_/);
                if (fileMatch) {
                    year = fileMatch[1];
                    break;
                }
            }

            // Extract line number from TOC entry: *(p. X, LNNN)*
            const lineNumMatch = line.match(/\*\(p\.\s*\d+,?\s*L(\d+)\)\*/);
            const pageMatch = line.match(/\*\(p\.\s*(\d+)/);

            if (lineNumMatch && year) {
                matches.push({
                    tocLine: line.trim(),
                    year: year,
                    startLine: parseInt(lineNumMatch[1]),
                    page: pageMatch ? parseInt(pageMatch[1]) : null,
                    score: matchScore
                });
            }
        }

        // Sort by score and take top matches
        matches.sort((a, b) => b.score - a.score);
        return matches.slice(0, 5); // Top 5 most relevant sections
    }

    async extractContent(tocMatches) {
        if (tocMatches.length === 0) return '';

        const contentParts = [];
        const yearsToLoad = [...new Set(tocMatches.map(m => m.year))];

        // Load all needed year files
        for (const year of yearsToLoad) {
            await this.loadGuidelineFile(year);
        }

        for (const match of tocMatches) {
            const lines = this.guidelinesCache[match.year];
            if (!lines) continue;

            // Find the next section's start line to know where to stop
            const nextMatch = tocMatches.find(m =>
                m.year === match.year && m.startLine > match.startLine
            );
            const endLine = nextMatch ? nextMatch.startLine : match.startLine + 200;

            // Extract content (limit to ~150 lines per section)
            const startIdx = Math.max(0, match.startLine - 1);
            const endIdx = Math.min(lines.length, startIdx + 150, endLine);
            const sectionContent = lines.slice(startIdx, endIdx).join('\n');

            contentParts.push(`\n--- FROM: ESC_${match.year}.md (Line ${match.startLine}, Page ${match.page}) ---\n${sectionContent}`);
        }

        // Limit total content to avoid token limits
        const combined = contentParts.join('\n\n');
        if (combined.length > 15000) {
            return combined.substring(0, 15000) + '\n\n[...contenuto troncato per limiti di lunghezza...]';
        }
        return combined;
    }

    extractKeywords(question) {
        const termMap = {
            // Anatomia e condizioni
            'aorta': ['aorta', 'aortic', 'ascending', 'root'],
            'fibrillazione atriale': ['atrial fibrillation', 'af', 'fibrillation', 'afib'],
            'stenosi': ['stenosis', 'stenotic', 'severe'],
            'insufficienza': ['insufficiency', 'regurgitation'],
            'scompenso': ['heart failure', 'hf', 'failure'],
            'ipertensione': ['hypertension', 'blood pressure', 'arterial'],
            'diabete': ['diabetes', 'glycemic', 'diabetic'],
            'anticoagulante': ['anticoagul', 'warfarin', 'doac', 'oac'],
            'tac': ['ct', 'computed tomography', 'imaging'],
            'eco': ['echo', 'echocardiograph'],
            'chirurgia': ['surgery', 'surgical', 'intervention'],
            'valvola': ['valve', 'valvular', 'mitral', 'aortic', 'tricuspid'],
            'coronar': ['coronary', 'cad', 'acs', 'stemi', 'nstemi'],
            'aritmia': ['arrhythmia', 'rhythm', 'tachycardia', 'bradycardia'],
            'pacemaker': ['pacing', 'crt', 'icd', 'device'],
            'endocardite': ['endocarditis', 'infective'],
            'cardiomiopatia': ['cardiomyopathy', 'hcm', 'dcm'],
            'ipertensione polmonare': ['pulmonary hypertension', 'ph'],
            // Farmaci -> condizioni correlate
            'mavacamten': ['mavacamten', 'cardiomyopathy', 'hcm', 'hypertrophic', 'obstructive'],
            'aficamten': ['aficamten', 'cardiomyopathy', 'hcm', 'hypertrophic'],
            'empagliflozin': ['empagliflozin', 'sglt2', 'heart failure', 'diabetes'],
            'dapagliflozin': ['dapagliflozin', 'sglt2', 'heart failure', 'diabetes'],
            'sacubitril': ['sacubitril', 'arni', 'heart failure', 'hfref'],
            'valsartan': ['valsartan', 'arni', 'heart failure'],
            'entresto': ['entresto', 'sacubitril', 'arni', 'heart failure'],
            'rivaroxaban': ['rivaroxaban', 'anticoagul', 'doac', 'fibrillation'],
            'apixaban': ['apixaban', 'anticoagul', 'doac', 'fibrillation'],
            'edoxaban': ['edoxaban', 'anticoagul', 'doac', 'fibrillation'],
            'dabigatran': ['dabigatran', 'anticoagul', 'doac', 'fibrillation'],
            'betabloccante': ['beta-blocker', 'metoprolol', 'bisoprolol', 'carvedilol'],
            'statina': ['statin', 'atorvastatin', 'rosuvastatin', 'cholesterol'],
            'ace inibitore': ['ace inhibitor', 'ramipril', 'enalapril', 'lisinopril'],
            'sartano': ['arb', 'losartan', 'valsartan', 'candesartan'],
        };

        const keywords = new Set();
        const questionLower = question.toLowerCase();

        // Add words > 3 chars
        questionLower.split(/\s+/).forEach(word => {
            if (word.length > 3) keywords.add(word.replace(/[?.,!]/g, ''));
        });

        // Add mapped terms
        Object.entries(termMap).forEach(([italian, english]) => {
            if (questionLower.includes(italian)) {
                english.forEach(term => keywords.add(term));
            }
        });

        // Numbers (for thresholds like 45mm, 50%)
        const numbers = question.match(/\d+/g);
        if (numbers) numbers.forEach(n => keywords.add(n));

        return Array.from(keywords);
    }

    buildSystemPrompt() {
        return `Sei un assistente esperto per le Linee Guida ESC (European Society of Cardiology).

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
**Pagina**: [numero]

**IMPORTANTE**: Rispondi SEMPRE in italiano. Se il contenuto fornito non contiene informazioni sufficienti, indicalo chiaramente.`;
    }

    buildUserPrompt(question, extractedContent, tocMatches) {
        const tocSummary = tocMatches.map(m => `- ${m.tocLine} (${m.year}, p.${m.page})`).join('\n');

        return `**DOMANDA CLINICA:**
${question}

**SEZIONI TROVATE NEL TOC:**
${tocSummary || 'Nessuna sezione specifica trovata'}

**CONTENUTO ESTRATTO DALLE LINEE GUIDA ESC:**
${extractedContent || 'Nessun contenuto disponibile. Rispondi indicando che le informazioni richieste non sono state trovate nelle linee guida caricate.'}

---
Rispondi alla domanda usando ESCLUSIVAMENTE il contenuto sopra. Cita esattamente dal testo.`;
    }

    async callOpenRouter(systemPrompt, userPrompt) {
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
                max_tokens: 2500
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || 'API request failed');
        }

        const data = await response.json();
        return data.choices[0].message.content;
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
