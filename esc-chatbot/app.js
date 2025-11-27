---
---
// ============================================
// ESC Guidelines Chatbot - Main Application
// ============================================

class ESCChatbot {
    constructor() {
        // API key is stored securely in Vercel environment variables
        this.model = 'anthropic/claude-3.5-sonnet';
        this.tocData = null;

        this.init();
    }

    async init() {
        // Load TOC data
        await this.loadTOC();

        // Setup event listeners
        this.setupEventListeners();

        // Enable chatbot (no API key check needed)
        this.enableChatbot();
    }

    async loadTOC() {
        try {
            const response = await fetch('../ESC_GUIDELINES_TOC.md');
            const text = await response.text();
            this.tocData = text;
            console.log('TOC loaded successfully');
        } catch (error) {
            console.error('Error loading TOC:', error);
        }
    }

    setupEventListeners() {
        // Form submission
        const form = document.getElementById('chat-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Textarea auto-resize and Enter key handling
        const textarea = document.getElementById('chat-input');
        textarea.addEventListener('input', () => this.autoResize(textarea));
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });

        // Example questions
        const exampleBtns = document.querySelectorAll('.example-btn');
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.dataset.question;
                textarea.value = question;
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
        // Hide API notice if exists
        const notice = document.getElementById('api-key-notice');
        if (notice) notice.style.display = 'none';

        // Enable input and button
        const input = document.getElementById('chat-input');
        const sendBtn = document.getElementById('send-button');
        input.disabled = false;
        sendBtn.disabled = false;
        input.placeholder = 'Fai una domanda sulle linee guida ESC...';

