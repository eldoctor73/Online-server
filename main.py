import os
import json
from fastapi import FastAPI, WebSocket
from database import buy_item, add_points, testmyself

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    async for message in websocket.iter_text():
        print(f"[WebSocket] Received message: {message}")
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({"status": "error", "reason": "invalid json"}))
            continue

        action = data.get("Action")
        player_id = data.get("player_id")
        print(f"[WebSocket] Action: {action}, Player: {player_id}")

        try:
            if action == "BuyItem":
                character_name = data.get("character_name")
                item_name = data.get("item_name")
                item_price = int(data.get("item_price"))
                response = await buy_item(action, player_id, item_price)

            elif action == "Buypoint":
                points = int(data.get("points", "0"))
                response = await add_points(action, player_id, points)

            elif action == "t3arof":
                response = await testmyself(action, player_id)

            else:
                response = {"status": "error", "reason": "unknown action"}

        except Exception as e:
            print(f"[WebSocket] Exception: {e}")
            response = {"status": "error", "reason": str(e)}

        await websocket.send_text(json.dumps(response))



# ==========================
# تشغيل السيرفر
# ==========================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on 0.0.0.0:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=False)
