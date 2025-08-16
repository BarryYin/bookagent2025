/**
 * 引导式书籍推荐智能体前端实现
 * 提供与后端推荐系统的交互功能
 */

class RecommendationAgent {
    constructor() {
        this.sessionId = null;
        this.userId = 1; // 模拟用户ID
        this.isActive = false;
        this.conversationHistory = [];
        this.currentStage = 'initial';
    }

    async startSession() {
        try {
            const response = await fetch('/api/recommendation/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_id: this.userId })
            });

            if (!response.ok) {
                throw new Error('Failed to start recommendation session');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.isActive = true;
            
            return {
                message: data.message,
                userProfile: data.user_profile
            };
        } catch (error) {
            console.error('Error starting recommendation session:', error);
            throw error;
        }
    }

    async sendMessage(message) {
        if (!this.isActive) {
            throw new Error('Recommendation session not started');
        }

        try {
            const response = await fetch('/api/recommendation/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId
                })
            });

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const data = await response.json();
            
            // 添加到对话历史
            this.conversationHistory.push({
                type: 'user',
                message: message,
                timestamp: new Date().toISOString()
            });

            this.conversationHistory.push({
                type: 'agent',
                message: data.message,
                recommendations: data.recommendations || [],
                timestamp: new Date().toISOString()
            });

            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    async getRecommendations() {
        try {
            const response = await fetch('/api/recommendation/recommendations');
            if (!response.ok) {
                throw new Error('Failed to get recommendations');
            }

            const data = await response.json();
            return data.recommendations;
        } catch (error) {
            console.error('Error getting recommendations:', error);
            throw error;
        }
    }

    async addMockData() {
        try {
            const response = await fetch('/api/recommendation/mock-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to add mock data');
            }

            return await response.json();
        } catch (error) {
            console.error('Error adding mock data:', error);
            throw error;
        }
    }

    clearSession() {
        this.sessionId = null;
        this.isActive = false;
        this.conversationHistory = [];
        this.currentStage = 'initial';
    }
}

class RecommendationUI {
    constructor() {
        this.agent = new RecommendationAgent();
        this.chatContainer = null;
        this.inputField = null;
        this.isInitialized = false;
    }

    init() {
        if (this.isInitialized) return;
        this.createUI();
        this.bindEvents();
        this.isInitialized = true;
    }

    createUI() {
        // 创建推荐智能体容器
        const container = document.createElement('div');
        container.id = 'recommendation-agent';
        container.className = 'recommendation-agent-container';
        container.innerHTML = `
            <div class="recommendation-header">
                <h3>📚 私人阅读顾问</h3>
                <button class="close-btn" title="关闭">×</button>
            </div>
            <div class="recommendation-chat">
                <div class="chat-messages"></div>
                <div class="chat-input-container">
                    <input type="text" class="chat-input" placeholder="和我聊聊你的阅读需求..." />
                    <button class="send-btn">发送</button>
                </div>
            </div>
        `;

        // 添加到页面
        document.body.appendChild(container);

        this.chatContainer = container.querySelector('.chat-messages');
        this.inputField = container.querySelector('.chat-input');
    }

    bindEvents() {
        const container = document.getElementById('recommendation-agent');
        const closeBtn = container.querySelector('.close-btn');
        const sendBtn = container.querySelector('.send-btn');
        const input = container.querySelector('.chat-input');

        // 关闭按钮
        closeBtn.addEventListener('click', () => {
            this.hide();
        });

        // 发送消息
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // 回车发送
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
    }

    async start() {
        try {
            this.show();
            this.addMessage('agent', '正在初始化您的私人阅读顾问...', 'loading');
            
            // 添加模拟数据
            await this.agent.addMockData();
            
            // 开始会话
            const response = await this.agent.startSession();
            this.clearMessages();
            this.addMessage('agent', response.message);
            
            if (response.userProfile) {
                this.displayUserProfile(response.userProfile);
            }
        } catch (error) {
            console.error('Error starting recommendation:', error);
            this.addMessage('agent', '抱歉，启动推荐服务时出现问题，请稍后重试。');
        }
    }

    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;

        this.addMessage('user', message);
        this.inputField.value = '';

        try {
            const response = await this.agent.sendMessage(message);
            this.addMessage('agent', response.message);

            if (response.recommendations && response.recommendations.length > 0) {
                this.displayRecommendations(response.recommendations);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('agent', '抱歉，发送消息时出现问题，请稍后重试。');
        }
    }

