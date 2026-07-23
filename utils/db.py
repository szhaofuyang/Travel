import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ... 其余函数
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ... 其余函数保持不变

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("请设置环境变量 SUPABASE_URL 和 SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- 初始化（表已在 Supabase 中手动创建，此函数留空） ----------
def init_db():
    """表结构已在 Supabase 控制台创建，此处无需操作"""
    pass

# ---------- 用户相关 ----------
def create_user(username, password):
    """
    注册用户，返回用户 id，若用户名已存在返回 None
    注：密码明文存储（演示），生产应哈希
    """
    try:
        # 检查用户名是否已存在
        existing = supabase.table("users").select("id").eq("username", username).execute()
        if existing.data:
            return None
        # 插入新用户
        result = supabase.table("users").insert({
            "username": username,
            "password": password
        }).execute()
        return result.data[0]['id']
    except Exception as e:
        print("注册错误:", e)
        return None

def get_user(username, password):
    """验证登录，返回用户字典或 None"""
    try:
        result = supabase.table("users").select("*") \
            .eq("username", username) \
            .eq("password", password) \
            .execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print("登录错误:", e)
        return None

# ---------- 地点 CRUD（所有操作带 user_id 过滤） ----------
def add_place(user_id, data):
    """插入新地点，返回新记录 id"""
    record = {
        "user_id": user_id,
        "name": data['name'],
        "city": data['city'],
        "lat": data['lat'],
        "lng": data['lng'],
        "status": data['status'],
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "budget_food": data['budget_food'],
        "budget_accommodation": data['budget_accommodation'],
        "budget_transport_big": data['budget_transport_big'],
        "budget_transport_small": data['budget_transport_small'],
        "budget_ticket": data['budget_ticket'],
        "notes": data['notes']
    }
    result = supabase.table("places").insert(record).execute()
    return result.data[0]['id']

def get_all_places(user_id, status=None):
    """获取当前用户所有地点，可选状态过滤，按 start_date 和 created_at 排序"""
    query = supabase.table("places").select("*").eq("user_id", user_id)
    if status:
        query = query.eq("status", status)
    query = query.order("start_date", desc=False).order("created_at", desc=False)
    result = query.execute()
    return result.data  # 返回列表字典

def get_place_by_id(user_id, pid):
    """根据 id 和 user_id 获取单个地点，返回字典或 None"""
    result = supabase.table("places").select("*") \
        .eq("id", pid) \
        .eq("user_id", user_id) \
        .execute()
    if result.data:
        return result.data[0]
    return None

def update_place(user_id, pid, data):
    """更新地点，同时校验 user_id 确保安全"""
    update_data = {
        "name": data['name'],
        "city": data['city'],
        "lat": data['lat'],
        "lng": data['lng'],
        "status": data['status'],
        "start_date": data['start_date'],
        "end_date": data['end_date'],
        "budget_food": data['budget_food'],
        "budget_accommodation": data['budget_accommodation'],
        "budget_transport_big": data['budget_transport_big'],
        "budget_transport_small": data['budget_transport_small'],
        "budget_ticket": data['budget_ticket'],
        "notes": data['notes']
    }
    supabase.table("places").update(update_data) \
        .eq("id", pid) \
        .eq("user_id", user_id) \
        .execute()

def delete_place(user_id, pid):
    """删除地点"""
    supabase.table("places").delete() \
        .eq("id", pid) \
        .eq("user_id", user_id) \
        .execute()

def get_total_budget(places):
    """计算总预算，places 为字典列表"""
    total = 0
    for p in places:
        total += (p.get('budget_food', 0) + p.get('budget_accommodation', 0) +
                  p.get('budget_transport_big', 0) + p.get('budget_transport_small', 0) +
                  p.get('budget_ticket', 0))
    return total

# ---------- 坐标缓存（持久化到 Supabase） ----------
def get_cached_coords(city):
    """从缓存表获取坐标，返回 (lat, lng) 或 (None, None)"""
    try:
        result = supabase.table("geo_cache").select("lat, lng").eq("city", city).execute()
        if result.data:
            return result.data[0]['lat'], result.data[0]['lng']
        return None, None
    except Exception:
        return None, None

def save_cached_coords(city, lat, lng):
    """保存或更新缓存"""
    supabase.table("geo_cache").upsert({
        "city": city,
        "lat": lat,
        "lng": lng
    }, on_conflict="city").execute()