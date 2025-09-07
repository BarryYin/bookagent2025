import json

def generate_narration_data(processed_narrations):
    """生成解说词数据 - 增强版，支持更智能的分割"""
    narration_data = []
    for i, narration in enumerate(processed_narrations):
        sentences = []
        timings = []
        
        # 按标点符号分割句子
        text = str(narration).strip()
        sentence_list = []
        
        # 更智能的句子分割，考虑多种标点符号
        import re
        # 按句号、感叹号、问号分割，但保留标点
        parts = re.split(r'([。！？])', text)
        current_sentence = ""
        
        for part in parts:
            if part in ['。', '！', '？']:
                if current_sentence.strip():
                    sentence_list.append(current_sentence.strip() + part)
                    current_sentence = ""
            else:
                current_sentence += part
        
        # 处理最后一个句子（如果没有标点结尾）
        if current_sentence.strip():
            sentence_list.append(current_sentence.strip())
        
        # 如果分割后句子太少，尝试按逗号、分号等分割
        if len(sentence_list) <= 2 and len(text) > 100:
            # 按逗号分割长句子
            temp_list = []
            for sentence in sentence_list:
                if len(sentence) > 80:  # 长句子进一步分割
                    parts = sentence.split('，')
                    for j, part in enumerate(parts):
                        if j < len(parts) - 1:
                            temp_list.append(part + '，')
                        else:
                            temp_list.append(part)
                else:
                    temp_list.append(sentence)
            sentence_list = temp_list
        
        # 如果还是分割不了，就用整段文字
        if not sentence_list:
            sentence_list = [text]
        
        # 生成时间点（根据句子长度动态调整间隔）
        for j, sentence in enumerate(sentence_list):
            sentences.append(sentence)
            # 根据句子长度调整时间间隔（短句4秒，长句8秒）
            if len(sentence) < 30:
                interval = 4
            elif len(sentence) < 60:
                interval = 6
            else:
                interval = 8
            
            timings.append(j * interval)
        
        narration_data.append({
            "sentences": sentences,
            "timings": timings
        })
    
    return narration_data

