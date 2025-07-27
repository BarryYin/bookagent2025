document.addEventListener('DOMContentLoaded', () => {
    const config = {
        apiBaseUrl: '', 
        defaultLang: 'zh',
    };

    const translations = {
        heroTitle: { zh: "在此赋予概念以生命，转瞬之间", en: "Bring Concepts to Life Here" },
        startCreatingTitle: { zh: "开始创作", en: "Start Creating" },
        githubrepo: { zh: "Github 开源仓库", en: "Fogsight Github Repo" },
        officialWebsite: { zh: "通向 AGI 之路社区", en: "WaytoAGI Open Source Community" },
        groupChat: { zh: "联系我们/加入交流群", en: "Contact Us" },
        placeholders: {
            zh: ["微积分的几何原理", "冒泡排序","热寂", "黑洞是如何形成的"],
            en: ["What is Heat Death?", "How are black holes formed?", "What is Bubble Sort?"]
        },
        newChat: { zh: "新对话", en: "New Chat" },
        newChatTitle: { zh: "新对话", en: "New Chat" },
        chatPlaceholder: {
            zh: "AI 生成结果具有随机性，您可在此输入修改意见",
            en: "Results are random. Enter your modifications here for adjustments."
        },
        sendTitle: { zh: "发送", en: "Send" },
        agentThinking: { zh: "Fogsight Agent 正在进行思考与规划，请稍后。这可能需要数十秒至数分钟...", en: "Fogsight Agent is thinking and planning, please wait..." },
        generatingCode: { zh: "生成代码中...", en: "Generating code..." },
        codeComplete: { zh: "代码已完成", en: "Code generated" },
        openInNewWindow: { zh: "在新窗口中打开", en: "Open in new window" },
        saveAsHTML: { zh: "保存为 HTML", en: "Save as HTML" },
        exportAsVideo: { zh: "导出为视频", en: "Export as Video" },
        featureComingSoon: { zh: "该功能正在开发中，将在不久的将来推出。\n 请关注我们的官方 GitHub 仓库以获取最新动态！", en: "This feature is under development and will be available soon.\n Follow our official GitHub repository for the latest updates!" },
        visitGitHub: { zh: "访问 GitHub", en: "Visit GitHub" },
        errorMessage: { zh: "抱歉，服务出现了一点问题。请稍后重试。", en: "Sorry, something went wrong. Please try again later." },
        errorFetchFailed: {zh: "LLM服务不可用，请稍后再试", en: "LLM service is unavailable. Please try again later."},
        errorTooManyRequests: {zh: "今天已经使用太多，请明天再试", en: "Too many requests today. Please try again tomorrow."},
        recentPPTs: { zh: "最近生成的PPT", en: "Recent PPTs" }
    };

    let currentLang = config.defaultLang;
    const body = document.body;
    const initialForm = document.getElementById('initial-form');
    const initialInput = document.getElementById('initial-input');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatLog = document.getElementById('chat-log');
    const newChatButton = document.getElementById('new-chat-button');
    const languageSwitcher = document.getElementById('language-switcher');
    const placeholderContainer = document.getElementById('animated-placeholder');
    const featureModal = document.getElementById('feature-modal');
    const modalGitHubButton = document.getElementById('modal-github-button');
    const modalCloseButton = document.getElementById('modal-close-button');

    const templates = {
        user: document.getElementById('user-message-template'),
        status: document.getElementById('agent-status-template'),
        code: document.getElementById('agent-code-template'),
        player: document.getElementById('animation-player-template'),
        error: document.getElementById('agent-error-template'),
    };

    let conversationHistory = [];
    let accumulatedCode = '';
    let placeholderInterval;
    let pptGallery = null;

    function handleFormSubmit(e) {
        console.log('表单提交开始', e);
        e.preventDefault();
        console.log('preventDefault已调用');
        
        const isInitial = e.currentTarget.id === 'initial-form';
        console.log('是否为初始表单:', isInitial);
        
        const submitButton = isInitial
            ? initialForm?.querySelector('button')
            : chatForm?.querySelector('button');
        
        const input = isInitial ? initialInput : chatInput;
        const topic = input.value.trim();
        console.log('输入的主题:', topic);
        
        if (!topic) {
            console.log('主题为空，返回');
            return;
        }

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.classList.add('disabled');
            console.log('按钮已禁用');
        }

        if (isInitial) {
            console.log('切换到聊天视图');
            switchToChatView();
        }

        conversationHistory.push({ role: 'user', content: topic });
        console.log('开始生成内容');
        
        try {
            startGeneration(topic, submitButton);  // 传递submitButton参数
            console.log('startGeneration已调用');
        } catch (error) {
            console.error('startGeneration调用失败:', error);
        }
        
        input.value = '';
        if (isInitial) placeholderContainer?.classList?.remove('hidden');
        console.log('表单提交处理完成');
    }

    async function startGeneration(topic, submitButton) {
        console.log('startGeneration开始，主题:', topic);
        
        // 在函数顶部声明变量，确保作用域正确
        let agentThinkingMessage;
        let inCodeBlock = false;
        let codeBlockElement = null;
        
        // 重置全局的accumulatedCode
        accumulatedCode = '';
        
        try {
            console.log('尝试添加用户消息');
            appendUserMessage(topic);
            console.log('用户消息已添加');
            
            console.log('尝试添加思考状态');
            agentThinkingMessage = appendAgentStatus(translations.agentThinking[currentLang]);
            console.log('思考状态已添加');

            console.log('开始API调用');
        } catch (error) {
            console.error('startGeneration初始化失败:', error);
            throw error;
        }

        try {
            const response = await fetch(`${config.apiBaseUrl}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic, history: conversationHistory })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;

                    const jsonStr = line.substring(6);
                    if (jsonStr.includes('[DONE]')) {
                        console.log('收到DONE信号');
                        console.log('accumulatedCode长度:', accumulatedCode.length);
                        console.log('codeBlockElement存在:', !!codeBlockElement);
                        
                        conversationHistory.push({ role: 'assistant', content: accumulatedCode });
                        if (codeBlockElement) {
                            markCodeAsComplete(codeBlockElement);
                            if (accumulatedCode) {
                                console.log('开始显示动画播放器');
                                appendAnimationPlayer(accumulatedCode, topic);
                            } else {
                                console.log('accumulatedCode为空，不显示播放器');
                            }
                        } else {
                            console.log('codeBlockElement不存在');
                        }
                        return;
                    }

                    const data = JSON.parse(jsonStr);
                    console.log('解析的数据:', data);
                    
                    if (data.error) throw new Error(data.error);

                    // 处理日志消息
                    if (data.log) {
                        console.log('收到日志消息:', data.log);
                        console.log('agentThinkingMessage存在:', !!agentThinkingMessage);
                        
                        if (agentThinkingMessage) {
                            console.log('更新现有思考消息');
                            console.log('思考消息元素:', agentThinkingMessage);
                            updateThinkingMessage(agentThinkingMessage, data.log);
                        } else {
                            console.log('创建新的思考消息');
                            agentThinkingMessage = appendAgentStatus(data.log);
                            console.log('新创建的思考消息元素:', agentThinkingMessage);
                        }
                        continue;
                    }

                    // 处理状态消息
                    if (data.status) {
                        if (agentThinkingMessage) {
                            updateThinkingMessage(agentThinkingMessage, data.status);
                        }
                        continue;
                    }

                    const token = data.token || '';
                    console.log('收到token:', token.substring(0, 100) + (token.length > 100 ? '...' : ''));

                    if (!inCodeBlock && token.includes('```')) {
                        console.log('开始代码块');
                        inCodeBlock = true;
                        if (agentThinkingMessage) {
                            // 将思考消息转换为日志显示
                            convertThinkingToLog(agentThinkingMessage);
                            agentThinkingMessage = null;
                        }
                        codeBlockElement = appendCodeBlock();
                        const contentAfterMarker = token.substring(token.indexOf('```') + 3).replace(/^html\n/, '');
                        updateCodeBlock(codeBlockElement, contentAfterMarker);
                    } else if (inCodeBlock) {
                        if (token.includes('```')) {
                            console.log('结束代码块');
                            inCodeBlock = false;
                            const contentBeforeMarker = token.substring(0, token.indexOf('```'));
                            updateCodeBlock(codeBlockElement, contentBeforeMarker);
                        } else {
                            updateCodeBlock(codeBlockElement, token);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Streaming failed:", error);
            if (agentThinkingMessage) agentThinkingMessage.remove();

            if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                showWarning(translations.errorFetchFailed[currentLang]);
            } else if (error.message.includes('status: 429')) {
                showWarning(translations.errorTooManyRequests[currentLang]);
            } else {
                showWarning(translations.errorFetchFailed[currentLang]); // 默认 fallback
            }

            appendErrorMessage(translations.errorMessage[currentLang]);  // 保留 chat-log 中的提示
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.classList.remove('disabled');
            }
        }
    }

    function switchToChatView() {
        body.classList.remove('show-initial-view');
        body.classList.add('show-chat-view');
        languageSwitcher.style.display = 'none';
        document.getElementById('logo-chat').style.display = 'block';
    }

    function appendFromTemplate(template, text) {
        const node = template.content.cloneNode(true);
        const element = node.firstElementChild;
        if (text) element.innerHTML = element.innerHTML.replace('${text}', text);
        element.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            const translation = translations[key]?.[currentLang];
            if (translation) el.textContent = translation;
        });
        chatLog.appendChild(element);
        scrollToBottom();
        return element;
    }

    const appendUserMessage = (text) => appendFromTemplate(templates.user, text);
    const appendAgentStatus = (text) => appendFromTemplate(templates.status, text);
    const appendErrorMessage = (text) => appendFromTemplate(templates.error, text);
    const appendCodeBlock = () => appendFromTemplate(templates.code);

    // 日志处理函数
    function updateThinkingMessage(thinkingElement, logText) {
        console.log('updateThinkingMessage被调用');
        console.log('thinkingElement:', thinkingElement);
        console.log('logText:', logText);
        
        const logContainer = thinkingElement.querySelector('.log-container');
        console.log('现有logContainer:', logContainer);
        
        if (!logContainer) {
            // 创建日志容器
            const container = document.createElement('div');
            container.className = 'log-container';
            container.style.cssText = `
                font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
                font-size: 0.9em;
                line-height: 1.4;
                background: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
                padding: 12px;
                margin-top: 8px;
                max-height: 300px;
                overflow-y: auto;
                white-space: pre-wrap;
            `;
            thinkingElement.appendChild(container);
        }
        
        const container = thinkingElement.querySelector('.log-container');
        const logLine = document.createElement('div');
        logLine.textContent = logText;
        logLine.style.cssText = `
            margin-bottom: 2px;
            opacity: 0;
            animation: fadeInLog 0.3s ease forwards;
        `;
        container.appendChild(logLine);
        
        // 自动滚动到底部
        container.scrollTop = container.scrollHeight;
        scrollToBottom();
    }

    function convertThinkingToLog(thinkingElement) {
        // 将思考状态转换为完成状态
        const dotsElement = thinkingElement.querySelector('.thinking-dots');
        if (dotsElement) {
            dotsElement.style.display = 'none';
        }
        
        const statusText = thinkingElement.querySelector('p');
        if (statusText) {
            statusText.textContent = '✅ 思考与规划完成，开始生成内容...';
        }
        
        // 添加完成样式
        thinkingElement.classList.add('thinking-complete');
    }

    function updateCodeBlock(codeBlockElement, text) {
        const codeElement = codeBlockElement.querySelector('code');
        if (!text || !codeElement) return;
        const span = document.createElement('span');
        span.textContent = text;
        codeElement.appendChild(span);
        accumulatedCode += text;
        scrollToBottom();
    }

    function markCodeAsComplete(codeBlockElement) {
        codeBlockElement.querySelector('[data-translate-key="generatingCode"]').textContent = translations.codeComplete[currentLang];
        codeBlockElement.querySelector('.code-details').removeAttribute('open');
    }

    function appendAnimationPlayer(htmlContent, topic) {
        const node = templates.player.content.cloneNode(true);
        const playerElement = node.firstElementChild;
        playerElement.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            el.textContent = translations[key]?.[currentLang] || el.textContent;
        });
        const iframe = playerElement.querySelector('.animation-iframe');
        iframe.srcdoc = htmlContent;

        playerElement.querySelector('.open-new-window').addEventListener('click', () => {
            const blob = new Blob([htmlContent], { type: 'text/html' });
            window.open(URL.createObjectURL(blob), '_blank');
        });
        playerElement.querySelector('.save-html').addEventListener('click', () => {
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = Object.assign(document.createElement('a'), { href: url, download: `${topic.replace(/\s/g, '_') || 'animation'}.html` });
            document.body.appendChild(a);
            a.click();
            URL.revokeObjectURL(url);
            a.remove();
        });
        playerElement.querySelector('.export-video')?.addEventListener('click', () => {
            featureModal.querySelector('p').textContent = translations.featureComingSoon[currentLang];
            modalGitHubButton.textContent = translations.visitGitHub[currentLang];
            featureModal.classList.add('visible');
        });
        chatLog.appendChild(playerElement);
        scrollToBottom();
    }

    const scrollToBottom = () => chatLog.scrollTo({ top: chatLog.scrollHeight, behavior: 'smooth' });

    function setNextPlaceholder() {
        const placeholderTexts = translations.placeholders[currentLang];
        const newSpan = document.createElement('span');
        newSpan.textContent = placeholderTexts[placeholderIndex];
        placeholderContainer.innerHTML = '';
        placeholderContainer.appendChild(newSpan);
        placeholderIndex = (placeholderIndex + 1) % placeholderTexts.length;
    }

    function startPlaceholderAnimation() {
        if (placeholderInterval) clearInterval(placeholderInterval);
        const placeholderTexts = translations.placeholders[currentLang];
        if (placeholderTexts && placeholderTexts.length > 0) {
            placeholderIndex = 0;
            setNextPlaceholder();
            placeholderInterval = setInterval(setNextPlaceholder, 4000);
        }
    }

    function setLanguage(lang) {
        if (!['zh', 'en'].includes(lang)) return;
        currentLang = lang;
        document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
        document.querySelectorAll('[data-translate-key]').forEach(el => {
            const key = el.dataset.translateKey;
            const translation = translations[key]?.[lang];
            if (!translation) return;
            if (el.hasAttribute('placeholder')) el.placeholder = translation;
            else if (el.hasAttribute('title')) el.title = translation;
            else el.textContent = translation;
        });
        languageSwitcher.querySelectorAll('button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === lang);
        });
        startPlaceholderAnimation();
        localStorage.setItem('preferredLanguage', lang);
    }

    let placeholderIndex = 0;

    function init() {
        initialInput.addEventListener('input', () => {
            placeholderContainer.classList.toggle('hidden', initialInput.value.length > 0);
        });
        initialInput.addEventListener('focus', () => clearInterval(placeholderInterval));
        initialInput.addEventListener('blur', () => {
            if (initialInput.value.length === 0) startPlaceholderAnimation();
        });

        initialForm.addEventListener('submit', handleFormSubmit);
        chatForm.addEventListener('submit', handleFormSubmit);
        newChatButton.addEventListener('click', () => location.reload());
        languageSwitcher.addEventListener('click', (e) => {
            const target = e.target.closest('button');
            if (target) setLanguage(target.dataset.lang);
        });

        function hideModal() {
            featureModal.classList.remove('visible');
        }

        modalCloseButton.addEventListener('click', hideModal);
        featureModal.addEventListener('click', (e) => {
            if (e.target === featureModal) hideModal();
        });

        modalGitHubButton.addEventListener('click', () => {
            window.open('https://github.com/fogsightai/fogsightai', '_blank');
            hideModal();
        });

        const savedLang = localStorage.getItem('preferredLanguage');
        setLanguage(['zh', 'en'].includes(savedLang) ? savedLang : config.defaultLang);
    }

    init();
});

