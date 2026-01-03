import os
import json
import asyncpg

DB_URL = os.environ.get("DATABASE_URL")
pool: asyncpg.Pool | None = None
async def init_db():
    global pool
    if not DB_URL:
        raise RuntimeError("DATABASE_URL is not set")

    pool = await asyncpg.create_pool(
        DB_URL,
        min_size=10,
        max_size=50,
        command_timeout=60
    )
# ======================
# اتصال بقاعدة البيانات
# ======================
# async def get_connection():
#     if not DB_URL:
#         raise RuntimeError("DATABASE_URL is not set")
#     return await asyncpg.connect(DB_URL)


# ======================
# إضافة نقاط للاعب
# ======================
async def add_points(action, player_id: str, points_to_add: int):
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                player_id = int(player_id)
                row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
                if not row:
                    response= {"result": "player not found"}
                    return response

                data_player = json.loads(row["data_player"])
                points = data_player.get("points", 0)

                data_player["points"] = points + points_to_add

                await conn.execute(
                    'UPDATE users SET data_player=$1 WHERE id_players=$2',
                    json.dumps(data_player), player_id
                )

                response = {"new_points": data_player["points"]}
                return response

            except Exception as e:
                response = {"Error":str(e)}
                return response

# ======================
# شراء عنصر من نقاط اللاعب
# ======================
async def buy_item(action, player_id: str, item_price: int):
    async with pool.acquire() as conn:
        async with conn.transaction():
            response = {
                "status": "success",
                "action": action,
                "player_id": player_id,
                "data": {},
                "error": None
            }
            try:
                player_id = int(player_id)
                row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
                if not row:
                    response["status"] = "error"
                    response["error"] = "player not found"
                    return response

                data_player = json.loads(row["data_player"])
                points = data_player.get("points", 0)
                items_count = data_player.get("items_count", 0)

                if points < item_price:
                    response["status"] = "error"
                    response["error"] = "Not enough points"
                    response["data"] = {
                        "new_points": points,
                        "items_count": items_count,
                        "anim_no_money": "play",
                        "3ard_sha7n": "open"
                    }
                    return response

                # العملية الأساسية
                data_player["points"] = points - item_price
                data_player["items_count"] = items_count + 1

                await conn.execute(
                    'UPDATE users SET data_player=$1 WHERE id_players=$2',
                    json.dumps(data_player), player_id
                )

                response["data"] = {
                    "new_points": data_player["points"],
                    "items_count": data_player["items_count"]
                }
                return response

            except Exception as e:
                response["status"] = "error"
                response["error"] = str(e)
                return response

# ======================
# تجربة الاتصال والرد
# ======================
async def testmyself(action, player_id):
    return {
        "status": "success",
        "action": action,
        "player_id": player_id,
        "data": {"msg": f"Hello {player_id}"},
        "error": None
    }



