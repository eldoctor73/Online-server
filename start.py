import os
import json
import asyncpg

DB_URL = os.environ.get("DATABASE_URL")

# ======================
# اتصال بقاعدة البيانات
# ======================
async def get_connection():
    if not DB_URL:
        raise RuntimeError("DATABASE_URL is not set")
    return await asyncpg.connect(DB_URL)

# ======================
# فانكشن Start Action
# ======================
async def start(action, player_id: str):
    """
    ديه فانكشن بتتعامل مع حدث Start من Unreal
    بتجيب بيانات اللاعب من الداتا بيز وترجعها عشان تملا الويدجيت
    """
    conn = await get_connection()
    try:
        player_id = int(player_id)

        # جلب بيانات اللاعب
        row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
        if not row:
            return {"status": "error", "reason": "player not found"}

        data_player = json.loads(row["data_player"])

        # ممكن تختار هنا أي قيم تحب ترجعها للـ widget
        widget_data = {
            "Name": data_player.get("Name"),
            "Type": data_player.get("Type"),
            "HP": data_player.get("HP"),
            "points": data_player.get("points"),
            "items_count": data_player.get("items_count", 0),
            "locationX": data_player.get("locationX"),
            "locationY": data_player.get("locationY"),
            "map": data_player.get("map")
        }

        return {
            "Actions": action,
            "player_id": player_id,
            "widget_data": widget_data
        }

    finally:
        if 'conn' in locals():
            await conn.close()