        // Update status badge
        const statusBadge = document.getElementById('status-badge');
        statusBadge.innerHTML = '<span class="badge-dot"></span> Pronto';
        statusBadge.className = 'badge badge-success';
    }

    async sendMessage() {
        const textarea = document.getElementById('chat-input');
        const message = textarea.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Clear input
        textarea.value = '';
        this.autoResize(textarea);

        // Disable input while processing
        textarea.disabled = true;
        document.getElementById('send-button').disabled = true;

        // Add loading message
        const loadingId = this.addLoadingMessage();

        try {
            // Process query with ESC workflow
            const response = await this.queryESCGuidelines(message);

            // Remove loading message
            this.removeMessage(loadingId);

            // Add assistant response
            this.addMessage(response, 'assistant');
        } catch (error) {
            console.error('Error:', error);
            this.removeMessage(loadingId);
            this.addMessage(
                'Mi dispiace, si è verificato un errore. Riprova più tardi.\n\nErrore: ' + error.message,
                'assistant'
            );
        } finally {
            // Re-enable input
            textarea.disabled = false;
            document.getElementById('send-button').disabled = false;
            textarea.focus();
        }
    }

    async queryESCGuidelines(question) {
        // Phase 1: Locate - Search TOC for relevant sections
        const relevantSections = this.searchTOC(question);

        // Phase 2 & 3: Read & Cite - Query LLM with context
        const systemPrompt = this.buildSystemPrompt();
        const userPrompt = this.buildUserPrompt(question, relevantSections);

        // Call OpenRouter API
        const response = await this.callOpenRouter(systemPrompt, userPrompt);

        return response;
    }

    searchTOC(question) {
        if (!this.tocData) return '';

        // Extract keywords from question
        const keywords = this.extractKeywords(question);

        // Search TOC for matching sections
        const lines = this.tocData.split('\n');
        const relevantLines = [];
        const context = 5; // Lines of context to include

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            const hasMatch = keywords.some(keyword => line.includes(keyword));

            if (hasMatch) {
                // Include context lines before and after
                const start = Math.max(0, i - context);
                const end = Math.min(lines.length, i + context + 1);

                for (let j = start; j < end; j++) {
                    if (!relevantLines.includes(j)) {
                        relevantLines.push(j);
                    }
                }
            }
        }

        // Sort and extract matched sections
        relevantLines.sort((a, b) => a - b);
        const sections = relevantLines.map(i => lines[i]).join('\n');

        return sections;
    }

    extractKeywords(question) {
        // Medical terms mapping (Italian to English + abbreviations)
        const termMap = {
            'aorta': ['aorta', 'aortic'],
            'fibrillazione atriale': ['atrial fibrillation', 'af', 'fibrillation'],
            'stenosi': ['stenosis', 'stenotic'],
            'insufficienza': ['insufficiency', 'regurgitation'],
            'scompenso': ['heart failure', 'hf'],
            'ipertensione': ['hypertension', 'blood pressure'],
            'diabete': ['diabetes', 'glycemic'],
            'anticoagulante': ['anticoagul', 'warfarin', 'doac'],
            'imaging': ['imaging', 'ct', 'tac', 'mri', 'rm', 'echo', 'eco'],
            'chirurgia': ['surgery', 'surgical', 'operation'],
            'sorveglianza': ['surveillance', 'follow-up', 'monitoring'],
        };

        const words = question.toLowerCase().split(/\s+/);
        const keywords = new Set();

        // Add original words
        words.forEach(word => {
            if (word.length > 3) {
                keywords.add(word);
            }
        });

        // Add mapped terms
        Object.entries(termMap).forEach(([italian, english]) => {
            if (question.toLowerCase().includes(italian)) {
                english.forEach(term => keywords.add(term));
            }
        });

        // Common medical abbreviations
        const abbreviations = {
            'tac': 'ct',
            'rm': 'mri',
            'eco': 'echo',
            'fa': 'atrial fibrillation',
        };

        Object.entries(abbreviations).forEach(([short, full]) => {
            if (question.toLowerCase().includes(short)) {
                keywords.add(full);
            }
        });

        return Array.from(keywords);
    }

    buildSystemPrompt() {
        return `You are an expert ESC Guidelines assistant. Your role is to answer clinical cardiovascular questions by citing the official ESC (European Society of Cardiology) Guidelines.

**CRITICAL INSTRUCTIONS:**

1. **Always cite sources**: Include PDF filename, section number, and page number
2. **Include evidence level**: State the Recommendation Class (I/IIa/IIb/III) and Level of Evidence (A/B/C)
3. **Quote exactly**: Use direct quotes from the guidelines when possible
4. **Provide clinical context**: Include thresholds, surveillance intervals, and special population considerations
5. **Structured response**: Follow this format:

## ESC Recommendation

**[Class X, Level Y]**: [Brief summary]

"[Exact quote from guidelines if available]"

## Clinical Context
- **Threshold/Criteria**: [Specific values]
- **Imaging/Treatment**: [Recommended approach]
- **Surveillance**: [Follow-up schedule]
- **Special Considerations**: [Risk factors, comorbidities]

## Source Citation
**PDF**: [filename].pdf
**Section**: [section number and title]
**Page**: [page number]

**AVAILABLE GUIDELINES (2020-2025):**
- 2024: Atrial Fibrillation, Chronic Coronary Syndromes, Hypertension, Peripheral Arterial & Aortic
- 2023: Acute Coronary Syndromes, Cardiomyopathies, CVD & Diabetes, Endocarditis
- 2022: Cardio-oncology, Valvular Heart Disease, Pulmonary Hypertension, Ventricular Arrhythmias
- 2021: Heart Failure, Pacing & CRT, Prevention
- 2020: Adult Congenital Heart Disease, Sports Cardiology

**IMPORTANT**:
- If you don't have access to the exact PDF content, indicate that the answer is based on general ESC guideline knowledge and recommend verifying in the official PDF
- Always maintain a professional, evidence-based tone
- Respond in Italian if the question is in Italian
`;
    }

    buildUserPrompt(question, tocSections) {
        return `**Clinical Question:**
${question}

**Relevant TOC Sections Found:**
${tocSections || 'No specific sections found in TOC search. Please answer based on your knowledge of ESC Guidelines.'}

**Instructions:**
1. Based on the TOC sections above, identify which ESC guideline PDF would contain the answer
2. Provide a detailed answer following the structured format in your system prompt
3. If the exact information is not in the TOC, use your knowledge of ESC guidelines but clearly indicate this
4. Respond in Italian

Please provide your answer now.`;
    }

    async callOpenRouter(systemPrompt, userPrompt) {
        // Call our secure backend API (API key stored in Vercel env vars)
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: this.model,
                messages: [
                    {
                        role: 'system',
                        content: systemPrompt
                    },
                    {
                        role: 'user',
                        content: userPrompt
                    }
                ]
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

        if (role === 'assistant') {
            avatar.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
            `;
        } else {
            avatar.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
            `;
        }

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        const messageHeader = document.createElement('div');
        messageHeader.className = 'message-header';

        const authorSpan = document.createElement('span');
        authorSpan.className = 'message-author';
        authorSpan.textContent = role === 'assistant' ? 'ESC Assistant' : 'Tu';

        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = new Date().toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit'
        });

        messageHeader.appendChild(authorSpan);
        messageHeader.appendChild(timeSpan);

        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(content);

        messageContent.appendChild(messageHeader);
        messageContent.appendChild(messageText);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);

        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
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
                <div class="message-header">
                    <span class="message-author">ESC Assistant</span>
                </div>
                <div class="message-text">
                    <div class="loading-dots">
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                        <div class="loading-dot"></div>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageId;
    }

    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }

    formatMessage(content) {
        // Convert markdown-like syntax to HTML
        let formatted = content;

        // Headers
        formatted = formatted.replace(/^## (.*$)/gim, '<h3>$1</h3>');
        formatted = formatted.replace(/^### (.*$)/gim, '<h4>$1</h4>');

        // Bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Code
        formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');

        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        // Links
        formatted = formatted.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        return formatted;
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new ESCChatbot();
});
