from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU News API")

TARGET_URL = "https://iiu.isit.or.th/th/home.aspx"

def clean_url(href):
    if href.startswith('http'):
        return href
    href_clean = href.lstrip('/')
    if href_clean.startswith('th/'):
        return f"https://iiu.isit.or.th/{href_clean}"
    else:
        return f"https://iiu.isit.or.th/th/{href_clean}"

@app.get("/", response_class=HTMLResponse)
def render_web_page():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_html_list = ""
        seen_titles = set()  # เอาไว้ตรวจสอบและบล็อกหัวข้อซ้ำ
        
        # คำที่เราไม่ต้องการให้หลุดเข้ามาโชว์ในรายการข่าว
        exclude_keywords = ["ข่าวสารวงการเหล็ก", "ข่าวประชาสัมพันธ์", "หน้าแรก", "เกี่ยวกับเรา", "ติดต่อเรา"]

        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            # กรองเงื่อนไข: ต้องเป็นลิงก์ข่าว, ตัวหนังสือยาวพอ, ไม่ซ้ำ, และไม่อยู่ในคำที่สั่งห้าม
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                if title in seen_titles or any(keyword in title for keyword in exclude_keywords):
                    continue
                    
                seen_titles.add(title)
                full_url = clean_url(href)
                
                # ตรรกะแยกวันที่ออกจากหัวข้อข่าว (ถ้ามี) เพื่อความสวยงาม
                date_str = ""
                display_title = title
                if len(title) >= 10 and title[2] == '.' and title[5] == '.':
                    date_str = title[:10]
                    display_title = title[10:].strip()

                # สร้างแถวแสดงผลรายการข่าวแบบ UI ทันสมัย
                news_html_list += f"""
                <div class="news-card">
                    {f'<span class="news-date">📅 {date_str}</span>' if date_str else ''}
                    <a href="{full_url}" target="_blank" class="news-title">
                        {display_title}
                    </a>
                    <a href="{full_url}" target="_blank" class="news-link-btn">อ่านต่อ ➔</a>
                </div>
                """
                
                if len(seen_titles) >= 10: # ดึงมาโชว์สูงสุด 10 ข่าวล่าสุด
                    break

        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ISIT IIU News Feed</title>
                <style>
                    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f7fb; color: #333; }}
                    .header {{ background: linear-gradient(135deg, #0f2b46 0%, #1a4a75 100%); color: white; padding: 40px 20px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                    .header h1 {{ margin: 0; font-size: 26px; font-weight: 600; letter-spacing: 0.5px; }}
                    .header p {{ margin: 10px 0 0 0; opacity: 0.8; font-size: 14px; }}
                    .container {{ max-width: 900px; margin: 30px auto; padding: 0 20px; }}
                    .feed-title {{ font-size: 18px; color: #4a5568; margin-bottom: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; }}
                    .news-card {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); border-left: 4px solid #328cc1; display: flex; flex-direction: column; gap: 8px; position: relative; transition: all 0.2s ease; }}
                    .news-card:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
                    .news-date {{ font-size: 13px; color: #e056fd; font-weight: bold; background: #fbecff; padding: 3px 8px; border-radius: 4px; align-self: flex-start; }}
                    .news-title {{ text-decoration: none; color: #2d3748; font-size: 16px; font-weight: bold; line-height: 1.5; padding-right: 70px; }}
                    .news-card:hover .news-title {{ color: #328cc1; }}
                    .news-link-btn {{ position: absolute; right: 20px; bottom: 20px; text-decoration: none; color: #328cc1; font-size: 14px; font-weight: bold; }}
                    .footer {{ margin-top: 40px; padding: 20px; font-size: 12px; color: #a0aec0; text-align: center; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🌐 ข่าวสารล่าสุด สถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย</h1>
                    <p>ระบบเชื่อมโยงข้อมูลข่าวสารอัตโนมัติผ่านกลุ่มงานความร่วมมือและพัฒนาอุตสาหกรรม (IIU)</p>
                </div>
                <div class="container">
                    <div class="feed-title">📰 รายการอัปเดตล่าสุด</div>
                    {news_html_list if news_html_list else '<div class="news-card"><p>❌ ไม่พบข้อมูลข่าวสารในขณะนี้</p></div>'}
                </div>
                <div class="footer">
                    แหล่งข้อมูลดิบ: <a href="{TARGET_URL}" target="_blank" style="color: #a0aec0;">{TARGET_URL}</a> | พัฒนาด้วย FastAPI & Render
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return HTMLResponse(content=f"<div style='padding:50px; text-align:center;'><h3>เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}</h3></div>", status_code=500)

@app.get("/api/news")
def get_latest_news():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        seen_titles = set()
        exclude_keywords = ["ข่าวสารวงการเหล็ก", "ข่าวประชาสัมพันธ์", "หน้าแรก", "เกี่ยวกับเรา", "ติดต่อเรา"]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                if title in seen_titles or any(keyword in title for keyword in exclude_keywords):
                    continue
                seen_titles.add(title)
                full_url = clean_url(href)
                news_list.append({"title": title, "url": full_url})
        
        return {"status": "success", "count": len(news_list[:10]), "data": news_list[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))