// 修复PPT画廊的JavaScript代码
console.log('PPT画廊修复脚本加载...');

// 等待页面加载完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化PPT画廊...');
    
    // 延迟一点时间确保所有资源加载完成
    setTimeout(() => {
        loadPPTGalleryFixed();
    }, 1000);
});

// 修复版的PPT画廊加载函数
async function loadPPTGalleryFixed() {
    console.log('开始加载PPT画廊...');
    const pptGrid = document.getElementById('ppt-grid');
    
    if (!pptGrid) {
        console.error('找不到ppt-grid元素');
        return;
    }
    
    try {
        console.log('发送API请求...');
        const response = await fetch('/api/generated-ppts?limit=3');
        console.log('API响应状态:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('API返回数据:', data);
        
        if (data.ppts && data.ppts.length > 0) {
            console.log(`找到 ${data.ppts.length} 个PPT，开始渲染...`);
            renderPPTCardsFixed(data.ppts);
        } else {
            console.log('没有找到PPT');
            renderEmptyGalleryFixed();
        }
    } catch (error) {
        console.error('加载PPT画廊失败:', error);
        renderErrorGalleryFixed();
    }
}

// 渲染PPT卡片（带图片预览）
function renderPPTCardsFixed(ppts) {
    const pptGrid = document.getElementById('ppt-grid');
    pptGrid.innerHTML = '';
    
    ppts.forEach((ppt, index) => {
        const card = document.createElement('div');
        card.className = 'ppt-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        // 生成渐变背景色
        const gradients = [
            'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
        ];
        const gradient = gradients[index % gradients.length];
        
        card.innerHTML = `
            <div class="ppt-card-header">
                <h3 class="ppt-card-title">${escapeHtmlFixed(ppt.title)}</h3>
                <div class="ppt-card-meta">
                    <span>${ppt.created_time}</span>
                    <span>${ppt.session_id.substring(0, 8)}...</span>
                </div>
            </div>
            <div class="ppt-card-preview">
                <div class="ppt-preview-image" style="
                    width: 100%;
                    height: 120px;
                    background: ${gradient};
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 1.2rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                ">
                    <div style="text-align: center; z-index: 2;">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📚</div>
                        <div style="font-size: 1.1rem;">${escapeHtmlFixed(ppt.title)}</div>
                        <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.25rem;">PPT演示</div>
                    </div>
                    <div style="
                        position: absolute;
                        top: -50%;
                        right: -50%;
                        width: 200%;
                        height: 200%;
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                        animation: shimmer 3s ease-in-out infinite;
                    "></div>
                </div>
                <div style="font-size: 0.85rem; color: #666; line-height: 1.4;">
                    点击查看完整的PPT演示
                </div>
            </div>
            <div class="ppt-card-actions">
                <a href="${ppt.html_url}" target="_blank" class="action-btn primary">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15,3 21,3 21,9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    查看PPT
                </a>
                <button class="action-btn" onclick="copyPPTLinkFixed('${ppt.html_url}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
                    复制链接
                </button>
            </div>
        `;
        
        pptGrid.appendChild(card);
    });
    
    // 添加查看更多卡片
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
        viewMoreCard.addEventListener('click', showAllPPTsFixed);
        pptGrid.appendChild(viewMoreCard);
    }
}



// 显示所有PPT
async function showAllPPTsFixed() {
    try {
        const response = await fetch('/api/generated-ppts');
        const data = await response.json();
        
        if (data.ppts && data.ppts.length > 0) {
            renderPPTCardsFixed(data.ppts);
            
            // 更新标题
            const galleryHeader = document.querySelector('.gallery-header h2');
            if (galleryHeader) {
                galleryHeader.textContent = `所有PPT (${data.ppts.length}个)`;
            }
        }
    } catch (error) {
        console.error('加载所有PPT失败:', error);
    }
}

// 渲染空画廊
function renderEmptyGalleryFixed() {
    const pptGrid = document.getElementById('ppt-grid');
    pptGrid.innerHTML = `
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

// 渲染错误画廊
function renderErrorGalleryFixed() {
    const pptGrid = document.getElementById('ppt-grid');
    pptGrid.innerHTML = `
        <div class="empty-gallery">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <p>加载PPT列表失败</p>
            <button class="action-btn" onclick="loadPPTGalleryFixed()" style="margin-top: 1rem;">重试</button>
        </div>
    `;
}

// 复制链接
function copyPPTLinkFixed(url) {
    const fullUrl = window.location.origin + url;
    navigator.clipboard.writeText(fullUrl).then(() => {
        console.log('链接已复制:', fullUrl);
        // 简单提示
        alert('链接已复制到剪贴板！');
    }).catch(err => {
        console.error('复制失败:', err);
    });
}

// HTML转义
function escapeHtmlFixed(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 全局函数，供按钮调用
window.loadPPTsNow = loadPPTGalleryFixed;
window.copyPPTLinkFixed = copyPPTLinkFixed;
window.showAllPPTsFixed = showAllPPTsFixed;

console.log('PPT画廊修复脚本加载完成！');