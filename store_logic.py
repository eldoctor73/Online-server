import os
import json
from fastapi import FastAPI, WebSocket
from database_manager import buy_item, add_points, testmyself, init_db#, start
from start import start

app = FastAPI()

# ==========================
# Init DB Pool on startup
# ==========================
@app.on_event("startup")
async def startup_event():
    await init_db()
    print("Database pool initialized")

# ==========================
# WebSocket endpoint
# ==========================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    async for message in websocket.iter_text():
        print(f"[WebSocket] Received message: {message}")

        # Parse JSON
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            await websocket.send_text(json.dumps({
                "status": "error",
                "action": None,
                "player_id": None,
                "data": {},
                "error": "invalid json"
            }))
            continue

        action = data.get("Action")
        player_id = data.get("player_id")
        print(f"[WebSocket] Action: {action}, Player: {player_id}")



        try:
            if action == "BuyItem":
                item_price = int(data.get("item_price", 0))
                response = await buy_item(action, player_id, item_price)

            elif action == "Buypoint":
                points = int(data.get("points", 0))
                response = await add_points(action, player_id, points)

            elif action == "start":
                response = await start(action, player_id)

            elif action == "t3arof":
                response = await testmyself(action, player_id)

        except Exception as e:
            # لو حصل أي استثناء داخلي
            response = {"Error": str(e)}

        # Send response
        await websocket.send_text(json.dumps(response))


# ==========================
# تشغيل السيرفر
# ==========================
if __name__ == "__main__":
    import uvicorn
    import asyncio

    port = int(os.environ.get("PORT", 8080))
    print(f"Starting server on 0.0.0.0:{port}")

    # ⚡ جهّز الـ pool قبل أي request
    asyncio.run(init_db())
    print("Database pool fully initialized before server starts")

    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info", reload=False)

