from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU Full Portal API")

BASE_URL = "https://iiu.isit.or.th"
TARGET_URL = f"{BASE_URL}/th/home.aspx"

def clean_url(href):
    if not href:
        return "#"
    if href.startswith('http'):
        return href
    href_clean = href.lstrip('/')
    if href_clean.startswith('th/'):
        return f"{BASE_URL}/{href_clean}"
    else:
        return f"{BASE_URL}/th/{href_clean}"

@app.get("/", response_class=HTMLResponse)
def render_web_page():
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- 1. ดึงภาพแบนเนอร์หลักสไลเดอร์ ---
        # ค้นหาภาพขนาดใหญ่ในหน้าแรก (ส่วนมากจะอยู่ในแท็ก img ที่มีขนาดใหญ่หรือระบุคลาส/ไอดี)
        banner_img = "https://iiu.isit.or.th/images/banner/Banner-IIU-2021.jpg" # Fallback หลัก
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'banner' in src.lower() or 'slide' in src.lower() or 'qr' in src.lower():
                banner_img = clean_url(src)
                break

        # --- 2. ดึงข้อมูลข่าวสารแยกแยะเนื้อหา ---
        news_items = []
        seen_titles = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 15:
                if title in seen_titles or "ข่าวสารวงการเหล็ก" in title or "ข่าวประชาสัมพันธ์" in title:
                    continue
                seen_titles.add(title)
                
                # มองหา tag รูปภาพใกล้เคียงเพื่อดึงมาเป็น Thumbnail (ถ้ามี)
                img_src = ""
                parent = link.find_parent()
                if parent:
                    img_tag = parent.find('img')
                    if img_tag:
                        img_src = clean_url(img_tag.get('src', ''))
                
                date_str = "10.06.2026"
                if title[2] == '.' and title[5] == '.':
                    date_str = title[:10]
                    title = title[10:].strip()
                
                news_items.append({
                    "title": title,
                    "url": clean_url(href),
                    "date": date_str,
                    "img": img_src if img_src else "https://via.placeholder.com/280x150/f0f0f0/666?text=ISIT+IIU"
                })

        # จัดสรรข่าวลง Layout (แบ่งเป็น 3 ข่าวหลักหน้าแรกตามต้นฉบับ)
        news_grid_html = ""
        for item in news_items[:3]:
            news_grid_html += f"""
            <div class="news-block-card">
                <div class="card-img-wrap">
                    <img src="{item['img']}" alt="News Image">
                </div>
                <div class="card-body-content">
                    <span class="card-date-badge">{item['date']}</span>
                    <a href="{item['url']}" target="_blank" class="card-title-link">{item['title']}</a>
                </div>
            </div>
            """

        # --- 3. ดึงโลโก้ผู้สนับสนุนสปอนเซอร์ด้านล่างเซกชัน ---
        sponsor_html = ""
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if any(x in src.lower() for x in ['logo', 'sponsor', 'banner_bottom', 'link']):
                # กรองเอาภาพขนาดเล็กด้านล่างมาทำเป็นตารางสปอนเซอร์
                img_url = clean_url(src)
                if "home" not in src.lower() and "iiu" not in src.lower():
                    sponsor_html += f'<img src="{img_url}" class="sponsor-logo-img" onerror="this.style.display=\'none\'">'

        # --- 4. ประกอบโครงสร้าง HTML & CSS ใกล้เคียงต้นฉบับ ---
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</title>
                <style>
                    body {{ font-family: Tahoma, Geneva, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; color: #333; }}
                    
                    /* Header Zone สีน้ำตาลเข้ม-แดง */
                    .main-header {{ background-color: white; border-bottom: 4px solid #4a2522; padding: 15px 10%; display: flex; justify-content: space-between; align-items: center; }}
                    .brand-container {{ display: flex; align-items: center; gap: 12px; }}
                    .logo-icon-mock {{ width: 40px; height: 40px; background-color: #4a2522; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }}
                    .brand-text h1 {{ margin: 0; font-size: 16px; color: #4a2522; }}
                    .brand-text p {{ margin: 0; font-size: 11px; color: #888; font-weight: bold; }}
                    
                    /* Navigation Bar */
                    .navigation-bar {{ background-color: #eaeaea; padding: 10px 10%; text-align: right; border-bottom: 1px solid #ddd; font-size: 13px; }}
                    .navigation-bar a {{ color: #444; text-decoration: none; margin-left: 20px; font-weight: bold; }}
                    .navigation-bar a:hover, .navigation-bar a.active {{ color: #4a2522; }}

                    /* Main Container Layout */
                    .portal-wrapper {{ max-width: 1200px; margin: 20px auto; padding: 0 15px; display: grid; grid-template-columns: 2.2fr 1fr; gap: 20px; }}
                    
                    /* Banner Left Side */
                    .banner-display-side {{ background-color: white; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
                    .banner-display-side img {{ width: 100%; height: auto; object-fit: cover; }}
                    
                    /* Right Side: Alert Box */
                    .alert-display-side {{ background-color: white; border: 1px solid #ddd; border-radius: 4px; padding: 15px; border-top: 4px solid #4a2522; }}
                    .alert-title {{ font-size: 13px; font-weight: bold; color: #4a2522; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }}
                    .alert-button {{ background-color: #8b736d; color: white; padding: 12px; margin-bottom: 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-decoration: none; display: block; }}
                    .alert-button:hover {{ background-color: #6e5752; }}

                    /* Grid Sections 下方องค์ประกอบ */
                    .content-section-block {{ grid-column: span 2; background-color: white; border: 1px solid #ddd; padding: 20px; border-radius: 4px; }}
                    .section-top-bar {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #4a2522; padding-bottom: 6px; margin-bottom: 15px; }}
                    .section-top-bar h2 {{ margin: 0; font-size: 16px; color: #4a2522; }}
                    .section-top-bar .btn-more {{ font-size: 12px; color: #777; text-decoration: none; font-weight: bold; }}

                    /* Layout รายการข่าว 3 คอลัมน์แบบรูปภาพ */
                    .news-triple-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
                    .news-block-card {{ border: 1px solid #eee; border-radius: 4px; overflow: hidden; background-color: #fafafa; transition: 0.2s; }}
                    .news-block-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
                    .card-img-wrap {{ width: 100%; height: 160px; background-color: #e0e0e0; overflow: hidden; }}
                    .card-img-wrap img {{ width: 100%; height: 100%; object-fit: cover; }}
                    .card-body-content {{ padding: 12px; display: flex; flex-direction: column; gap: 6px; }}
                    .card-date-badge {{ font-size: 11px; color: #888; }}
                    .card-title-link {{ font-size: 13px; font-weight: bold; color: #333; text-decoration: none; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 36px; }}
                    .card-title-link:hover {{ color: #4a2522; }}

                    /* แถบพาร์ทเนอร์โลโก้ด้านล่าง */
                    .sponsors-flex-row {{ grid-column: span 2; background-color: white; border: 1px solid #ddd; padding: 15px; text-align: center; border-radius: 4px; }}
                    .sponsor-logos-wrap {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-top: 10px; }}
                    .sponsor-logo-img {{ height: 45px; width: auto; object-fit: contain; filter: grayscale(20%); transition: 0.2s; }}
                    .sponsor-logo-img:hover {{ filter: grayscale(0%); }}

                    /* Footer */
                    .main-footer {{ background-color: #3b201e; color: #ccc; text-align: center; padding: 15px; font-size: 11px; margin-top: 30px; }}
                </style>
            </head>
            <body>

                <div class="main-header">
                    <div class="brand-container">
                        <div class="logo-icon-mock">⚙️</div>
                        <div class="brand-text">
                            <h1>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</h1>
                            <p>IRON & STEEL INTELLIGENCE UNIT (ISIT IIU)</p>
                        </div>
                    </div>
                </div>

                <div class="navigation-bar">
                    <a href="#" class="active">หน้าหลัก</a>
                    <a href="#">เกี่ยวกับเรา</a>
                    <a href="#">ข่าวสาร</a>
                    <a href="#">วารสารและรายงาน</a>
                    <a href="#">ข้อมูลสถิติ</a>
                </div>

                <div class="portal-wrapper">
                    
                    <div class="banner-display-side">
                        <img src="{banner_img}" alt="ISIT Banner Image">
                    </div>

                    <div class="alert-display-side">
                        <div class="alert-title">📊 เตือนภัยอุตสาหกรรมเหล็ก มิถุนายน 2569</div>
                        <a href="https://iiu.isit.or.th/th/news/Iron%20Industry%20News.aspx" target="_blank" class="alert-button">📄 อุตสาหกรรมเหล็กกระแสบน ➔</a>
                        <a href="https://iiu.isit.or.th/th/news/Press%20Releases%20News.aspx" target="_blank" class="alert-button">📄 อุตสาหกรรมเหล็กกระแสยาว ➔</a>
                    </div>

                    <div class="content-section-block">
                        <div class="section-top-bar">
                            <h2>📰 ข่าวล่าสุด (News)</h2>
                            <a href="{TARGET_URL}" target="_blank" class="btn-more">เพิ่มเติม ➔</a>
                        </div>
                        <div class="news-triple-grid">
                            {news_grid_html if news_grid_html else "<p>กำลังดึงข้อมูลข่าวสารใหม่ล่าสุด...</p>"}
                        </div>
                    </div>

                    <div class="sponsors-flex-row">
                        <div style="font-size: 12px; font-weight: bold; color: #666; text-align: left; border-bottom: 1px solid #eee; padding-bottom: 5px;">🤝 พันธมิตร / สมาชิกสถาบันเหล็กฯ</div>
                        <div class="sponsor-logos-wrap">
                            {sponsor_html if sponsor_html else '<span style="color:#aaa; font-size:11px;">กำลังดึงโลโก้พาร์ทเนอร์...</span>'}
                        </div>
                    </div>

                </div>

                <div class="main-footer">
                    © 2026 IRON AND STEEL INSTITUTE OF THAILAND. ALL RIGHTS RESERVED.<br>
                    พัฒนาระบบเชื่อมโยงข้อมูลหลังบ้านอัตโนมัติด้วย FastAPI และปรับปรุงโครงสร้าง Layout ผ่าน Render Cloud
                </div>

            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return HTMLResponse(content=f"<div style='padding:50px; text-align:center;'><h3>เกิดข้อผิดพลาดจากทางเว็บต้นทาง: {str(e)}</h3></div>", status_code=500)

@app.get("/api/news")
def get_latest_news():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        seen_titles = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 15:
                if title in seen_titles or "ข่าวสารวงการเหล็ก" in title:
                    continue
                seen_titles.add(title)
                news_list.append({"title": title, "url": clean_url(href)})
        return {"status": "success", "count": len(news_list[:3]), "data": news_list[:3]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