function showWarning(message) {
    const box = document.getElementById('warning-box');
    const overlay = document.getElementById('overlay');
    const text = document.getElementById('warning-message');
    text.textContent = message;
    box.style.display = 'flex';
    overlay.style.display = 'block';

    setTimeout(() => {
        hideWarning();
    }, 10000);
}

function hideWarning() {
    document.getElementById('warning-box').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}
    // PPT画廊相关功能
    async function initPPTGallery() {
        pptGallery = document.getElementById('ppt-grid');
        if (pptGallery) {
            await loadPPTGallery();
        }
    }

    async function loadPPTGallery() {
        console.log('开始加载PPT画廊...');
        
        try {
            // 首页只显示最新的3条PPT
            console.log('发送API请求...');
            const response = await fetch('/api/generated-ppts?limit=3');
            console.log('API响应状态:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('API返回数据:', data);
            
            if (data.ppts && data.ppts.length > 0) {
                console.log(`找到 ${data.ppts.length} 个PPT`);
                renderPPTCards(data.ppts);
            } else {
                console.log('没有找到PPT');
                renderEmptyGallery();
            }
        } catch (error) {
            console.error('加载PPT画廊失败:', error);
            renderErrorGallery();
        }
    }

    function renderPPTCards(ppts) {
        pptGallery.innerHTML = '';
        
        ppts.forEach(ppt => {
            const card = createPPTCard(ppt);
            pptGallery.appendChild(card);
        });
        
        // 如果显示的是限制数量的PPT，添加"查看更多"链接
        if (ppts.length === 3) {
            const viewMoreCard = document.createElement('div');
            viewMoreCard.className = 'view-more-card';
            viewMoreCard.innerHTML = `
                <div class="view-more-content">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="1"></circle>
                        <circle cx="12" cy="5" r="1"></circle>
                        <circle cx="12" cy="19" r="1"></circle>
                    </svg>
                    <h3>查看更多PPT</h3>
                    <p>点击查看所有已生成的PPT</p>
                </div>
            `;
            viewMoreCard.addEventListener('click', showAllPPTs);
            pptGallery.appendChild(viewMoreCard);
        }
    }

    function createPPTCard(ppt) {
        const card = document.createElement('div');
        card.className = 'ppt-card';
        
        card.innerHTML = `
            <div class="ppt-card-header">
                <h3 class="ppt-card-title">${escapeHtml(ppt.title)}</h3>
                <div class="ppt-card-meta">
                    <span>${ppt.created_time}</span>
                    <span>${ppt.session_id.substring(0, 8)}...</span>
                </div>
            </div>
            <div class="ppt-card-preview" id="preview-${ppt.session_id}">
                <div class="loading-spinner" style="width: 20px; height: 20px; margin: 1rem auto;"></div>
            </div>
            <div class="ppt-card-actions">
                <a href="${ppt.html_url}" target="_blank" class="action-btn primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15,3 21,3 21,9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    查看PPT
                </a>
                <button class="action-btn" onclick="copyPPTLink('${ppt.html_url}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    复制链接
                </button>
            </div>
        `;
        
        // 异步加载预览
        loadPPTPreview(ppt.session_id);
        
        return card;
    }

    async function loadPPTPreview(sessionId) {
        try {
            const response = await fetch(`/api/ppt-preview/${sessionId}`);
            const preview = await response.json();
            
            const previewContainer = document.getElementById(`preview-${sessionId}`);
            if (previewContainer && preview.preview_slides) {
                previewContainer.innerHTML = '';
                
                preview.preview_slides.slice(0, 2).forEach(slide => {
                    const slideDiv = document.createElement('div');
                    slideDiv.className = 'preview-slide';
                    slideDiv.innerHTML = `
                        <div class="preview-slide-title">${escapeHtml(slide.title)}</div>
                        <div class="preview-slide-content">${escapeHtml(slide.content)}</div>
                    `;
                    previewContainer.appendChild(slideDiv);
                });
                
                if (preview.total_slides > 2) {
                    const moreDiv = document.createElement('div');
                    moreDiv.className = 'preview-slide';
                    moreDiv.style.textAlign = 'center';
                    moreDiv.style.color = 'var(--text-secondary)';
                    moreDiv.innerHTML = `... 还有 ${preview.total_slides - 2} 页`;
                    previewContainer.appendChild(moreDiv);
                }
            }
        } catch (error) {
            console.error(`Failed to load preview for ${sessionId}:`, error);
            const previewContainer = document.getElementById(`preview-${sessionId}`);
            if (previewContainer) {
                previewContainer.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 1rem;">预览加载失败</div>';
            }
        }
    }

    function renderEmptyGallery() {
        pptGallery.innerHTML = `
            <div class="empty-gallery">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21,15 16,10 5,21"></polyline>
                </svg>
                <p>还没有生成任何PPT</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">在上方输入框中输入书名开始创建吧！</p>
            </div>
        `;
    }

    function renderErrorGallery() {
        pptGallery.innerHTML = `
            <div class="empty-gallery">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p>加载PPT列表失败</p>
                <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem;">
                    请检查服务器是否正常运行，或打开浏览器控制台查看详细错误信息
                </p>
                <button class="action-btn" onclick="refreshPPTGallery()" style="margin-top: 1rem;">重试</button>
            </div>
        `;
    }

    async function refreshPPTGallery() {
        const refreshBtn = document.getElementById('refresh-gallery');
        if (refreshBtn) {
            refreshBtn.style.transform = 'rotate(180deg)';
            setTimeout(() => {
                refreshBtn.style.transform = '';
            }, 300);
        }
        
        pptGallery.innerHTML = `
            <div class="loading-placeholder">
                <div class="loading-spinner"></div>
                <p>正在刷新PPT列表...</p>
            </div>
        `;
        
        await loadPPTGallery();
    }

    function copyPPTLink(url) {
        const fullUrl = window.location.origin + url;
        navigator.clipboard.writeText(fullUrl).then(() => {
            // 简单的提示
            const btn = event.target.closest('.action-btn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20,6 9,17 4,12"></polyline></svg>已复制';
            setTimeout(() => {
                btn.innerHTML = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy link:', err);
        });
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 健康检查函数
    async function checkServerHealth() {
        try {
            const response = await fetch('/api/generated-ppts?limit=1');
            return response.ok;
        } catch (error) {
            console.error('服务器健康检查失败:', error);
            return false;
        }
    }

    // 在页面加载完成后初始化PPT画廊
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', async () => {
            console.log('页面加载完成，开始初始化...');
            const isHealthy = await checkServerHealth();
            console.log('服务器健康状态:', isHealthy);
            initPPTGallery();
        });
    } else {
        console.log('页面已加载，直接初始化...');
        initPPTGallery();
    }

    async function showAllPPTs() {
        try {
            // 获取所有PPT
            const response = await fetch('/api/generated-ppts');
            const data = await response.json();
            
            if (data.ppts && data.ppts.length > 0) {
                // 清空当前显示，重新渲染所有PPT
                pptGallery.innerHTML = '';
                data.ppts.forEach(ppt => {
                    const card = createPPTCard(ppt);
                    pptGallery.appendChild(card);
                });
                
                // 更新标题
                const galleryHeader = document.querySelector('.gallery-header h2');
                if (galleryHeader) {
                    galleryHeader.textContent = `所有PPT (${data.ppts.length}个)`;
                }
                
                // 添加"收起"按钮
                const collapseCard = document.createElement('div');
                collapseCard.className = 'view-more-card';
                collapseCard.innerHTML = `
                    <div class="view-more-content">
                        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="18,15 12,9 6,15"></polyline>
                        </svg>
                        <h3>收起</h3>
                        <p>只显示最新的3个PPT</p>
                    </div>
                `;
                collapseCard.addEventListener('click', () => {
                    // 恢复标题
                    if (galleryHeader) {
                        galleryHeader.textContent = translations.recentPPTs[currentLang];
                    }
                    // 重新加载最新3个
                    loadPPTGallery();
                });
                pptGallery.appendChild(collapseCard);
            }
        } catch (error) {
            console.error('Failed to load all PPTs:', error);
        }
    }  
  // 直接测试API的函数
    window.testAPIDirectly = async function() {
        console.log('直接测试API...');
        const pptGrid = document.getElementById('ppt-grid');
        
        try {
            const response = await fetch('/api/generated-ppts?limit=3');
            console.log('API响应:', response);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('API数据:', data);
            
            pptGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                    <h3>✅ API测试成功！</h3>
                    <p>找到 ${data.ppts ? data.ppts.length : 0} 个PPT</p>
                    <pre style="text-align: left; background: #f5f5f5; padding: 1rem; border-radius: 4px; overflow: auto;">
${JSON.stringify(data, null, 2)}
                    </pre>
                    <button onclick="loadPPTGallery()" style="margin-top: 1rem; padding: 0.5rem 1rem; cursor: pointer;">重新加载画廊</button>
                </div>
            `;
        } catch (error) {
            console.error('API测试失败:', error);
            pptGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                    <h3>❌ API测试失败</h3>
                    <p style="color: red;">${error.message}</p>
                    <button onclick="testAPIDirectly()" style="margin-top: 1rem; padding: 0.5rem 1rem; cursor: pointer;">重试</button>
                </div>
            `;
        }
    };