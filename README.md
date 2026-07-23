# 旅游预算轻应用 ✈️

基于 Streamlit + Supabase 构建，支持多用户、计划/已去管理、预算计算、地图点亮，坐标缓存持久化，支持 CSV/PDF 导出，UI 模仿 Apple 风格。

## 功能特色

- 🔐 **多用户系统**：注册/登录，数据完全隔离。
- 📌 **计划去**：添加未来目的地，预算包含吃、住、大交通（高铁/飞机/租车等）、小交通（打车/地铁等）、门票。
- ✅ **已去过**：记录已到访地点，同样支持预算录入。
- 🗺️ **地图点亮**：计划用蓝色，已去用绿色，首页合并显示。
- 📋 **列表展示**：按日期排序，点击查看/修改详情。
- 💾 **数据永久保存**：使用 Supabase 云数据库，重启不丢失。
- 📤 **导出数据**：支持 CSV 和 PDF 报告导出。
- 🎨 **Apple 风格 UI**：圆角卡片、柔和阴影、San Francisco 字体。

## 部署到 Streamlit Cloud（含 Supabase）

### 1. 创建 Supabase 项目

1. 注册 [Supabase](https://supabase.com/) 免费账号。
2. 新建项目，记下 **Project URL**（如 `https://xxxxx.supabase.co`）和 **API Key（anon public）**。
3. 在 Supabase SQL Editor 中执行以下建表 SQL（依次执行）：

```sql
-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 地点表
CREATE TABLE places (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    lat FLOAT,
    lng FLOAT,
    status TEXT CHECK (status IN ('plan', 'visited')) DEFAULT 'plan',
    start_date DATE,
    end_date DATE,
    budget_food FLOAT DEFAULT 0,
    budget_accommodation FLOAT DEFAULT 0,
    budget_transport_big FLOAT DEFAULT 0,
    budget_transport_small FLOAT DEFAULT 0,
    budget_ticket FLOAT DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_places_user ON places(user_id);

-- 坐标缓存表
CREATE TABLE geo_cache (
    city TEXT PRIMARY KEY,
    lat FLOAT,
    lng FLOAT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);