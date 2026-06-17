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
        seen_titles = set()
        exclude_keywords = ["ข่าวสารวงการเหล็ก", "ข่าวประชาสัมพันธ์", "หน้าแรก", "เกี่ยวกับเรา", "ติดต่อเรา", "เพิ่มเติม"]

        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                if title in seen_titles or any(keyword in title for keyword in exclude_keywords):
                    continue
                    
                seen_titles.add(title)
                full_url = clean_url(href)
                
                date_str = "10.06.2026"  # กำหนดค่าเริ่มต้น หรือตัดจากข้อความถ้ามี
                display_title = title
                if len(title) >= 10 and title[2] == '.' and title[5] == '.':
                    date_str = title[:10]
                    display_title = title[10:].strip()

                # บล็อกแสดงรายการข่าวสารแต่ละช่องแบบมินิมอลตามแบบ
                news_html_list += f"""
                <div class="news-item-box">
                    <div class="news-img-placeholder">📰</div>
                    <div class="news-date-tag">{date_str}</div>
                    <a href="{full_url}" target="_blank" class="news-item-title">{display_title}</a>
                </div>
                """
                if len(seen_titles) >= 3:  # ดึงมาโชว์ 3 ข่าวเด่นตาม Layout หน้าแรก
                    break

        # โครงสร้างหน้าตาเว็บเลียนแบบดีไซน์ภาพที่ 2 (โทนน้ำตาล-เทา)
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย (จำลอง)</title>
                <style>
                    body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; color: #4a4a4a; }}
                    
                    /* แถบหัวเว็บสีขาว-น้ำตาล */
                    .top-logo-bar {{ background: white; padding: 15px 10%; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e0e0e0; }}
                    .logo-title-group {{ display: flex; align-items: center; gap: 15px; }}
                    .logo-box {{ width: 45px; height: 45px; background: #4a2825; border-radius: 8px; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 20px; }}
                    .logo-text h2 {{ margin: 0; font-size: 16px; color: #4a2825; }}
                    .logo-text p {{ margin: 0; font-size: 11px; color: #7a7a7a; font-weight: bold; }}
                    
                    /* เมนูนำทาง */
                    .nav-bar {{ background: #f7f7f7; padding: 10px 10%; text-align: right; border-bottom: 2px solid #4a2825; font-size: 13px; font-weight: bold; }}
                    .nav-bar a {{ color: #666; text-decoration: none; margin-left: 20px; }}
                    .nav-bar a.active {{ color: #4a2825; }}

                    /* พื้นที่หลักตรงกลางแบ่งเป็น 2 ฝั่ง (Grid) */
                    .main-wrapper {{ max-width: 1200px; margin: 25px auto; padding: 0 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }}
                    
                    /* ฝั่งซ้าย: แบนเนอร์จำลอง */
                    .banner-slider-mock {{ background: linear-gradient(135deg, #5c5c5c 0%, #3a3a3a 100%); color: white; border-radius: 4px; padding: 40px; position: relative; min-height: 220px; display: flex; flex-direction: column; justify-content: center; }}
                    .banner-slider-mock h2 {{ margin: 0 0 10px 0; font-size: 24px; }}
                    .banner-slider-mock p {{ margin: 0; opacity: 0.8; font-size: 14px; }}
                    .qr-mock {{ position: absolute; right: 40px; top: 50%; transform: translateY(-50%); width: 100px; height: 100px; background: white; border-radius: 4px; padding: 10px; display: flex; align-items: center; justify-content: center; color: #333; font-weight: bold; font-size: 12px; text-align: center; }}

                    /* ฝั่งขวา: กล่องเตือนภัยสีน้ำตาล */
                    .right-panel-box {{ background: white; border-radius: 4px; padding: 20px; border-top: 4px solid #4a2825; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                    .panel-header-title {{ font-size: 14px; font-weight: bold; color: #4a2825; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
                    .alert-btn-item {{ background: #9d8781; color: white; padding: 12px; margin-bottom: 10px; border-radius: 4px; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
                    .alert-btn-item:hover {{ background: #86716b; }}

                    /* ส่วนเนื้อหาข่าวสารด้านล่าง */
                    .section-news-container {{ grid-column: span 2; background: white; padding: 25px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
                    .section-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #4a2825; padding-bottom: 8px; margin-bottom: 20px; }}
                    .section-header h3 {{ margin: 0; color: #4a2825; font-size: 18px; }}
                    .section-header a {{ color: #888; text-decoration: none; font-size: 12px; font-weight: bold; }}
                    
                    /* รายการข่าวเรียงแบบ 3 คอลัมน์ */
                    .news-grid-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
                    .news-item-box {{ background: #fafafa; border: 1px solid #e0e0e0; padding: 15px; border-radius: 4px; display: flex; flex-direction: column; gap: 8px; }}
                    .news-img-placeholder {{ width: 100%; height: 130px; background: #e0e0e0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 32px; color: #999; }}
                    .news-date-tag {{ font-size: 11px; color: white; background: #4a2825; padding: 2px 6px; border-radius: 3px; align-self: flex-start; font-weight: bold; margin-top: 5px; }}
                    .news-item-title {{ text-decoration: none; color: #333; font-size: 13px; font-weight: bold; line-height: 1.4; height: 55px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }}
                    .news-item-title:hover {{ color: #4a2825; }}

                    .footer {{ text-align: center; margin-top: 40px; padding: 20px; background: #e0e0e0; font-size: 11px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="top-logo-bar">
                    <div class="logo-title-group">
                        <div class="logo-box">✦</div>
                        <div class="logo-text">
                            <h2>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</h2>
                            <p>IRON & STEEL INTELLIGENCE UNIT</p>
                        </div>
                    </div>
                </div>
                
                <div class="nav-bar">
                    <a href="#" class="active">หน้าหลัก</a>
                    <a href="#">เกี่ยวกับเรา</a>
                    <a href="#">ข่าวสาร</a>
                    <a href="#">วารสารและรายงาน</a>
                    <a href="#">ข้อมูลสถิติ</a>
                </div>

                <div class="main-wrapper">
                    <div class="banner-slider-mock">
                        <h2>ขอเรียนเชิญร่วมประเมิน</h2>
                        <p>แบบสอบถามความพึงพอใจการใช้บริการศูนย์สารสนเทศอัจฉริยะ</p>
                        <div class="qr-mock">SCAN QR CODE</div>
                    </div>

                    <div class="right-panel-box">
                        <div class="panel-header-title">เตือนภัยอุตสาหกรรมเหล็ก มิถุนายน 2569</div>
                        <div class="alert-btn-item">🚨 อุดสาหกรรมเหล็กกระแสสั้น ➔</div>
                        <div class="alert-btn-item">🚨 อุดสาหกรรมเหล็กกระแสยาว ➔</div>
                    </div>

                    <div class="section-news-container">
                        <div class="section-header">
                            <h3>📰 ข่าวสารล่าสุด</h3>
                            <a href="{TARGET_URL}" target="_blank">เพิ่มเติม ➔</a>
                        </div>
                        <div class="news-grid-row">
                            {news_html_list if news_html_list else "<p>ไม่พบข้อมูลข่าวสารในขณะนี้</p>"}
                        </div>
                    </div>
                </div>

                <div class="footer">
                    ระบบดึงข้อมูลจำลองหน้าตาเว็บอัตโนมัติจากหน้าหลัก IIU ISIT | พัฒนาด้วย FastAPI & Render สายฟรี
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return HTMLResponse(content=f"<div style='padding:50px; text-align:center;'><h3>เกิดข้อผิดพลาด: {str(e)}</h3></div>", status_code=500)

@app.get("/api/news")
def get_latest_news():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        seen_titles = set()
        exclude_keywords = ["ข่าวสารวงการเหล็ก", "ข่าวประชาสัมพันธ์", "หน้าแรก", "เกี่ยวกับเรา", "ติดต่อเรา", "เพิ่มเติม"]
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                if title in seen_titles or any(keyword in title for keyword in exclude_keywords):
                    continue
                seen_titles.add(title)
                full_url = clean_url(href)
                news_list.append({"title": title, "url": full_url})
        
        return {"status": "success", "count": len(news_list[:3]), "data": news_list[:3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))