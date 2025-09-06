import json

def generate_narration_data(processed_narrations):
    """生成解说词数据"""
    narration_data = []
    for i, narration in enumerate(processed_narrations):
        sentences = []
        timings = []
        
        # 按标点符号分割句子
        text = str(narration).strip()
        sentence_list = []
        for sent in text.split('。'):
            sent = sent.strip()
            if sent:
                sentence_list.append(sent + '。')
        
        # 如果没有按句号分割成功，尝试其他标点
        if len(sentence_list) <= 1:
            for sent in text.split('！'):
                sent = sent.strip()
                if sent:
                    sentence_list.append(sent + '！')
        
        if len(sentence_list) <= 1:
            for sent in text.split('？'):
                sent = sent.strip()
                if sent:
                    sentence_list.append(sent + '？')
        
        # 如果还是分割不了，就用整段文字
        if len(sentence_list) <= 1:
            sentence_list = [text]
        
        # 生成时间点（每句话间隔6秒）
        for j, sentence in enumerate(sentence_list):
            sentences.append(sentence)
            timings.append(j * 6)
        
        narration_data.append({
            "sentences": sentences,
            "timings": timings
        })
    
    return narration_data

def generate_modern_tech_slides_html(processed_slides, processed_narrations, final_book_title):
    """生成现代科技风格的slides HTML"""
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        narration_text = processed_narrations[i] if i < len(processed_narrations) else ""
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="tech-grid"></div>
                    <div style="display: flex; height: 100%; align-items: center; justify-content: center; position: relative; z-index: 2;">
                        <div style="text-align: center; max-width: 800px;">
                            <div style="background: linear-gradient(45deg, #00FFFF, #533483); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 4rem; font-weight: 900; margin-bottom: 2rem;">
                                {final_book_title}
                            </div>
                            <div style="height: 2px; width: 200px; background: linear-gradient(90deg, #00FFFF, #533483); margin: 2rem auto; border-radius: 1px;"></div>
                            <p style="font-size: 1.5rem; color: #E8E8E8; font-weight: 300; letter-spacing: 2px;">
                                🚀 智能书籍解读
                            </p>
                        </div>
                    </div>
                </div>'''
        else:
            content = slide.get('content', '')
            if isinstance(content, list):
                content_html = '<ul style="list-style: none; padding: 0;">'
                for item in content:
                    content_html += f'<li style="margin: 1rem 0; padding: 1rem; background: linear-gradient(135deg, rgba(33,150,243,0.1), rgba(255,152,0,0.1)); border-radius: 12px; border: 1px solid rgba(33,150,243,0.2);">▶ {str(item)}</li>'
                content_html += '</ul>'
            else:
                content_html = f'<p style="line-height: 1.7; font-size: 1.1rem; color: #263238; background: linear-gradient(135deg, rgba(33,150,243,0.05), rgba(255,255,255,0.95)); padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">{str(content).replace(chr(10), "<br>")}</p>'
                
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="tech-grid"></div>
                    <div style="position: relative; z-index: 2; padding: 3rem;">
                        <h2 style="font-size: 2.5rem; margin-bottom: 1.5rem; color: #1565C0; background: linear-gradient(45deg, #2196F3, #FF9800); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">{slide.get('title', f'第{i+1}页')}</h2>
                        {content_html}
                    </div>
                </div>'''
    
    return slides_html

def generate_elegant_art_slides_html(processed_slides, processed_narrations, final_book_title):
    """生成优雅艺术风格的slides HTML"""
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        narration_text = processed_narrations[i] if i < len(processed_narrations) else ""
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="ornament ornament-1"></div>
                    <div class="ornament ornament-2"></div>
                    <div style="display: flex; height: 100%; align-items: center; justify-content: center; position: relative; z-index: 2;">
                        <div style="text-align: center; max-width: 700px; padding: 2rem;">
                            <h1 class="gold-accent" style="font-size: 4rem; font-weight: 400; margin-bottom: 1rem; font-style: italic; letter-spacing: 3px;">
                                {final_book_title}
                            </h1>
                            <div style="width: 200px; height: 2px; background: linear-gradient(90deg, #B8860B, #C9B037, #DAA520); margin: 2rem auto; border-radius: 1px;"></div>
                            <p style="font-size: 1.4rem; color: #2C1810; font-style: italic; font-weight: 300; letter-spacing: 1px;">
                                ✨ 优雅的文学之旅
                            </p>
                        </div>
                    </div>
                </div>'''
        else:
            content = slide.get('content', '')
            if isinstance(content, list):
                content_html = '<div style="display: grid; gap: 1.5rem;">'
                for item in content:
                    content_html += f'<div style="background: linear-gradient(135deg, rgba(248,246,240,0.9), rgba(232,226,213,0.9)); border: 2px solid #B8860B; border-radius: 25px; padding: 2rem; text-align: center;"><p style="margin: 0; color: #2C1810; line-height: 1.8; font-style: italic;">• {str(item)}</p></div>'
                content_html += '</div>'
            else:
                content_html = f'<div style="background: rgba(248, 246, 240, 0.9); border: 2px solid #B8860B; border-radius: 25px; padding: 3rem;"><p style="color: #2C1810; font-size: 1.3rem; font-style: italic; line-height: 1.8;">{str(content).replace(chr(10), "<br>")}</p></div>'
                
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="ornament ornament-1"></div>
                    <div class="ornament ornament-2"></div>
                    <div style="position: relative; z-index: 2; padding: 3rem;">
                        <h2 class="gold-accent" style="font-size: 2.8rem; font-weight: 400; margin-bottom: 2rem; font-style: italic; text-align: center;">{slide.get('title', f'第{i+1}页')}</h2>
                        <div style="width: 120px; height: 2px; background: linear-gradient(90deg, #B8860B, #C9B037, #DAA520); margin: 0 auto 2rem;"></div>
                        {content_html}
                    </div>
                </div>'''
    
    return slides_html