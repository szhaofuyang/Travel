import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from utils.db import get_cached_coords, save_cached_coords

def geocode_city(city_name):
    """根据城市名获取经纬度，优先缓存，否则调用 API"""
    if not city_name:
        return None, None
    key = city_name.strip()
    
    lat, lng = get_cached_coords(key)
    if lat is not None and lng is not None:
        return lat, lng
    
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
    生成中国地图，使用高德地图瓦片（国内访问快）
    中心固定为中国，显示所有城市标记
    """
    center_lat, center_lng = 35.0, 105.0
    zoom_start = 4

    # 使用高德地图标准瓦片（带中文字标注）
    tiles = 'http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'
    attr = '© 高德地图'

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_start,
        tiles=tiles,
        attr=attr,
        control_scale=True,
        min_zoom=3,
        max_zoom=10
    )

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