    addMessage(type, text, className = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message ${className}`;
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = text.replace(/\n/g, '<br>');
        
        messageDiv.appendChild(content);
        this.chatContainer.appendChild(messageDiv);
        
        // 滚动到底部
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    clearMessages() {
        this.chatContainer.innerHTML = '';
    }

    displayUserProfile(profile) {
        const profileDiv = document.createElement('div');
        profileDiv.className = 'user-profile';
        profileDiv.innerHTML = `
            <h4>您的阅读档案</h4>
            <p><strong>阅读频率：</strong>${profile.reading_frequency || '未知'}</p>
            <p><strong>偏好类别：</strong>${(profile.preferred_categories || []).join(', ')}</p>
            <p><strong>当前阶段：</strong>${profile.current_life_stage || '未知'}</p>
            <p><strong>情感需求：</strong>${(profile.emotional_needs || []).join(', ')}</p>
        `;
        this.chatContainer.appendChild(profileDiv);
    }

    displayRecommendations(recommendations) {
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.className = 'recommendations';
        
        let html = '<h4>为您推荐</h4>';
        recommendations.forEach(book => {
            html += `
                <div class="book-recommendation">
                    <h5>${book.title}</h5>
                    <p class="author">作者：${book.author}</p>
                    <p class="category">类别：${book.category}</p>
                    <p class="description">${book.description}</p>
                    <p class="reason">推荐理由：${book.reason}</p>
                </div>
            `;
        });
        
        recommendationsDiv.innerHTML = html;
        this.chatContainer.appendChild(recommendationsDiv);
    }

    show() {
        const container = document.getElementById('recommendation-agent');
        if (container) {
            container.style.display = 'block';
        }
    }

    hide() {
        const container = document.getElementById('recommendation-agent');
        if (container) {
            container.style.display = 'none';
        }
    }

    toggle() {
        const container = document.getElementById('recommendation-agent');
        if (container.style.display === 'none' || !container.style.display) {
            this.start();
        } else {
            this.hide();
        }
    }
}

// 全局实例
const recommendationUI = new RecommendationUI();

// 初始化函数
function initRecommendationAgent() {
    // 添加CSS样式
    const style = document.createElement('style');
    style.textContent = `
        .recommendation-agent-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            z-index: 10000;
            display: none;
            flex-direction: column;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .recommendation-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e0e0e0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px 12px 0 0;
        }

        .recommendation-header h3 {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: background-color 0.2s;
        }

        .close-btn:hover {
            background: rgba(255,255,255,0.2);
        }

        .recommendation-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-messages {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .message {
            margin-bottom: 1rem;
            animation: fadeIn 0.3s ease-in;
        }

        .message-content {
            padding: 0.75rem 1rem;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
        }

        .user-message .message-content {
            background: #667eea;
            color: white;
            margin-left: auto;
        }

        .agent-message .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
        }

        .user-profile, .recommendations {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }

        .user-profile h4, .recommendations h4 {
            margin: 0 0 0.5rem 0;
            color: #667eea;
        }

        .book-recommendation {
            border-left: 3px solid #667eea;
            padding-left: 1rem;
            margin: 1rem 0;
        }

        .book-recommendation h5 {
            margin: 0 0 0.25rem 0;
            color: #333;
        }

        .book-recommendation .author {
            font-size: 0.9rem;
            color: #666;
            margin: 0.25rem 0;
        }

        .book-recommendation .category {
            font-size: 0.85rem;
            color: #888;
            margin: 0.25rem 0;
        }

        .book-recommendation .description, .book-recommendation .reason {
            font-size: 0.9rem;
            color: #555;
            margin: 0.25rem 0;
            line-height: 1.4;
        }

        .chat-input-container {
            display: flex;
            padding: 1rem;
            border-top: 1px solid #e0e0e0;
            background: white;
            border-radius: 0 0 12px 12px;
        }

        .chat-input {
            flex: 1;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
            font-size: 0.9rem;
        }

        .chat-input:focus {
            border-color: #667eea;
        }

        .send-btn {
            margin-left: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background-color 0.2s;
        }

        .send-btn:hover {
            background: #5a6fd8;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 响应式设计 */
        @media (max-width: 480px) {
            .recommendation-agent-container {
                width: 95%;
                height: 80%;
                top: 10%;
                left: 2.5%;
                transform: none;
            }
        }
    `;
    document.head.appendChild(style);

    // 绑定推荐按钮事件
    document.addEventListener('DOMContentLoaded', function() {
        const recommendationBtn = document.querySelector('[data-agent="recommendation"]');
        if (recommendationBtn) {
            recommendationBtn.addEventListener('click', function(e) {
                e.preventDefault();
                recommendationUI.toggle();
            });
        }
    });
}

// 初始化
initRecommendationAgent();

// 确保全局可用
window.recommendationUI = window.recommendationUI || recommendationUI;