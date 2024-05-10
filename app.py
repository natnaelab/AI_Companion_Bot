from fastapi import FastAPI, Request, Response
from telegram import Update
from bot import bot_app
import uvicorn
import asyncio
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()

SITE_URL = os.getenv("SITE_URL")


@app.post("/telegram")
async def telegram(request: Request):
    await bot_app.update_queue.put(
        Update.de_json(data=await request.json(), bot=bot_app.bot)
    )

    return Response()


async def main():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)

    await bot_app.bot.set_webhook(f"{SITE_URL}/telegram")

    async with bot_app:
        await bot_app.start()
        await server.serve()
        await bot_app.stop()


if __name__ == "__main__":
    asyncio.run(main())
