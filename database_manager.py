import os
import json
import asyncpg

DB_URL = os.environ.get("DATABASE_URL")
# سيبناها بالأندرسكور زي ما تحب عشان الأمان
_pool = None


async def init_db():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DB_URL, min_size=5, max_size=20)
        print("✅ Pool Initialized")


# دالة ذكية تجيب الـ pool في أي وقت
def get_pool():
    if _pool is None:
        raise RuntimeError("الـ Pool مش شغال يا بطل!")
    return _pool


# ======================
# إضافة نقاط للاعب
# ======================
async def add_points(player_id: str):
    # بدل ما ننادي الـ Variable مباشرة، بننادي الدالة اللي بتجيبه
    pool_to_use = get_pool()

    async with pool_to_use.acquire() as conn:
        try:
            p_id_int = int(player_id)
            row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', p_id_int)

            if not row:
                return {"Status": "Error", "Message": "Player not found"}

            data_player = json.loads(row["data_player"])
            data_player["points"] = data_player.get("points", 0) + 10

            await conn.execute(
                'UPDATE users SET data_player=$1 WHERE id_players=$2',
                json.dumps(data_player), p_id_int
            )

            return {
                "Status": "Success",
                "new_points": str(data_player["points"]),
                "items_count": str(data_player.get("items_count", "0"))
            }
        except Exception as e:
            return {"Status": "Error", "Message": str(e)}