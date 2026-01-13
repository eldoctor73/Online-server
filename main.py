import os
import uvicorn
from fastapi import FastAPI
from database_manager import init_db, add_points
import player_logic
import store_logic

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # لو init_db فيها مشكلة، السيرفر كله مش هيقوم وهيدي 502
    try:
        await init_db()
        print("🚀 Database connected!")
    except Exception as e:
        print(f"❌ Database failed: {e}")

@app.post("/player_data")
async def get_player_info(data: dict):
    # اتأكد إنك باعت player_id من انريل جوه الـ JSON
    p_id = data.get("player_id")
    return await player_logic.get_player_data(p_id)


@app.post("/addpoint")
async def addpoints(data: dict):
    # اتأكد إنك باعت player_id من انريل جوه الـ JSON
    p_id = data.get("player_id")
    return await add_points(p_id)

@app.get("/status")
async def status():
    return {"status": "ok"}

if __name__ == "__main__":
    # التعديل هنا: شلنا "main:app" وخليناها app علطول
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)