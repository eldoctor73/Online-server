import json
from database_manager import get_pool


async def get_player_data(player_id):
    # 1. تأكد إن الـ ID مش فاضي
    if not player_id:
        return {"Status": "Error", "Message": "Player ID is empty from Unreal"}

    pool = get_pool()
    try:
        async with pool.acquire() as conn:
            # 2. تحويل آمن للـ ID
            p_id_int = int(player_id)

            row = await conn.fetchrow('SELECT data_player, inv FROM users WHERE id_players=$1', p_id_int)

            if row:
                data_player = json.loads(row['data_player'])
                hp = int(data_player.get("HP", "100"))/ 1000
                return {
                    "Status": "Success",
                    "points": str(data_player.get("points", "0")),
                    "HP": str(hp),
                    "items_count": str(data_player.get("items_count", "0"))
                }
            else:
                return {"Status": "Error", "Message": f"Player {player_id} not found in DB"}

    except Exception as e:
        # لو حصل أي غلطة، السيرفر هيرجعلك نص الغلطة بدل 500
        return {"Status": "Error", "Message": str(e)}