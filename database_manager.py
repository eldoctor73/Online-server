import os
import json
import asyncpg

DB_URL = os.environ.get("DATABASE_URL")

_pool: asyncpg.Pool | None = None

async def init_db():
    global _pool
    if not DB_URL:
        raise RuntimeError("DATABASE_URL is not set")

    if _pool is None:
        _pool = await asyncpg.create_pool(
            DB_URL,
            min_size=10,
            max_size=50,
            command_timeout=60
        )

def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized yet")
    return _pool

# ======================
# اتصال بقاعدة البيانات
# ======================
# async def get_connection():
#     if not DB_URL:
#         raise RuntimeError("DATABASE_URL is not set")
#     return await asyncpg.connect(DB_URL)

async def start(action, player_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                player_id = int(player_id)
                row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1', player_id)
                if not row:
                    response = {"error": "player not found"}
                    return response

                data_player = row["data_player"]
                if isinstance(data_player, str):
                    data_player = json.loads(data_player)

                response = {

                        "Name": data_player.get("Name"),
                        "Type": data_player.get("Type"),
                        "HP": data_player.get("HP"),
                        "points": data_player.get("points", 0),
                        "items_count": data_player.get("items_count", 0),
                        "locationX": data_player.get("locationX"),
                        "locationY": data_player.get("locationY"),
                        "map": data_player.get("map"),
                    }

                return response

            except Exception as e:
                response = {"Error": str(e)}
                return response


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
                    response= {"Error": "player not found"}
                    return response

                data_player = json.loads(row["data_player"])
                points = data_player.get("points")
                items_count = data_player.get("items_count")
                data_player["points"] = points + points_to_add

                await conn.execute(
                    'UPDATE users SET data_player=$1 WHERE id_players=$2',
                    json.dumps(data_player), player_id
                )

                response = {"new_points": data_player["points"],
                            "items_count": data_player["items_count"],
                            "Action":action
                            }
                return response

            except Exception as e:
                response = {"Error":str(e)}
                return response

# ======================
# شراء عنصر من نقاط اللاعب
# ======================
async def buy_item(action, player_id: str, item_price):
    async with pool.acquire() as conn:
        async with conn.transaction():
            try:
                player_id = int(player_id)
                row = await conn.fetchrow(
                    'SELECT data_player FROM users WHERE id_players=$1 FOR UPDATE',
                    player_id
                )
                if not row:
                    response = {"Error": "player not found"}
                    return response

                data_player = json.loads(row["data_player"])
                points = data_player.get("points")
                items_count = data_player.get("items_count")

                if points < item_price:
                    response ={"items_count": data_player["items_count"],
                        "new_points": data_player["points"],
                        "anim_no_money": "play",
                        "3ard_sha7n": "open",
                               "Action": action }
                    return response

                # العملية الأساسية
                data_player["points"] = points - item_price
                data_player["items_count"] = items_count + 1

                await conn.execute(
                    'UPDATE users SET data_player=$1 WHERE id_players=$2',
                    json.dumps(data_player), player_id
                )

                response = {
                    "new_points": data_player["points"],
                    "items_count": data_player["items_count"],
                "Action":action}
                return response

            except Exception as e:
                response ={"Error":str(e)}
                return response

# ======================
# تجربة الاتصال والرد
# ======================
async def testmyself(action, player_id):
    return {
        "msg": f"Hello {player_id}"
    }