def generate_modern_tech_slides_html(processed_slides, processed_narrations, final_book_title):
    """生成现代科技风格的slides HTML - 增强版，支持丰富内容结构"""
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        narration_text = processed_narrations[i] if i < len(processed_narrations) else ""
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            # 首页 - 更加丰富的内容
            subtitle = slide.get('subtitle', '智能书籍解读')
            content = slide.get('content', '')
            
            # 如果首页有内容，也要显示
            content_html = ""
            if content and str(content).strip():
                if isinstance(content, list):
                    content_html = '<div style="margin-top: 2rem; display: grid; gap: 1rem;">'
                    for j, item in enumerate(content[:3]):  # 首页最多显示3个要点
                        content_html += f'''
                            <div style="background: rgba(0,255,255,0.1); border: 1px solid rgba(0,255,255,0.3); 
                                        border-radius: 10px; padding: 1rem; text-align: center;">
                                <div style="color: #00FFFF; font-size: 1.1rem; font-weight: 500;">{str(item)}</div>
                            </div>'''
                    content_html += '</div>'
                else:
                    content_html = f'''
                        <div style="margin-top: 2rem; background: rgba(0,255,255,0.05); border: 1px solid rgba(0,255,255,0.2); 
                                    border-radius: 15px; padding: 2rem; text-align: center;">
                            <p style="color: #E8E8E8; font-size: 1.2rem; line-height: 1.6; margin: 0;">{str(content)[:200]}{'...' if len(str(content)) > 200 else ''}</p>
                        </div>'''
            
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="tech-grid"></div>
                    <div style="display: flex; height: 100%; align-items: center; justify-content: center; position: relative; z-index: 2;">
                        <div style="text-align: center; max-width: 900px; padding: 2rem;">
                            <div style="background: linear-gradient(45deg, #00FFFF, #533483); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 4rem; font-weight: 900; margin-bottom: 1rem;">
                                {final_book_title}
                            </div>
                            <div style="height: 3px; width: 250px; background: linear-gradient(90deg, #00FFFF, #533483); margin: 2rem auto; border-radius: 2px;"></div>
                            <p style="font-size: 1.8rem; color: #E8E8E8; font-weight: 300; letter-spacing: 2px; margin-bottom: 2rem;">
                                🚀 {subtitle}
                            </p>
                            {content_html}
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
                                <div style="background: rgba(0,255,255,0.1); border: 1px solid rgba(0,255,255,0.3); border-radius: 10px; padding: 1rem;">
                                    <div style="color: #00FFFF; font-size: 1.2rem; margin-bottom: 0.5rem;">📚 深度解读</div>
                                    <div style="color: #E8E8E8; font-size: 0.9rem;">专业视角分析</div>
                                </div>
                                <div style="background: rgba(83,52,131,0.1); border: 1px solid rgba(83,52,131,0.3); border-radius: 10px; padding: 1rem;">
                                    <div style="color: #533483; font-size: 1.2rem; margin-bottom: 0.5rem;">🎨 多元视角</div>
                                    <div style="color: #E8E8E8; font-size: 0.9rem;">全方位理解</div>
                                </div>
                                <div style="background: rgba(255,152,0,0.1); border: 1px solid rgba(255,152,0,0.3); border-radius: 10px; padding: 1rem;">
                                    <div style="color: #FF9800; font-size: 1.2rem; margin-bottom: 0.5rem;">✨ 智能分析</div>
                                    <div style="color: #E8E8E8; font-size: 0.9rem;">现代科技助力</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>'''
        else:
            # 内容页 - 更好地处理丰富内容
            content = slide.get('content', '')
            subtitle = slide.get('subtitle', '')
            key_message = slide.get('key_message', '')
            
            # 确保内容不为空
            if not content or str(content).strip() == '':
                content = f"这是第{i+1}页的内容，正在为您展示相关信息。"
            
            # 处理内容的不同格式
            if isinstance(content, list):
                content_html = '<div style="display: grid; gap: 1.5rem;">'
                for j, item in enumerate(content):
                    if str(item).strip():  # 确保项目不为空
                        icon = ['🔹', '🔸', '🔷', '🔶'][j % 4]
                        content_html += f'''
                            <div style="background: linear-gradient(135deg, rgba(0,255,255,0.1), rgba(83,52,131,0.1)); 
                                        border: 1px solid rgba(0,255,255,0.3); border-radius: 15px; padding: 2rem;
                                        transition: all 0.3s ease; position: relative; overflow: hidden;">
                                <div style="position: absolute; top: -50%; right: -50%; width: 100px; height: 100px; 
                                            background: radial-gradient(circle, rgba(0,255,255,0.1), transparent); 
                                            border-radius: 50%;"></div>
                                <div style="position: relative; z-index: 2;">
                                    <span style="color: #00FFFF; font-size: 1.3rem; margin-right: 1rem;">{icon}</span>
                                    <span style="color: #FFFFFF; font-size: 1.2rem; line-height: 1.7; font-weight: 500;">{str(item)}</span>
                                </div>
                            </div>'''
                content_html += '</div>'
            else:
                # 处理文本内容，支持段落分割和句子分割
                text_content = str(content).strip()
                
                # 首先尝试按段落分割
                paragraphs = text_content.split('\n\n')
                if len(paragraphs) == 1:
                    # 如果没有段落分割，尝试按句子分割
                    import re
                    sentences = re.split(r'[。！？]', text_content)
                    sentences = [s.strip() + ('。' if not s.strip().endswith(('。', '！', '？')) and s.strip() else '') 
                               for s in sentences if s.strip()]
                    if len(sentences) > 1:
                        paragraphs = sentences
                
                content_html = '<div style="display: grid; gap: 2rem;">'
                for k, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        # 检查是否是列表项
                        if paragraph.strip().startswith('•') or paragraph.strip().startswith('-') or paragraph.strip().startswith('*'):
                            # 列表项样式
                            content_html += f'''
                                <div style="background: linear-gradient(135deg, rgba(0,255,255,0.08), rgba(15,15,35,0.95)); 
                                            border-left: 4px solid #00FFFF; border-radius: 0 12px 12px 0; 
                                            padding: 2rem; box-shadow: 0 4px 12px rgba(0,255,255,0.2);">
                                    <p style="color: #FFFFFF; font-size: 1.2rem; line-height: 1.8; margin: 0; font-weight: 500;">{paragraph.strip()}</p>
                                </div>'''
                        else:
                            # 普通段落样式
                            content_html += f'''
                                <div style="background: linear-gradient(135deg, rgba(0,255,255,0.05), rgba(15,15,35,0.95)); 
                                            border: 1px solid rgba(0,255,255,0.2); border-radius: 15px; 
                                            padding: 2.5rem; box-shadow: 0 6px 20px rgba(0,255,255,0.1);">
                                    <p style="color: #FFFFFF; font-size: 1.2rem; line-height: 1.8; margin: 0; font-weight: 500; text-align: justify;">{paragraph.strip().replace(chr(10), "<br>")}</p>
                                </div>'''
                content_html += '</div>'
            
            # 添加关键信息显示
            key_message_html = ""
            if key_message:
                key_message_html = f'''
                    <div style="background: linear-gradient(45deg, #00FFFF, #533483); border-radius: 15px; 
                                padding: 2rem; margin-top: 2rem; text-align: center; box-shadow: 0 8px 25px rgba(0,255,255,0.3);">
                        <div style="color: white; font-size: 1.3rem; font-weight: 600; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            💡 {key_message}
                        </div>
                    </div>'''
                
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="tech-grid"></div>
                    <div style="position: relative; z-index: 2; padding: 2rem; height: 100%; overflow-y: auto;">
                        <div style="max-width: 1000px; margin: 0 auto;">
                            <h2 style="font-size: 2.8rem; margin-bottom: 1rem; color: #00FFFF; 
                                       background: linear-gradient(45deg, #00FFFF, #533483); 
                                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                                       font-weight: 900; text-align: center; text-shadow: 0 0 20px rgba(0,255,255,0.3);">{slide.get('title', f'第{i+1}页')}</h2>
                            {f'<p style="text-align: center; color: #E8E8E8; font-size: 1.3rem; margin-bottom: 2rem; font-style: italic; opacity: 0.8;">{subtitle}</p>' if subtitle else ''}
                            <div style="margin-top: 2rem;">
                                {content_html}
                            </div>
                            {key_message_html}
                        </div>
                    </div>
                </div>'''
    
    return slides_html

