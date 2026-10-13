from fastapi import FastAPI, HTTPException
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running", "message": "Threads Scraper API is active"}

@app.get("/scrape")
async def scrape_threads(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' query parameter.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu",
            ]
        )
        page = await browser.new_page()
        try:
            # 設置模擬 User-Agent 避免被阻擋
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # 前往目標網址
            await page.goto(url, timeout=40000)
            
            # 自動向下滾動頁面以觸發動態載入留言
            for _ in range(2):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(2000)
            
            # 萃取頁面純文字內容
            content = await page.inner_text("body")
            
            return {
                "status": "success",
                "url": url,
                "content": content
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await browser.close()