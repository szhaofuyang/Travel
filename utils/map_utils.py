import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from utils.db import get_cached_coords, save_cached_coords

def geocode_city(city_name):
    """根据城市名获取经纬度，优先从缓存读取，否则调用 API"""
    if not city_name:
        return None, None
    key = city_name.strip()
    
    # 查数据库缓存
    lat, lng = get_cached_coords(key)
    if lat is not None and lng is not None:
        return lat, lng
    
    # 调用 Nominatim
    geolocator = Nominatim(user_agent="travel_budget_app")
    try:
        location = geolocator.geocode(key, timeout=5)
        if location:
            lat, lng = location.latitude, location.longitude
            save_cached_coords(key, lat, lng)
            return lat, lng
        return None, None
    except (GeocoderTimedOut, GeocoderUnavailable):
        time.sleep(1)
        try:
            location = geolocator.geocode(key, timeout=5)
            if location:
                lat, lng = location.latitude, location.longitude
                save_cached_coords(key, lat, lng)
                return lat, lng
        except:
            pass
        return None, None

def generate_map(places, highlight_status=None):
    """
    生成中国地图，中心固定为中国，缩放级别为4。
    places: 数据库行列表（包含 lat, lng, status, name, city）
    highlight_status: 如果指定，则只显示该状态的点，否则全部显示
    """
    # 固定中国中心
    center_lat, center_lng = 35.0, 105.0
    zoom_start = 4  # 显示中国全境
    
    # 创建地图
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_start,
        control_scale=True,
        min_zoom=3,
        max_zoom=10  # 限制缩放范围，避免过于放大
    )
    
    # 添加中国地图背景（可选，folium 默认是 OpenStreetMap，已包含中国）
    # 可以添加一个 tile layer 更清晰，但默认可接受
    
    color_map = {'plan': '#007aff', 'visited': '#34c759'}
    
    for p in places:
        lat, lng = p['lat'], p['lng']
        if lat is None or lng is None:
            continue
        status = p['status']
        if highlight_status and status != highlight_status:
            continue
        color = color_map.get(status, '#888888')
        popup_text = f"<b>{p['name']}</b><br>{p['city']}<br>状态: {'计划去' if status=='plan' else '已去'}"
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_text, max_width=200),
            icon=folium.Icon(color=color, icon='circle', prefix='fa'),
            tooltip=p['name']
        ).add_to(m)
    
    return m