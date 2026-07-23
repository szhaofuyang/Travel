import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
from fpdf import FPDF
from utils.db import get_all_places, get_total_budget, create_user, get_user
from utils.map_utils import generate_map
from utils.theme_utils import get_theme_css

st.set_page_config(page_title="旅游预算 · 首页", page_icon="✈️", layout="wide", initial_sidebar_state="collapsed")

# 加载静态样式（基础样式）
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 用户认证
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None

# 侧边栏（登录/注册 + 主题）
with st.sidebar:
    st.markdown("### 👤 用户中心")
    if st.session_state.user_id:
        st.write(f"已登录：**{st.session_state.username}**")
        if st.button("登出"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()
    else:
        with st.expander("登录", expanded=True):
            login_user = st.text_input("用户名", key="login_user")
            login_pass = st.text_input("密码", type="password", key="login_pass")
            if st.button("登录"):
                user = get_user(login_user, login_pass)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.username = user['username']
                    st.rerun()
                else:
                    st.error("用户名或密码错误")
        with st.expander("注册新账号"):
            reg_user = st.text_input("新用户名", key="reg_user")
            reg_pass = st.text_input("新密码", type="password", key="reg_pass")
            reg_pass2 = st.text_input("确认密码", type="password", key="reg_pass2")
            if st.button("注册"):
                if reg_pass != reg_pass2:
                    st.error("两次密码不一致")
                elif len(reg_user) < 3:
                    st.error("用户名至少3个字符")
                else:
                    uid = create_user(reg_user, reg_pass)
                    if uid:
                        st.success("注册成功，请登录")
                    else:
                        st.error("用户名已存在")

    st.sidebar.divider()
    st.sidebar.markdown("### 🎨 主题")
    theme = st.sidebar.selectbox(
        "选择主题",
        options=["浅色", "深色", "自定义背景"],
        index=0,
        key="theme_select"
    )
    if theme == "自定义背景":
        bg_color = st.sidebar.color_picker("背景颜色", "#f5f5f7", key="bg_color")
    else:
        bg_color = None
    st.session_state.theme = theme
    st.session_state.bg_color = bg_color

# 应用主题 CSS（立即生效）
theme = st.session_state.get('theme', '浅色')
bg_color = st.session_state.get('bg_color', None)
css = get_theme_css(theme, bg_color)
st.markdown(css, unsafe_allow_html=True)

# 未登录时阻断
if not st.session_state.user_id:
    st.warning("请先在左侧边栏登录或注册，以查看您的旅行计划。")
    st.stop()

# 主体
st.markdown('<h1 style="text-align:center;">✈️ 我的旅行计划</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center;color:#6e6e73;font-size:1.2rem;">用户：{st.session_state.username}</p>', unsafe_allow_html=True)
st.divider()

places = get_all_places(st.session_state.user_id)
plan_places = [p for p in places if p['status'] == 'plan']
visited_places = [p for p in places if p['status'] == 'visited']

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
        <div class="app-card" style="text-align:center;">
            <h3>📌 计划去</h3>
            <p style="font-size:2.5rem;font-weight:600;margin:0;">{len(plan_places)}</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="app-card" style="text-align:center;">
            <h3>✅ 已去过</h3>
            <p style="font-size:2.5rem;font-weight:600;margin:0;">{len(visited_places)}</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    total_budget = get_total_budget(places)
    st.markdown(f"""
        <div class="app-card" style="text-align:center;">
            <h3>💰 总预算</h3>
            <p style="font-size:2.5rem;font-weight:600;margin:0;">¥ {total_budget:,.0f}</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# 导出功能
st.markdown("### 📤 导出数据")
col_exp1, col_exp2 = st.columns(2)

def export_csv(places):
    if not places:
        return None
    df = pd.DataFrame([{
        '名称': p['name'],
        '城市': p['city'],
        '状态': '计划去' if p['status']=='plan' else '已去',
        '开始日期': p['start_date'],
        '结束日期': p['end_date'],
        '餐饮预算': p['budget_food'],
        '住宿预算': p['budget_accommodation'],
        '大交通预算': p['budget_transport_big'],
        '小交通预算': p['budget_transport_small'],
        '门票预算': p['budget_ticket'],
        '备注': p['notes'] or ''
    } for p in places])
    return df.to_csv(index=False).encode('utf-8-sig')

def export_pdf(places, username):
    if not places:
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"旅行计划报告 - {username}", ln=True, align='C')
    pdf.ln(10)
    headers = ['名称', '城市', '状态', '开始', '结束', '餐饮', '住宿', '大交通', '小交通', '门票', '备注']
    col_widths = [30, 30, 20, 22, 22, 20, 20, 22, 22, 20, 30]
    pdf.set_font("Arial", 'B', 8)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()
    pdf.set_font("Arial", '', 8)
    for p in places:
        row = [
            p['name'], p['city'],
            '计划' if p['status']=='plan' else '已去',
            p['start_date'] or '', p['end_date'] or '',
            f"{p['budget_food']:.0f}", f"{p['budget_accommodation']:.0f}",
            f"{p['budget_transport_big']:.0f}", f"{p['budget_transport_small']:.0f}",
            f"{p['budget_ticket']:.0f}", p['notes'] or ''
        ]
        for i, item in enumerate(row):
            pdf.cell(col_widths[i], 8, str(item), border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin1')

with col_exp1:
    csv_data = export_csv(places)
    if csv_data:
        st.download_button(
            label="📥 导出 CSV",
            data=csv_data,
            file_name=f"travel_plan_{st.session_state.username}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("暂无数据可导出")

with col_exp2:
    pdf_data = export_pdf(places, st.session_state.username)
    if pdf_data:
        st.download_button(
            label="📄 导出 PDF 报告",
            data=pdf_data,
            file_name=f"travel_plan_{st.session_state.username}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("暂无数据")

st.divider()

# 地图
st.markdown('<h2>🗺️ 足迹地图</h2>', unsafe_allow_html=True)
if places:
    m = generate_map(places, highlight_status=None)
    st_folium(m, width='100%', height=500, returned_objects=[])
else:
    st.info("还没有任何目的地，去「计划去」或「已去」页面添加吧！")

st.divider()

# 计划列表
st.markdown('<h2>📋 计划去的目的地</h2>', unsafe_allow_html=True)
if plan_places:
    for p in plan_places:
        with st.container():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"""
                    <div class="list-item">
                        <div>
                            <span class="name">{p['name']}</span>
                            <span class="city">📍 {p['city']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_b:
                total = p['budget_food'] + p['budget_accommodation'] + p['budget_transport_big'] + p['budget_transport_small'] + p['budget_ticket']
                st.markdown(f'<span style="font-weight:600;">¥ {total:,.0f}</span>', unsafe_allow_html=True)
            with col_c:
                if st.button("查看", key=f"view_plan_{p['id']}"):
                    st.query_params['id'] = p['id']
                    st.switch_page("pages/计划去.py")  # 注意：此处应跳转到详情页，但详情页是"详情.py"
                    # 修正：应该跳转到 "pages/详情.py"
                    st.switch_page("pages/详情.py")
else:
    st.caption("暂无计划，去「计划去」页面添加吧。")