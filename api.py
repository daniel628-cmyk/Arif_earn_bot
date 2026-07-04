from fastapi import FastAPI

app = FastAPI(title="Arif Earn Bot API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Arif Earn Bot is running"}