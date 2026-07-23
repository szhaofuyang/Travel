import streamlit as st

def get_theme_css(theme, bg_color=None):
    """根据主题返回 CSS 样式字符串"""
    if theme == "浅色":
        bg = "#f5f5f7"
        card_bg = "#ffffff"
        text_color = "#1d1d1f"
        input_bg = "#fafafc"
        border_color = "#d2d2d7"
        shadow = "0 4px 16px rgba(0,0,0,0.04)"
        shadow_hover = "0 12px 32px rgba(0,0,0,0.08)"
    elif theme == "深色":
        bg = "#1c1c1e"
        card_bg = "#2c2c2e"
        text_color = "#f5f5f7"
        input_bg = "#3a3a3c"
        border_color = "#3a3a3c"
        shadow = "0 4px 16px rgba(0,0,0,0.3)"
        shadow_hover = "0 12px 32px rgba(0,0,0,0.5)"
    else:  # 自定义背景
        bg = bg_color or "#f5f5f7"
        # 根据背景亮度自动选择卡片颜色（简单处理）
        card_bg = "#ffffff" if theme == "浅色" else "#2c2c2e"
        text_color = "#1d1d1f" if theme == "浅色" else "#f5f5f7"
        input_bg = "#fafafc" if theme == "浅色" else "#3a3a3c"
        border_color = "#d2d2d7" if theme == "浅色" else "#3a3a3c"
        shadow = "0 4px 16px rgba(0,0,0,0.04)"
        shadow_hover = "0 12px 32px rgba(0,0,0,0.08)"

    css = f"""
    <style>
        /* 全局 */
        body {{
            background-color: {bg} !important;
            color: {text_color} !important;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}
        .stApp {{
            background-color: {bg} !important;
        }}
        /* 卡片 */
        .app-card {{
            background-color: {card_bg} !important;
            box-shadow: {shadow} !important;
            border-color: {border_color} !important;
        }}
        .app-card:hover {{
            box-shadow: {shadow_hover} !important;
        }}
        /* 输入框 */
        .stTextInput > div > div > input,
        .stDateInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {{
            background-color: {input_bg} !important;
            border-color: {border_color} !important;
            color: {text_color} !important;
        }}
        .stTextInput > div > div > input:focus,
        .stDateInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: #007aff !important;
            box-shadow: 0 0 0 4px rgba(0,122,255,0.15) !important;
        }}
        /* 选择框 */
        .stSelectbox > div > div {{
            background-color: {input_bg} !important;
            border-color: {border_color} !important;
            color: {text_color} !important;
        }}
        /* 按钮 */
        .stButton > button {{
            background-color: #007aff !important;
            color: white !important;
        }}
        .stButton > button:hover {{
            background-color: #0066d9 !important;
        }}
        /* 下载按钮 */
        .stDownloadButton > button {{
            background-color: #34c759 !important;
        }}
        .stDownloadButton > button:hover {{
            background-color: #2db84e !important;
        }}
        /* 展开器 */
        .streamlit-expanderHeader {{
            background-color: {card_bg} !important;
            border-color: {border_color} !important;
            color: {text_color} !important;
        }}
        .streamlit-expanderContent {{
            background-color: {card_bg} !important;
            border-color: {border_color} !important;
        }}
        /* 分割线 */
        hr {{
            background: linear-gradient(to right, {border_color}, #d2d2d7, {border_color}) !important;
        }}
        /* 侧边栏 */
        .css-1d391kg {{
            background-color: {card_bg} !important;
        }}
        .stAlert {{
            background-color: {card_bg} !important;
            border-color: {border_color} !important;
        }}
        /* 列表项 */
        .list-item {{
            border-bottom-color: {border_color} !important;
        }}
        /* 文本颜色 */
        h1, h2, h3, .name, .budget {{
            color: {text_color} !important;
        }}
        .city, .caption {{
            color: {text_color}90 !important;
        }}
        /* 状态标签保持不变 */
        .status-plan {{ background-color: #dbeafe; color: #1e40af; }}
        .status-visited {{ background-color: #d1fae5; color: #065f46; }}
    </style>
    """
    return css