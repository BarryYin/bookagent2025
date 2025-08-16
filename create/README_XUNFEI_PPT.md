# PPT配音工具 - 讯飞语音版本

## 功能特点

这个工具已经升级支持**讯飞语音合成**，提供高质量的中文语音合成服务。

### 语音合成优先级
1. **讯飞语音合成** (推荐) - 高质量中文语音
2. **Fish Audio** - 备选方案  
3. **系统语音** (macOS say) - 最后备选

## 快速使用

### 基本用法
```bash
# 使用默认配置
python ppt_voice_generator.py

# 指定HTML文件和音频前缀
python ppt_voice_generator.py your_ppt.html custom_prefix
```

### 环境变量配置
```bash
# 讯飞语音配置 (可选，有默认值)
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key" 
export XUNFEI_API_SECRET="your_api_secret"
export XUNFEI_VOICE="x4_xiaoguo"  # 发音人选择

# Fish Audio 配置 (可选)
export FISH_API_KEY="your_fish_api_key"
export FISH_REFERENCE_ID="your_reference_id"
```

## 发音人选择

讯飞语音提供多种发音人，通过 `XUNFEI_VOICE` 环境变量设置：

- `x4_xiaoguo` (默认) - 小果，活泼年轻女声
- `x4_yeting` - 叶婷，温柔甜美女声  
- `x4_qianxue` - 千雪，知性优雅女声
- `wangqianqian` - 王倩倩，标准普通话女声

## HTML格式要求

PPT HTML文件需要包含 `data-speech` 属性：

```html
<div data-speech="这里是第一页的配音文本">第1页内容</div>
<div data-speech="这里是第二页的配音文本">第2页内容</div>
```

## 输出文件

- 音频文件保存在 `ppt_audio/` 目录
- 文件命名格式：`{prefix}_{页码}.mp3`
- 自动生成播放列表：`{html文件名}配音列表.m3u`

## 测试工具

运行测试确保功能正常：
```bash
python test_xunfei_ppt.py
```

## 故障排除

### 讯飞语音合成失败
1. 检查网络连接
2. 验证API密钥是否正确
3. 确认账户余额充足
4. 检查发音人权限是否开通

### 依赖库问题
```bash
# 安装必需的库
pip install requests

# 可选：安装BeautifulSoup提升HTML解析性能
pip install beautifulsoup4

# 可选：安装Fish Audio SDK
pip install fish-audio-sdk
```

### 系统语音问题 (macOS)
```bash
# 检查系统语音可用性
say "测试语音"

# 安装ffmpeg (用于音频格式转换)
brew install ffmpeg
```

## 示例输出

```
🎵 PPT 配音生成器
============================================================
📄 HTML: 高效人士的7个习惯PPT演示.html
🔖 前缀: habit_slide
🎤 语音合成优先级: 讯飞(x4_xiaoguo) > Fish Audio > 系统语音

✅ 提取到 7 页配音文本
🎵 第1页: 156 字
🔄 使用讯飞语音合成…
✅ 讯飞语音: habit_slide_01.mp3
----------------------------------------
🎵 第2页: 203 字
🔄 使用讯飞语音合成…
✅ 讯飞语音: habit_slide_02.mp3
----------------------------------------

📊 统计
✅ 成功: 7/7 页
⏱️ 总时长: 67.3 秒 (≈1.1 分钟)
📁 输出目录: ppt_audio
📝 播放列表: 高效人士的7个习惯PPT演示配音列表.m3u

🎉 完成！可在 ppt_audio 目录查看
```

## 注意事项

1. **文本长度**: 讯飞API对单次合成文本长度有限制，建议每页PPT配音文本不超过1000字
2. **API调用频率**: 避免过于频繁的API调用，工具已内置适当的延时
3. **音频质量**: 讯飞语音合成生成16kHz MP3格式，质量良好适合PPT配音
4. **费用控制**: 讯飞语音合成按字符计费，请注意控制使用量

## 技术支持

如遇问题，请检查：
1. 网络连接是否正常
2. 讯飞API密钥配置是否正确  
3. 依赖库是否完整安装
4. HTML文件格式是否符合要求