def generate_elegant_art_slides_html(processed_slides, processed_narrations, final_book_title):
    """生成优雅艺术风格的slides HTML - 增强版，支持丰富内容结构"""
    slides_html = ""
    for i, slide in enumerate(processed_slides):
        active_class = "active" if i == 0 else ""
        narration_text = processed_narrations[i] if i < len(processed_narrations) else ""
        narration_text = str(narration_text).replace('"', '&quot;').replace('\n', ' ').replace('\r', '')
        
        if i == 0:
            # 首页 - 更加优雅的内容
            subtitle = slide.get('subtitle', '优雅的文学之旅')
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="ornament ornament-1"></div>
                    <div class="ornament ornament-2"></div>
                    <div style="display: flex; height: 100%; align-items: center; justify-content: center; position: relative; z-index: 2;">
                        <div style="text-align: center; max-width: 800px; padding: 3rem;">
                            <h1 class="gold-accent" style="font-size: 4.5rem; font-weight: 400; margin-bottom: 1rem; 
                                                      font-style: italic; letter-spacing: 3px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                                {final_book_title}
                            </h1>
                            <div style="width: 250px; height: 3px; background: linear-gradient(90deg, #B8860B, #C9B037, #DAA520); 
                                        margin: 2rem auto; border-radius: 2px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                            <p style="font-size: 1.6rem; color: #2C1810; font-style: italic; font-weight: 300; 
                                      letter-spacing: 1px; margin-bottom: 2rem;">
                                ✨ {subtitle}
                            </p>
                            <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 3rem; flex-wrap: wrap;">
                                <div style="background: rgba(248,246,240,0.8); border: 2px solid #B8860B; border-radius: 20px; 
                                           padding: 1.5rem; min-width: 150px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                    <div style="color: #B8860B; font-size: 2rem; margin-bottom: 0.5rem;">📜</div>
                                    <div style="color: #2C1810; font-size: 1rem; font-style: italic;">文学之美</div>
                                </div>
                                <div style="background: rgba(248,246,240,0.8); border: 2px solid #B8860B; border-radius: 20px; 
                                           padding: 1.5rem; min-width: 150px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                    <div style="color: #B8860B; font-size: 2rem; margin-bottom: 0.5rem;">🎨</div>
                                    <div style="color: #2C1810; font-size: 1rem; font-style: italic;">艺术价值</div>
                                </div>
                                <div style="background: rgba(248,246,240,0.8); border: 2px solid #B8860B; border-radius: 20px; 
                                           padding: 1.5rem; min-width: 150px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                                    <div style="color: #B8860B; font-size: 2rem; margin-bottom: 0.5rem;">🕰️</div>
                                    <div style="color: #2C1810; font-size: 1rem; font-style: italic;">永恒价值</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>'''
        else:
            # 内容页 - 更好地处理丰富内容
            content = slide.get('content', '')
            subtitle = slide.get('subtitle', '')
            key_message = slide.get('key_message', '')
            
            # 处理内容的不同格式
            if isinstance(content, list):
                content_html = '<div style="display: grid; gap: 2rem;">'
                for j, item in enumerate(content):
                    ornament = ['🌿', '🌸', '🌺', '🌼'][j % 4]
                    content_html += f'''
                        <div style="background: linear-gradient(135deg, rgba(248,246,240,0.95), rgba(232,226,213,0.9)); 
                                    border: 2px solid #B8860B; border-radius: 25px; padding: 2.5rem; 
                                    text-align: center; position: relative; overflow: hidden;
                                    box-shadow: 0 6px 20px rgba(184,134,11,0.2);">
                            <div style="position: absolute; top: 10px; right: 15px; color: #B8860B; 
                                        font-size: 1.5rem; opacity: 0.6;">{ornament}</div>
                            <p style="margin: 0; color: #2C1810; line-height: 1.8; font-style: italic; 
                                      font-size: 1.2rem; position: relative; z-index: 2;">
                                • {str(item)}
                            </p>
                        </div>'''
                content_html += '</div>'
            else:
                # 处理文本内容，支持段落分割
                paragraphs = str(content).split('\n\n')
                content_html = '<div style="display: grid; gap: 2rem;">'
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # 检查是否是列表项
                        if paragraph.strip().startswith('•') or paragraph.strip().startswith('-'):
                            # 列表项样式
                            content_html += f'''
                                <div style="background: rgba(248, 246, 240, 0.9); border-left: 4px solid #B8860B; 
                                            border-radius: 0 20px 20px 0; padding: 2rem; 
                                            box-shadow: 0 4px 15px rgba(184,134,11,0.15);">
                                    <p style="color: #2C1810; font-size: 1.2rem; font-style: italic; 
                                              line-height: 1.8; margin: 0;">{paragraph.strip()}</p>
                                </div>'''
                        else:
                            # 普通段落样式
                            content_html += f'''
                                <div style="background: rgba(248, 246, 240, 0.9); border: 2px solid #B8860B; 
                                            border-radius: 25px; padding: 3rem; text-align: justify;
                                            box-shadow: 0 6px 20px rgba(184,134,11,0.2);">
                                    <p style="color: #2C1810; font-size: 1.3rem; font-style: italic; 
                                              line-height: 1.8; margin: 0;">{paragraph.strip().replace(chr(10), "<br>")}</p>
                                </div>'''
                content_html += '</div>'
            
            # 添加关键信息显示
            key_message_html = ""
            if key_message:
                key_message_html = f'''
                    <div style="background: linear-gradient(45deg, #B8860B, #C9B037, #DAA520); 
                                border-radius: 25px; padding: 2rem; margin-top: 2rem; text-align: center;
                                box-shadow: 0 8px 25px rgba(184,134,11,0.3);">
                        <div style="color: white; font-size: 1.3rem; font-weight: 600; font-style: italic;
                                   text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                            ✨ {key_message}
                        </div>
                    </div>'''
                
            slides_html += f'''
                <div class="slide {active_class}" data-speech="{narration_text}">
                    <div class="ornament ornament-1"></div>
                    <div class="ornament ornament-2"></div>
                    <div style="position: relative; z-index: 2; padding: 2rem; height: 100%; overflow-y: auto;">
                        <div style="max-width: 900px; margin: 0 auto;">
                            <h2 class="gold-accent" style="font-size: 3rem; font-weight: 400; margin-bottom: 0.5rem; 
                                                      font-style: italic; text-align: center; 
                                                      text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">{slide.get('title', f'第{i+1}页')}</h2>
                            {f'<p style="text-align: center; color: #8B4513; font-size: 1.3rem; margin-bottom: 1rem; font-style: italic;">{subtitle}</p>' if subtitle else ''}
                            <div style="width: 150px; height: 2px; background: linear-gradient(90deg, #B8860B, #C9B037, #DAA520); 
                                        margin: 0 auto 3rem; border-radius: 1px;"></div>
                            <div style="margin-top: 2rem;">
                                {content_html}
                            </div>
                            {key_message_html}
                        </div>
                    </div>
                </div>'''
    
    return slides_html