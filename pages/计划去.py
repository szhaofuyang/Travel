import streamlit as st
from streamlit_folium import st_folium
from utils.db import get_all_places, add_place
from utils.map_utils import generate_map, geocode_city
from utils.theme_utils import get_theme_css
from datetime import date

st.set_page_config(page_title="计划去", page_icon="📌", layout="wide")
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

st.markdown('<h1>📌 计划去</h1>', unsafe_allow_html=True)
st.markdown('在这里添加你未来想去的地方，并规划预算。')

with st.expander("➕ 添加新计划", expanded=False):
    with st.form("add_plan_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("目的地名称 *", placeholder="例如：东京")
            city = st.text_input("城市 *", placeholder="例如：东京")
            start_date = st.date_input("开始日期", value=date.today())
            end_date = st.date_input("结束日期", value=date.today())
        with col2:
            budget_food = st.number_input("🍜 餐饮预算 (¥)", min_value=0.0, step=50.0, value=0.0)
            budget_accommodation = st.number_input("🏨 住宿预算 (¥)", min_value=0.0, step=50.0, value=0.0)
            budget_transport_big = st.number_input("🚆 大交通预算 (¥)", min_value=0.0, step=50.0, value=0.0)
            budget_transport_small = st.number_input("🚌 小交通预算 (¥)", min_value=0.0, step=50.0, value=0.0)
            budget_ticket = st.number_input("🎟️ 门票预算 (¥)", min_value=0.0, step=50.0, value=0.0)
        notes = st.text_area("备注", placeholder="旅行小贴士或特殊需求")
        submitted = st.form_submit_button("💾 保存计划")

        if submitted:
            if not name.strip() or not city.strip():
                st.error("请填写目的地名称和城市")
            else:
                lat, lng = geocode_city(city)
                if lat is None or lng is None:
                    st.warning(f"无法获取「{city}」的坐标，将使用默认值 (0,0)。可稍后手动编辑。")
                    lat, lng = 0.0, 0.0
                data = {
                    'name': name.strip(),
                    'city': city.strip(),
                    'lat': lat,
                    'lng': lng,
                    'status': 'plan',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'budget_food': budget_food,
                    'budget_accommodation': budget_accommodation,
                    'budget_transport_big': budget_transport_big,
                    'budget_transport_small': budget_transport_small,
                    'budget_ticket': budget_ticket,
                    'notes': notes
                }
                pid = add_place(user_id, data)
                st.success(f"✅ 已添加计划：{name} (ID: {pid})")
                st.rerun()

places = get_all_places(user_id, status='plan')
if places:
    # 地图标题改为“计划目的地”，高度 40vh
    st.markdown('<h3>🗺️ 计划目的地</h3>', unsafe_allow_html=True)
    m = generate_map(places, highlight_status='plan')
    st_folium(m, width='100%', height='40vh', returned_objects=[])

    st.divider()
    st.markdown('<h3>📋 计划列表</h3>', unsafe_allow_html=True)
    sorted_places = sorted(places, key=lambda x: x['start_date'] or '')
    for p in sorted_places:
        with st.container():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.markdown(f"""
                    <div class="list-item">
                        <div>
                            <span class="name">{p['name']}</span>
                            <span class="city">📍 {p['city']}</span>
                            <span style="font-size:0.75rem;color:#6e6e73;margin-left:10px;">
                                {p['start_date']} ~ {p['end_date']}
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col_b:
                total = p['budget_food'] + p['budget_accommodation'] + p['budget_transport_big'] + p['budget_transport_small'] + p['budget_ticket']
                st.markdown(f'<span class="budget">¥ {total:,.0f}</span>', unsafe_allow_html=True)
            with col_c:
                if st.button("查看", key=f"view_plan_{p['id']}"):
                    st.query_params['id'] = p['id']
                    st.switch_page("pages/详情.py")
else:
    st.info("还没有计划的目的地，快来添加吧！")