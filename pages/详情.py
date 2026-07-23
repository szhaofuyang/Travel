import streamlit as st
from utils.db import get_place_by_id, update_place, delete_place
from utils.map_utils import geocode_city
from utils.theme_utils import get_theme_css
from datetime import date

st.set_page_config(page_title="详情", page_icon="📝", layout="wide")
with open('static/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 应用主题
theme = st.session_state.get('theme', '浅色')
bg_color = st.session_state.get('bg_color', None)
css = get_theme_css(theme, bg_color)
st.markdown(css, unsafe_allow_html=True)

if not st.session_state.get('user_id'):
    st.warning("请先登录")
    st.stop()

user_id = st.session_state.user_id

pid = st.query_params.get('id')
if not pid:
    st.error("未指定目的地 ID，请从列表进入。")
    st.stop()
try:
    pid = int(pid)
except ValueError:
    st.error("无效的 ID。")
    st.stop()

place = get_place_by_id(user_id, pid)
if not place:
    st.error(f"未找到 ID 为 {pid} 的目的地，或您无权访问。")
    st.stop()

p = dict(place)

st.markdown(f'<h1>📝 {p["name"]}</h1>', unsafe_allow_html=True)
status_label = "计划去" if p['status'] == 'plan' else "已去"
st.markdown(f'<span class="status-badge status-{p["status"]}">{status_label}</span>', unsafe_allow_html=True)

with st.form("edit_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("目的地名称", value=p['name'])
        city = st.text_input("城市", value=p['city'])
        status = st.selectbox("状态", options=['plan', 'visited'], index=0 if p['status']=='plan' else 1,
                              format_func=lambda x: "计划去" if x=='plan' else "已去")
        start_date = st.date_input("开始日期", value=date.fromisoformat(p['start_date']) if p['start_date'] else date.today())
        end_date = st.date_input("结束日期", value=date.fromisoformat(p['end_date']) if p['end_date'] else date.today())
    with col2:
        budget_food = st.number_input("🍜 餐饮", min_value=0.0, step=50.0, value=float(p['budget_food']))
        budget_accommodation = st.number_input("🏨 住宿", min_value=0.0, step=50.0, value=float(p['budget_accommodation']))
        budget_transport_big = st.number_input("🚆 大交通", min_value=0.0, step=50.0, value=float(p['budget_transport_big']))
        budget_transport_small = st.number_input("🚌 小交通", min_value=0.0, step=50.0, value=float(p['budget_transport_small']))
        budget_ticket = st.number_input("🎟️ 门票", min_value=0.0, step=50.0, value=float(p['budget_ticket']))
    notes = st.text_area("备注", value=p['notes'] or "")
    
    col_save, col_del = st.columns([1, 1])
    with col_save:
        submitted = st.form_submit_button("💾 保存修改", use_container_width=True)
    with col_del:
        delete_btn = st.form_submit_button("🗑️ 删除此目的地", use_container_width=True, type="primary")

    if submitted:
        lat, lng = p['lat'], p['lng']
        if city != p['city']:
            new_lat, new_lng = geocode_city(city)
            if new_lat is not None and new_lng is not None:
                lat, lng = new_lat, new_lng
            else:
                st.warning("无法获取新城市的坐标，保留原有坐标。")
        data = {
            'name': name,
            'city': city,
            'lat': lat,
            'lng': lng,
            'status': status,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'budget_food': budget_food,
            'budget_accommodation': budget_accommodation,
            'budget_transport_big': budget_transport_big,
            'budget_transport_small': budget_transport_small,
            'budget_ticket': budget_ticket,
            'notes': notes
        }
        update_place(user_id, pid, data)
        st.success("✅ 修改已保存")
        st.rerun()
    
    if delete_btn:
        delete_place(user_id, pid)
        st.success("🗑️ 已删除此目的地")
        st.switch_page("app.py")

total = p['budget_food'] + p['budget_accommodation'] + p['budget_transport_big'] + p['budget_transport_small'] + p['budget_ticket']
st.divider()
st.markdown(f"### 💰 总预算：¥ {total:,.0f}")
st.caption(f"创建于：{p['created_at']}")