from database import get_pool
import json


async def start(action, player_id: str):
    pool = pool()
    async with pool.acquire() as conn:
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

