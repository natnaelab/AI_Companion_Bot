from io import BytesIO
import os
import httpx

# cloudflare
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")


async def llama2_7b_chat_fp16(prompt):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-2-7b-chat-fp16",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are a friendly assistant"},
                    {"role": "user", "content": prompt},
                ]
            },
        )

        if response.status_code != 200:
            message = (
                response.json().get("messages")[0]
                if response.json().get("messages")
                else "Something went wrong..."
            )
            raise Exception(message)

        result = response.json()
    return result


async def dreamshaper_8_lcm(prompt):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/lykon/dreamshaper-8-lcm",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt},
        )

        if response.status_code != 200:
            message = (
                response.json().get("messages")[0]
                if response.json().get("messages")
                else "Something went wrong..."
            )
            raise Exception(message)

        return BytesIO(response.content)


async def whisper(audio):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/openai/whisper",
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/octet-stream",
            },
            data=audio.read(),
        )

        if response.status_code != 200:
            raise Exception("Something went wrong")

        return response.json()["result"]["text"]
