/**
 * 图片尺寸自适应工具
 * 根据图片的宽高比自动调整容器尺寸和显示方式
 */

// 通用图片适配函数
function adaptImageSize(img, options = {}) {
    if (!img || !img.naturalWidth || !img.naturalHeight) {
        return;
    }
    
    const container = img.parentElement;
    const aspectRatio = img.naturalWidth / img.naturalHeight;
    
    // 默认配置
    const config = {
        landscapeThreshold: 1.5,    // 横向图片阈值
        portraitThreshold: 0.7,     // 纵向图片阈值
        defaultHeight: 200,         // 默认高度
        landscapeHeight: 150,       // 横向图片高度
        portraitHeight: 250,        // 纵向图片高度
        useTransition: true,        // 是否使用过渡动画
        ...options
    };
    
    // 根据宽高比调整容器
    if (aspectRatio > config.landscapeThreshold) {
        // 横向图片
        container.style.height = config.landscapeHeight + 'px';
        img.classList.add('landscape');
        img.classList.remove('portrait', 'square');
    } else if (aspectRatio < config.portraitThreshold) {
        // 纵向图片
        container.style.height = config.portraitHeight + 'px';
        img.classList.add('portrait');
        img.classList.remove('landscape', 'square');
    } else {
        // 正常比例
        container.style.height = config.defaultHeight + 'px';
        img.classList.add('square');
        img.classList.remove('landscape', 'portrait');
    }
    
    // 添加过渡动画
    if (config.useTransition) {
        container.style.transition = 'height 0.3s ease';
        img.style.transition = 'object-fit 0.3s ease';
    }
    
    // 添加适配容器类
    container.classList.add('adaptive-image-container');
    img.classList.add('adaptive-image');
}

// 书籍封面适配函数
function adaptBookCoverSize(img) {
    adaptImageSize(img, {
        landscapeThreshold: 1.2,
        portraitThreshold: 0.6,
        defaultHeight: 100,
        landscapeHeight: 80,
        portraitHeight: 120
    });
}

// 图书馆卡片封面适配函数
function adaptLibraryCardCover(img) {
    adaptImageSize(img, {
        landscapeThreshold: 1.5,
        portraitThreshold: 0.7,
        defaultHeight: 200,
        landscapeHeight: 150,
        portraitHeight: 250
    });
}

// 批量处理页面中的所有图片
function adaptAllImages(selector = '.adaptive-image') {
    const images = document.querySelectorAll(selector);
    images.forEach(img => {
        if (img.complete && img.naturalWidth > 0) {
            adaptImageSize(img);
        } else {
            img.addEventListener('load', () => adaptImageSize(img));
        }
    });
}

// 监听DOM变化，自动处理新添加的图片
function observeImageChanges() {
    const observer = new MutationObserver(mutations => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    // 检查新添加的元素是否包含需要适配的图片
                    const images = node.querySelectorAll ? node.querySelectorAll('img[data-adaptive]') : [];
                    images.forEach(img => {
                        if (img.complete && img.naturalWidth > 0) {
                            adaptImageSize(img);
                        } else {
                            img.addEventListener('load', () => adaptImageSize(img));
                        }
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// 暴露到全局作用域
window.adaptImageSize = adaptImageSize;
window.adaptBookCoverSize = adaptBookCoverSize;
window.adaptLibraryCardCover = adaptLibraryCardCover;
window.adaptAllImages = adaptAllImages;

// 页面加载完成后自动处理
document.addEventListener('DOMContentLoaded', function() {
    // 处理已有的图片
    adaptAllImages();
    
    // 开始监听DOM变化
    observeImageChanges();
});