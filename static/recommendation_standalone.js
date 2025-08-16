/**
 * 引导推荐智能体交互脚本 - 独立版本
 */

// 全局变量存储聊天记录
let chatHistory = [];

// 初始化推荐会话
document.addEventListener('DOMContentLoaded', function() {
    initializeRecommendationSystem();
});

async function initializeRecommendationSystem() {
    try {
        const response = await fetch('/api/standalone-recommendation/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (response.ok) {
            const data = await response.json();
            addMessage('agent', data.message);
            
            // 显示用户信息
            if (data.user_info) {
                document.getElementById('session-status').textContent = 
                    `访客模式 - 无需登录`;
            }
        } else {
            addMessage('agent', '抱歉，推荐系统暂时无法使用。请稍后再试。');
        }
    } catch (error) {
        console.error('Failed to initialize recommendation system:', error);
        addMessage('agent', '连接失败，请检查网络后重试。');
    }
}

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
        const response = await fetch('/api/standalone-recommendation/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });
        
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
                    `<button class="book-action-btn primary" onclick="window.location.href='/outputs/${contentId}/presentation.html'">查看已有内容</button>` : 
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
    // 直接跳转到图书馆页面并带上搜索参数
    window.location.href = `/?search=${encodeURIComponent(title)}`;
}

// 生成图书介绍
function generateBookIntro(title, author) {
    // 由于独立版本没有生成功能，我们改为显示一个提示
    const message = `正在为《${title}》生成介绍...`;
    addMessage('agent', message);
    
    // 添加一个延迟，模拟生成过程
    setTimeout(() => {
        const introMessage = `《${title}》是${author}的代表作。
        
在访客模式下，无法使用完整的生成功能。如需生成详细的图书介绍，请登录系统或联系管理员。
        
您可以继续使用推荐功能，或者尝试询问我关于其他书籍的信息。`;
        
        addMessage('agent', introMessage);
    }, 1000);
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