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
# إضافة نقاط للاعب
# ======================
async def add_points(action, player_id: str, points_to_add: int):
    conn = await get_connection()
    try:
        player_id = int(player_id)

        # جلب بيانات اللاعب
        row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
        if not row:
            return {"status": "error", "reason": "player not found"}

        # تحويل JSON string لـ dict
        data_player = json.loads(row["data_player"])

        # توقف الكود فورًا لو points غير موجودة أو مش int
        if "points" not in data_player:

            data_player["points"] = 0
            await conn.execute(
                'UPDATE users SET data_player=$1 WHERE id_players=$2',
                json.dumps(data_player), player_id
            )

            return {"status": "error", "reason": "'points' key missing in data_player", "data_player": data_player}

        if not isinstance(data_player["points"], int):
            return {
                "status": "error",
                "reason": f"'points' must be int, got {data_player['points']} ({type(data_player['points'])})",
                "data_player": data_player
            }

        # العملية الأساسية
        data_player["points"] += points_to_add
        new_points = data_player["points"]

        # تحديث DB
        await conn.execute(
            'UPDATE users SET data_player=$1 WHERE id_players=$2',
            json.dumps(data_player), player_id
        )

        # جلب كل اللاعبين
        # all_rows = await conn.fetch('SELECT id_players, data_player FROM users')
        # users_list = [{"id_players": r["id_players"], "data_player": r["data_player"]} for r in all_rows]

        # إرسال كل البيانات في رسالة واحدة للـ Unreal
        return {
            "Actions": action,
            "player_id": player_id,
            "new_points": new_points

        }

    finally:
        if 'conn' in locals():
            await conn.close()

# ======================
# شراء عنصر من نقاط اللاعب
# ======================
async def buy_item(action, player_id: str, item_price: int):
    try:
        conn = await get_connection()
        player_id = int(player_id)

        # جلب بيانات اللاعب
        row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
        if not row:
            return {"status": "error", "reason": "player not found"}

        data_player = json.loads(row["data_player"])

        # تحقق من وجود المفتاح points
        if "points" not in data_player:
            return {"status": "error", "reason": "'points' key missing in data_player", "data_player": data_player}

        # تحقق من وجود المفتاح items_count
        if "items_count" not in data_player:
            data_player["items_count"] = 0

        current_points = data_player["points"]
        current_items = data_player["items_count"]

        # تحقق من كفاية النقاط
        if current_points < item_price:

            return {"Actions":action,
                "anim_no_monye": "play",
                    "new_points": data_player["points"],
                    "items_count": data_player["items_count"],
                    "3ard_sha7n": "open"}

        # خصم النقاط وزيادة عدد العناصر
        data_player["points"] = current_points - item_price
        data_player["items_count"] = current_items + 1

        # تحديث DB
        await conn.execute(
            'UPDATE users SET data_player=$1 WHERE id_players=$2',
            json.dumps(data_player), player_id
        )

        # إرجاع النتيجة
        return {
            "Actions": action,
            "player_id": player_id,
            "new_points": data_player["points"],
            "items_count": data_player["items_count"]
        }

    except Exception as e:
        return {"status": "error", "reason": str(e)}

    finally:
        if 'conn' in locals():
            await conn.close()

# ======================
# تجربة الاتصال والرد
# ======================
async def testmyself(action, player_id):
    try:
        conn = await get_connection()
        return {"Actions": action, "msg": f"Hello {player_id}"}
    finally:
        if 'conn' in locals():
            await conn.close()

