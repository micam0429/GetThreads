import os
import json
from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/scrape")
async def scrape_threads(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        )
        
        # 建立一個設定了 User-Agent 的 Context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        # 如果 Render 有設定 THREADS_COOKIES，就把它們注入進去
        cookies_env = os.getenv("THREADS_COOKIES")
        if cookies_env:
            try:
                cookies = json.loads(cookies_env)
                await context.add_cookies(cookies)
            except Exception as e:
                print(f"Failed to load cookies: {e}")

        page = await context.new_page()
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(4000)
            
            content = await page.inner_text("body")
            return {"status": "success", "url": url, "content": content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await browser.close()
