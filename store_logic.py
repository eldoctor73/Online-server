import json
from database_manager import get_pool


async def secure_buy(player_id: str, item_id: int):  # هنبعت الـ ID بتاع الايتم
    pool = get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():
            # 1. نجيب بيانات الايتم من جدول الـ items
            item_row = await conn.fetchrow('SELECT item_data FROM items WHERE id=$1', item_id)
            if not item_row:
                return {"Status": "Error", "Message": "Item not found in store"}

            item_info = json.loads(item_row['item_data'])
            item_price = item_info.get('price', 0)
            item_name = item_info.get('name', 'Unknown')

            # 2. نجيب بيانات اللاعب
            player_row = await conn.fetchrow('SELECT data_player FROM users WHERE id_players=$1 FOR UPDATE',
                                             int(player_id))
            if not player_row:
                return {"Status": "Error", "Message": "Player not found"}

            player_data = json.loads(player_row['data_player'])
            current_points = player_data.get('points', 0)

            # 3. التأكد من الرصيد
            if current_points < item_price:
                return {"Status": "Failed", "Message": "No enough points", "Needed": item_price}

            # 4. الخصم
            player_data['points'] = current_points - item_price

            # 5. حفظ التعديل في جدول الـ users
            await conn.execute('UPDATE users SET data_player=$1 WHERE id_players=$2',
                               json.dumps(player_data), int(player_id))

            return {
                "Status": "Success",
                "NewPoints": player_data['points'],
                "BoughtItem": item_name
            }