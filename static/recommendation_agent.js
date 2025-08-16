/**
 * 引导推荐智能体交互脚本
 */

// 数据库查询函数 - 获取图书详情
async function getBookDetails(title, author) {
    try {
        const response = await fetch(`/api/books/search?title=${encodeURIComponent(title)}&author=${encodeURIComponent(author)}`);
        if (response.ok) {
            const data = await response.json();
            return data.books && data.books.length > 0 ? data.books[0] : null;
        }
        return null;
    } catch (error) {
        console.error('获取图书详情失败:', error);
        return null;
    }
}

// 初始化推荐会话
document.addEventListener('DOMContentLoaded', function() {
    checkAuthAndInitialize();
});

async function checkAuthAndInitialize() {
    try {
        // 使用现有系统的认证检查端点
        const authResponse = await fetch('/api/user');
        
        if (authResponse.ok) {
            const authData = await authResponse.json();
            if (authData.success && authData.user) {
                // 用户已登录，初始化推荐系统
                await initializeRecommendationSystem();
                return;
            }
        }
        
        // 用户未登录，显示登录提示
        showAuthRequired();
        
    } catch (error) {
        console.error('Auth check failed:', error);
        showAuthRequired();
    }
}

function showAuthRequired() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="message agent-message">
            <div class="message-avatar">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 12l2 2 4-4"/>
                    <path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"/>
                    <path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3"/>
                </svg>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <p>🔐 需要登录才能使用引导推荐功能</p>
                    <p>请先登录您的账户，这样我就能根据您的阅读历史提供个性化推荐了。</p>
                    <button onclick="window.location.href='/'" style="margin-top: 10px; padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
                        返回首页登录
                    </button>
                </div>
                <div class="message-time">${new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        </div>
    `;
    
    // 禁用输入框
    document.getElementById('chat-input').disabled = true;
    document.getElementById('send-button').disabled = true;
    document.getElementById('session-status').textContent = '需要登录';
}

async function initializeRecommendationSystem() {
    try {
        const response = await fetch('/api/recommendation/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 包含cookies
            body: JSON.stringify({})
        });
        
        if (response.status === 401) {
            showAuthRequired();
            return;
        }
        
        if (response.ok) {
            const data = await response.json();
            addMessage('agent', data.message);
            updateUserProfile(data.user_profile);
            
            // 显示用户信息
            if (data.user_info) {
                document.getElementById('session-status').textContent = 
                    `欢迎，${data.user_info.username}！已分析您的阅读偏好`;
            }
        } else {
            addMessage('agent', '抱歉，推荐系统暂时无法使用。请稍后再试。');
        }
    } catch (error) {
        console.error('Failed to initialize recommendation system:', error);
        addMessage('agent', '连接失败，请检查网络后重试。');
    }
}

// 全局变量存储聊天记录
let chatHistory = [];

function addMessage(type, text) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                ${type === 'agent' ? 
                    '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>' :
                    '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'
                }
            </svg>
        </div>
        <div class="message-content">
            <div class="message-text">${text}</div>
            <div class="message-time">${timeString}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // 保存聊天记录到全局变量
    chatHistory.push({
        type: type,
        text: text,
        timestamp: now.toISOString()
    });
    
    // 显示保存按钮
    document.getElementById('save-chat-btn').style.display = 'block';
}

// 保存聊天记录功能
document.addEventListener('DOMContentLoaded', function() {
    const saveButton = document.getElementById('save-chat-btn');
    if (saveButton) {
        saveButton.addEventListener('click', saveChatHistory);
    }
});

// 保存聊天记录
function saveChatHistory() {
    if (chatHistory.length === 0) {
        alert('没有可保存的聊天记录');
        return;
    }
    
    // 创建完整聊天记录
    const fullChatHistory = {
        timestamp: new Date().toISOString(),
        messages: chatHistory,
        metadata: {
            user_agent: navigator.userAgent,
            platform: navigator.platform
        }
    };
    
    // 创建压缩版本（只保留文本内容）
    const compressedChatHistory = chatHistory.map(msg => {
        return {
            role: msg.type === 'agent' ? 'assistant' : 'user',
            content: msg.text
        };
    });
    
    // 将聊天记录转换为JSON字符串
    const fullChatJSON = JSON.stringify(fullChatHistory, null, 2);
    const compressedChatJSON = JSON.stringify(compressedChatHistory, null, 2);
    
    // 创建下载链接 - 完整版
    const fullDataBlob = new Blob([fullChatJSON], { type: 'application/json' });
    const fullDataURL = URL.createObjectURL(fullDataBlob);
    const fullDownloadLink = document.createElement('a');
    fullDownloadLink.href = fullDataURL;
    fullDownloadLink.download = `chat_history_full_${new Date().toISOString().slice(0,10)}.json`;
    
    // 创建下载链接 - 压缩版
    const compressedDataBlob = new Blob([compressedChatJSON], { type: 'application/json' });
    const compressedDataURL = URL.createObjectURL(compressedDataBlob);
    const compressedDownloadLink = document.createElement('a');
    compressedDownloadLink.href = compressedDataURL;
    compressedDownloadLink.download = `chat_history_${new Date().toISOString().slice(0,10)}.json`;
    
    // 触发下载
    document.body.appendChild(fullDownloadLink);
    fullDownloadLink.click();
    document.body.removeChild(fullDownloadLink);
    
    setTimeout(() => {
        document.body.appendChild(compressedDownloadLink);
        compressedDownloadLink.click();
        document.body.removeChild(compressedDownloadLink);
    }, 100);
    
    // 释放URL对象
    setTimeout(() => {
        URL.revokeObjectURL(fullDataURL);
        URL.revokeObjectURL(compressedDataURL);
    }, 1000);
}

function updateUserProfile(profile) {
    const statusEl = document.getElementById('session-status');
    if (profile && profile.recent_books) {
        statusEl.textContent = `已分析 ${profile.recent_books.length} 本书的阅读模式`;
    } else {
        statusEl.textContent = `已连接推荐系统`;
    }
}

// 发送消息功能
const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');

// 监听输入框变化，启用/禁用发送按钮
chatInput.addEventListener('input', function() {
    const hasText = this.value.trim().length > 0;
    sendButton.disabled = !hasText;
    
    // 自动调整文本框高度
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendButton.addEventListener('click', sendMessage);

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    addMessage('user', message);
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('send-button').disabled = true;
    
    try {
        const response = await fetch('/api/recommendation/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 包含cookies
            body: JSON.stringify({
                message: message
            })
        });
        
        if (response.status === 401) {
            addMessage('agent', '认证已过期，请重新登录。');
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
            return;
        }
        
        if (response.ok) {
            const data = await response.json();
            addMessage('agent', data.message);
            
            if (data.recommendations && data.recommendations.length > 0) {
                updateRecommendations(data.recommendations);
            }
        } else {
            addMessage('agent', '抱歉，暂时无法回复。请稍后再试。');
        }
    } catch (error) {
        console.error('Failed to send message:', error);
        addMessage('agent', '发送失败，请检查网络后重试。');
    }
}

async function updateRecommendations(recommendations) {
    const container = document.getElementById('recommendations-list');
    const countEl = document.getElementById('recommendation-count');
    
    container.innerHTML = '';
    countEl.textContent = `${recommendations.length}本书`;
    
    for (const book of recommendations) {
        // 尝试从数据库获取更多图书信息
        let bookDetails = await getBookDetails(book.title, book.author);
        let bookId = bookDetails ? bookDetails.id : null;
        
        // 尝试获取封面图片
        let coverUrl = `/covers/${book.title}_${book.author}.jpg`;
        
        const bookCard = document.createElement('div');
        bookCard.className = 'book-card';
        
        // 检查封面图片是否存在
        const coverExists = await checkImageExists(coverUrl);
        
        // 检查是否有已生成的内容
        const hasContent = book.has_content || false;
        const contentId = book.content_id || null;
        
        bookCard.innerHTML = `
            <div class="book-card-content">
                <div class="book-cover">
                    ${coverExists ? 
                        `<img src="${coverUrl}" alt="${book.title}" />` : 
                        `<div class="book-cover-placeholder">📚</div>`
                    }
                </div>
                <div class="book-info">
                    <h4>${book.title}</h4>
                    <p class="book-author">${book.author}</p>
                    <p class="book-reason">${book.reason}</p>
                    <div class="book-meta">
                        <span class="category-tag">${book.category || '未分类'}</span>
                        <span class="difficulty-tag">${book.difficulty || '普通'}</span>
                        ${hasContent ? '<span class="available-tag">已有内容</span>' : ''}
                    </div>
                </div>
            </div>
            <div class="book-actions">
                ${hasContent ? 
                    `<button class="book-action-btn primary" onclick="window.location.href='/ppt/${contentId}'">查看已有内容</button>` : 
                    bookId ? 
                        `<button class="book-action-btn" onclick="window.location.href='/book/${bookId}'">查看详情</button>` : 
                        `<button class="book-action-btn" onclick="searchBook('${book.title}', '${book.author}')">查找此书</button>`
                }
                <button class="book-action-btn" onclick="generateBookIntro('${book.title}', '${book.author}')">生成介绍</button>
            </div>
        `;
        container.appendChild(bookCard);
    }
}

// 检查图片是否存在
async function checkImageExists(url) {
    try {
        const response = await fetch(url, { method: 'HEAD' });
        return response.ok;
    } catch (e) {
        return false;
    }
}

// 搜索图书
function searchBook(title, author) {
    window.location.href = `/search?q=${encodeURIComponent(title)}`;
}

// 生成图书介绍
function generateBookIntro(title, author) {
    window.location.href = `/generate?title=${encodeURIComponent(title)}&author=${encodeURIComponent(author)}`;
}