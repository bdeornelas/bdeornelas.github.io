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
        // All available guideline files (separate, not merged)
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
            console.log('TOC loaded successfully');
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
            this.guidelinesCache[filename] = content.split('\n');
            console.log(`Loaded ${filename}.md (${this.guidelinesCache[filename].length} lines)`);
            return this.guidelinesCache[filename];
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

        console.log('Direct search keywords:', keywords);
        console.log('Question words:', questionWords);

        // Prioritize files based on question content
        const prioritizedFiles = this.prioritizeFiles(keywords, questionWords);
        console.log('Prioritized files:', prioritizedFiles.slice(0, 5).map(f => f.file));

        for (const { file, priority } of prioritizedFiles) {
            try {
                console.log(`Searching ${file}...`);
                const lines = await this.loadGuidelineFile(file);
                if (!lines || lines.length === 0) {
                    console.log(`Failed to load ${file}`);
                    continue;
                }
                console.log(`Loaded ${file}: ${lines.length} lines`);

                // Quick search for exact question words in the raw content
                const rawContent = lines.join('\n').toLowerCase();
                let startSearchLine = 0;
                let foundTerm = null;

                // Find the first occurrence of any long question word
                for (const word of questionWords) {
                    if (word.length >= 6) {
                        const idx = rawContent.indexOf(word);
                        if (idx !== -1) {
                            startSearchLine = rawContent.substring(0, idx).split('\n').length - 1;
                            foundTerm = word;
                            console.log(`Found "${word}" at line ${startSearchLine} in ${file}`);
                            break;
                        }
                    }
                }

                // If we found a specific term, search around that area
                const searchStart = Math.max(0, startSearchLine - 50);
                const searchEnd = Math.min(lines.length, startSearchLine + 200);

                let bestMatch = null;
                let bestScore = 0;

                for (let i = searchStart; i < searchEnd; i += 20) {
                    const chunk = lines.slice(i, i + 60).join(' ').toLowerCase();

                    let matchScore = keywords.filter(kw => chunk.includes(kw.toLowerCase())).length;
                    questionWords.forEach(word => {
                        if (chunk.includes(word)) matchScore += 3;
                    });
                    // Bonus for files that matched by name priority
                    matchScore += priority;

                    if (matchScore > bestScore) {
                        bestScore = matchScore;
                        let page = null;
                        for (let j = i; j >= Math.max(0, i - 50); j--) {
                            const pageMatch = lines[j].match(/^### Page (\d+)/);
                            if (pageMatch) {
                                page = parseInt(pageMatch[1]);
                                break;
                            }
                        }
                        const year = file.substring(0, 4);
                        bestMatch = {
                            tocLine: `Direct match in ${file}.md`,
                            filename: file,
                            year: year,
                            startLine: i + 1,
                            page: page,
                            score: matchScore
                        };
                    }
                }

                if (bestMatch && bestScore >= 4) {
                    console.log(`Found match in ${file}: line ${bestMatch.startLine}, score ${bestScore}`);
                    matches.push(bestMatch);
                    // If we found an excellent match in a prioritized file, stop
                    if (bestScore >= 10 && foundTerm) {
                        console.log('Found excellent match with search term, stopping');
                        break;
                    }
                } else {
                    console.log(`No good match in ${file}, best score: ${bestScore}`);
                }

                // Limit search to top 8 files max
                if (matches.length >= 3) break;
            } catch (error) {
                console.error(`Error searching ${file}:`, error);
            }
        }

        console.log('Direct search results:', matches.length);
        matches.sort((a, b) => b.score - a.score);
        return matches.slice(0, 3);
    }

    prioritizeFiles(keywords, questionWords) {
        // Map keywords to relevant guideline files
        const fileKeywords = {
            '2023_Cardiomyopathies': ['cardiomyopathy', 'hcm', 'dcm', 'hypertrophic', 'mavacamten', 'aficamten', 'obstructive'],
            '2023_Cardiomyopathies_Supplementary': ['cardiomyopathy', 'hcm', 'dcm', 'hypertrophic'],
            '2024_Atrial_Fibrillation': ['fibrillation', 'af', 'afib', 'anticoagul', 'ablation', 'rhythm'],
            '2020_Atrial_Fibrillation': ['fibrillation', 'af', 'afib', 'anticoagul'],
            '2021_Heart_Failure': ['heart failure', 'hf', 'ejection', 'lvef', 'hfref', 'hfpef', 'sacubitril'],
            '2023_Heart_Failure_Update': ['heart failure', 'hf', 'sglt2', 'empagliflozin', 'dapagliflozin'],
            '2023_Acute_Coronary_Syndromes': ['acs', 'stemi', 'nstemi', 'infarction', 'troponin', 'pci'],
            '2024_Chronic_Coronary_Syndromes': ['ccs', 'angina', 'coronary', 'stent', 'cabg'],
            '2021_Valvular_Heart_Disease': ['valve', 'stenosis', 'regurgitation', 'mitral', 'aortic', 'tricuspid'],
            '2025_Valvular_Heart_Disease': ['valve', 'stenosis', 'regurgitation', 'mitral', 'aortic', 'tavi', 'tavr'],
            '2024_Hypertension': ['hypertension', 'blood pressure', 'arterial', 'antihypertensive'],
            '2023_Endocarditis': ['endocarditis', 'infective', 'vegetation'],
            '2023_CVD_Diabetes': ['diabetes', 'glycemic', 'sglt2', 'glp1'],
            '2022_Pulmonary_Hypertension': ['pulmonary hypertension', 'ph', 'pah'],
            '2022_Ventricular_Arrhythmias_SCD': ['arrhythmia', 'vt', 'vf', 'sudden death', 'icd', 'defibrillator'],
            '2021_Cardiac_Pacing_CRT': ['pacemaker', 'pacing', 'crt', 'bradycardia', 'av block'],
            '2024_Peripheral_Arterial_Aortic': ['aorta', 'aneurysm', 'dissection', 'peripheral', 'claudication'],
            '2025_Myocarditis_Pericarditis': ['myocarditis', 'pericarditis', 'pericardial'],
            '2025_Pregnancy_CVD': ['pregnancy', 'pregnant', 'gestational'],
            '2022_Non_Cardiac_Surgery': ['surgery', 'perioperative', 'non-cardiac'],
            '2022_Cardio_Oncology': ['cardio-oncology', 'chemotherapy', 'cancer', 'anthracycline'],
            '2021_CVD_Prevention': ['prevention', 'risk', 'score', 'lipid', 'statin'],
            '2025_Dyslipidaemias_Update': ['cholesterol', 'ldl', 'lipid', 'statin', 'pcsk9'],
            '2020_Sports_Cardiology': ['sport', 'athlete', 'exercise'],
            '2020_Adult_Congenital_Heart_Disease': ['congenital', 'achd', 'shunt'],
            '2025_Mental_Health_CVD': ['mental', 'depression', 'anxiety', 'psychological'],
            '2020_ACS_NSTE': ['nstemi', 'nste-acs', 'unstable angina']
        };

        const allKeywords = [...keywords, ...questionWords].map(k => k.toLowerCase());

        return this.guidelineFiles.map(file => {
            let priority = 0;
            const fileKws = fileKeywords[file] || [];

            // Check how many keywords match this file's topics
            for (const kw of allKeywords) {
                if (fileKws.some(fkw => kw.includes(fkw) || fkw.includes(kw))) {
                    priority += 5;
                }
                // Also check if keyword appears in filename
                if (file.toLowerCase().includes(kw)) {
                    priority += 3;
                }
            }

            // Prefer newer guidelines
            const year = parseInt(file.substring(0, 4));
            priority += (year - 2020) * 0.5;

            return { file, priority };
        }).sort((a, b) => b.priority - a.priority);
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
            // Priority: **File:** > anchor name > year header
            let year = null;
            let foundAnchor = null;
            for (let j = i; j >= Math.max(0, i - 100); j--) {
                // Highest priority: **File:** `2023_Cardiomyopathies.pdf`
                const fileMatch = lines[j].match(/\*\*File:\*\*.*`(202[0-5])_/);
                if (fileMatch) {
                    year = fileMatch[1];
                    break;
                }
                // Second priority: ### <a name="2023-cardiomyopathies"></a>
                if (!foundAnchor) {
                    const anchorMatch = lines[j].match(/###.*<a name="(202[0-5])-/);
                    if (anchorMatch) {
                        foundAnchor = anchorMatch[1];
                    }
                }
            }
            // Use anchor if no file match found
            if (!year && foundAnchor) {
                year = foundAnchor;
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
        const filesToLoad = [...new Set(tocMatches.map(m => m.filename || `ESC_${m.year}`))];

        // Load all needed files
        for (const file of filesToLoad) {
            await this.loadGuidelineFile(file);
        }

        for (const match of tocMatches) {
            const cacheKey = match.filename || `ESC_${match.year}`;
            const lines = this.guidelinesCache[cacheKey];
            if (!lines) continue;

            // Find the next section's start line to know where to stop
            const nextMatch = tocMatches.find(m =>
                (m.filename || m.year) === (match.filename || match.year) && m.startLine > match.startLine
            );
            const endLine = nextMatch ? nextMatch.startLine : match.startLine + 200;

            // Extract content (limit to ~150 lines per section)
            const startIdx = Math.max(0, match.startLine - 1);
            const endIdx = Math.min(lines.length, startIdx + 150, endLine);
            const sectionContent = lines.slice(startIdx, endIdx).join('\n');

            const filename = match.filename || `ESC_${match.year}`;
            contentParts.push(`\n--- FROM: ${filename}.md (Line ${match.startLine}, Page ${match.page}) ---\n${sectionContent}`);
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
