from fastapi import FastAPI, WebSocket
import json
from Data_Base import buy_item, add_points, testmyself

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    async for message in websocket.iter_text():
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({"status": "error", "reason": "invalid json"}))
            continue

        action = data.get("Action")
        player_id = data.get("player_id")

        if action == "BuyItem":
            character_name = data.get("character_name")
            item_name = data.get("item_name")
            item_price = int(data.get("item_price", "0"))
            response = await buy_item(action, player_id, character_name, item_name, item_price)
            await websocket.send_text(json.dumps(response))

        elif action == "AddPoints":
            points = int(data.get("points", "0"))
            response = await add_points(action, player_id, points)
            await websocket.send_text(json.dumps(response))

        elif action == "t3arof":
            response = await testmyself(action, player_id)
            await websocket.send_text(json.dumps(response))
        else:
            await websocket.send_text(json.dumps({"status": "error", "reason": "unknown action"}))


# ==========================
# تشغيل السيرفر
# ==========================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))  # الحصول على البورت من البيئة أو 8080

    # تشغيل Uvicorn بشكل مباشر
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
