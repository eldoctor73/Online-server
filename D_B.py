import asyncpg
import os

DB_URL = os.environ["DATABASE_URL"]

async def get_connection():
    return await asyncpg.connect(DB_URL)

# عملية شراء عنصر
async def buy_item(action, player_id: str, character_name: str, item_name: str, item_price: int):
    conn = await get_connection()

    # جلب بيانات اللاعب
    row = await conn.fetchrow("SELECT points FROM users WHERE player_id=$1", player_id)
    if not row:
        await conn.close()
        return {"status": "error", "reason": "player not found"}

    current_points = row["points"]

    if current_points < item_price:
        await conn.close()
        return {"status": "error", "reason": "points not enough"}

    # خصم النقاط
    new_points = current_points - item_price
    await conn.execute("UPDATE users SET points=$1 WHERE player_id=$2", new_points, player_id)

    # هنا ممكن تضيف كود لتحديث الانفنتوري للـ character_name بالـ item_name
    await conn.close()

    return {"Actions": action, "new_points": new_points, "item_bought": item_name, "character": character_name}

# عملية إضافة نقاط (مثال على Buy points)
async def add_points(action, player_id: str, points_to_add: int):
    conn = await get_connection()
    row = await conn.fetchrow("SELECT points FROM users WHERE player_id=$1", player_id)
    if not row:
        await conn.close()
        return {"status": "error", "reason": "player not found"}

    new_points = row["points"] + points_to_add
    await conn.execute("UPDATE users SET points=$1 WHERE player_id=$2", new_points, player_id)
    await conn.close()
    return {"Actions": action, "new_points": new_points}

async def testmyself(action, player_id):
    conn = await get_connection()
    strings = f"hello {player_id}"
    await conn.close()
    return {"Actions":action, "msg":strings}
