from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse  # เพิ่มตัวส่งกลับเป็นหน้าเว็บ HTML
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU News API")

TARGET_URL = "https://iiu.isit.or.th/th/home.aspx"

# 1. เปลี่ยนเส้นทางหลัก (/) ให้พ่นหน้าตาเว็บไซต์ออกมาโชว์
@app.get("/", response_class=HTMLResponse)
def render_web_page():
    try:
        # ไปดึงข้อมูลข่าวมาก่อนด้วยตรรกะเดิม
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_html_list = ""
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                full_url = f"https://iiu.isit.or.th/th/{href}" if not href.startswith('http') else href
                # ประกอบร่างให้เป็นแท็กลิงก์ HTML สำหรับโชว์บนหน้าเว็บ
                news_html_list += f'<li><a href="{full_url}" target="_blank">{title}</a></li>'

        # เขียนโครงสร้างหน้าเว็บแบบง่ายๆ (มี CSS ตกแต่งนิดหน่อยให้ดูสบายตา)
        html_content = f"""
        <html>
            <head>
                <title>ISIT IIU News Feed</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f6f9; }}
                    .container {{ max-width: 800px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    h1 {{ color: #0275d8; border-bottom: 2px solid #0275d8; padding-bottom: 10px; }}
                    ul {{ list-style-type: none; padding: 0; }}
                    li {{ padding: 12px; border-bottom: 1px solid #eee; transition: 0.2s; }}
                    li:hover {{ background-color: #f8f9fa; }}
                    a {{ text-decoration: none; color: #333; font-size: 16px; font-weight: 500; }}
                    a:hover {{ color: #0275d8; }}
                    .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📰 ข่าวสารล่าสุด สถาบันเหล็กและเหล็กกล้าฯ</h1>
                    <ul>
                        {news_html_list if news_html_list else "<li>ไม่มีข้อมูลข่าวสารในขณะนี้</li>"}
                    </ul>
                    <div class="footer">ดึงข้อมูลอัตโนมัติจาก: {TARGET_URL}</div>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return HTMLResponse(content=f"<h3>เกิดข้อผิดพลาด: {str(e)}</h3>", status_code=500)

# 2. เก็บเส้นทางดึงข้อความดิบไว้เหมือนเดิม เผื่อเอาไปต่อกับระบบอื่น (/api/news)
@app.get("/api/news")
def get_latest_news():
    # ... (โค้ดดึง JSON ชุดเดิมของคุณ) ...
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                full_url = f"https://iiu.isit.or.th/th/{href}" if not href.startswith('http') else href
                news_item = {"title": title, "url": full_url}
                if news_item not in news_list: news_list.append(news_item)
        return {"status": "success", "data": news_list[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))