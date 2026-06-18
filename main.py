from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU Portal Mirror API")

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- 1. ดึงภาพแบนเนอร์หลักสไลเดอร์จากเว็บจริง (Fallback ตัวล่าสุดที่มีบนเซิร์ฟเวอร์) ---
        banner_img = f"{BASE_URL}/images/banner/Banner-IIU-2021.jpg"
        # สแกนหาภาพสไลเดอร์ที่ใช้ในหน้าแรกจริง
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if 'banner' in src.lower() or 'slide' in src.lower() or 'home' in src.lower():
                if not src.endswith('.gif'): 
                    banner_img = clean_url(src)
                    break

        # --- 2. เจาะกลุ่มข้อมูลข่าวสาร (แกะกล่องข้อความข่าวพร้อมแยกรูปคู่ตัว) ---
        news_items = []
        seen_titles = set()
        
        # ค้นหาผ่านกล่องข่าวสารต้นฉบับ เพื่อจับคู่รูปคู่กับข้อความข่าว
        for table_box in soup.find_all(['table', 'div']):
            link_tag = table_box.find('a', href=True)
            img_tag = table_box.find('img')
            
            if link_tag:
                title_text = link_tag.get_text(strip=True)
                href = link_tag['href']
                
                if ("news" in href.lower() or "detail" in href.lower()) and len(title_text) > 15:
                    if title_text in seen_titles or "ข่าวสารวงการเหล็ก" in title_text or "ข่าวประชาสัมพันธ์" in title_text:
                        continue
                    
                    seen_titles.add(title_text)
                    
                    # สกัดรูป Thumbnail ข่าว
                    img_src = ""
                    if img_tag and img_tag.get('src'):
                        img_src = clean_url(img_tag.get('src'))
                    else:
                        # เจาะหาภาพในตารางข้างเคียง
                        sibling_img = table_box.find_next('img')
                        if sibling_img:
                            img_src = clean_url(sibling_img.get('src', ''))

                    # แยกวันที่ออกจากหัวข้อข่าว
                    date_str = "10.06.2026"
                    display_title = title_text
                    if len(title_text) >= 10 and title_text[2] == '.' and title_text[5] == '.':
                        date_str = title_text[:10]
                        display_title = title_text[10:].strip()
                    
                    if not img_src or "bullet" in img_src.lower() or "icon" in img_src.lower():
                        img_src = f"{BASE_URL}/images/news/default.jpg" # หรือใช้ Placeholder สวยๆ

                    news_items.append({
                        "title": display_title,
                        "url": clean_url(href),
                        "date": date_str,
                        "img": img_src
                    })

        # สร้างโครง HTML ข่าว 2 บล็อกหลักยอดนิยมพร้อมรูปประกอบตามต้นฉบับ
        news_grid_html = ""
        # บังคับดึงรูปภาพข่าวที่มีจากหน้าเว็บหลักมาวาง
        news_to_show = news_items[:2]
        if len(news_to_show) > 0:
            for item in news_to_show:
                # แก้ไข Broken Image โดยให้ใช้ภาพจริง หรือสลับไปใช้ภาพจำลองข่าวเศรษฐกิจถ้าดึงไม่ผ่าน
                final_img = item['img']
                if 'default.jpg' in final_img:
                    final_img = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=500&auto=format&fit=crop"

                news_grid_html += f"""
                <div class="news-card">
                    <div class="card-image-area">
                        <img src="{final_img}" alt="News Picture">
                        <div class="card-date-tag">{item['date']}</div>
                    </div>
                    <div class="card-info-area">
                        <a href="{item['url']}" target="_blank" class="card-news-title">{item['title']}</a>
                    </div>
                </div>
                """
        else:
            news_grid_html = "<p style='color:#999; padding:20px;'>กำลังเชื่อมต่อฐานข้อมูลข่าวสารสถาบันเหล็ก...</p>"

        # --- 3. ดึงกลุ่มโลโก้ผู้สนับสนุนสัญญลักษณ์สถาบันเหล็กด้านล่างสุด ---
        partner_logos = [
            f"{BASE_URL}/images/link/sys.png",
            f"{BASE_URL}/images/link/pacific.png",
            f"{BASE_URL}/images/link/hidaka.png",
            f"{BASE_URL}/images/link/ssi.png",
            f"{BASE_URL}/images/link/nippon.png",
            f"{BASE_URL}/images/link/danieli.png",
            f"{BASE_URL}/images/link/twc.png",
            f"{BASE_URL}/images/link/mitr.png"
        ]
        
        sponsor_html = ""
        for logo_url in partner_logos:
            sponsor_html += f'<img src="{logo_url}" class="partner-img-logo" onerror="this.src=\'https://via.placeholder.com/120x50/ffffff/666666?text=ISIT+PARTNER\'">'

        # --- 4. ประกอบร่างชุดหน้าตา Layout ให้ถอดแบบออกมาเป๊ะๆ ---
        html_content = f"""
        <!DOCTYPE html>
        <html lang="th">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย (ISIT IIU)</title>
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, 'MS Sans Serif'; margin: 0; padding: 0; background-color: #fcfcfc; color: #3a3a3a; }}
                    
                    /* แถบคาดบนสุดสีน้ำตาลเข้ม */
                    .top-line-accent {{ height: 5px; background-color: #3b1e1b; width: 100%; }}

                    /* หัวเว็บ (Header Bar) */
                    .header-main-container {{ background: #ffffff; padding: 15px 12%; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e8e8e8; }}
                    .identity-group {{ display: flex; align-items: center; gap: 12px; }}
                    .identity-logo-box {{ width: 42px; height: 42px; background-color: #3b1e1b; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 22px; font-weight: bold; }}
                    .identity-text h1 {{ margin: 0; font-size: 16px; color: #3b1e1b; font-weight: bold; letter-spacing: 0.5px; }}
                    .identity-text p {{ margin: 2px 0 0 0; font-size: 10.5px; color: #8c8c8c; font-weight: 600; letter-spacing: 0.8px; }}
                    
                    /* แถบเมนูนำทางด้านขวา */
                    .menu-navigation-bar {{ background: #f4f4f4; padding: 10px 12%; text-align: right; border-bottom: 1px solid #e0e0e0; }}
                    .menu-navigation-bar a {{ color: #555555; text-decoration: none; margin-left: 22px; font-size: 13px; font-weight: bold; transition: 0.2s; }}
                    .menu-navigation-bar a:hover, .menu-navigation-bar a.active {{ color: #3b1e1b; border-bottom: 2px solid #3b1e1b; padding-bottom: 3px; }}

                    /* พื้นที่แสดงผลโครงสร้างหลัก 2 ฝั่ง (Grid) */
                    .portal-content-grid {{ max-width: 1200px; margin: 25px auto; padding: 0 15px; display: grid; grid-template-columns: 2.1fr 0.9fr; gap: 20px; }}
                    
                    /* ฝั่งซ้าย: สไลเดอร์ภาพโฆษณาจัดส่งใบประกาศประเมิน */
                    .left-hero-slider-area {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03); display: flex; }}
                    .left-hero-slider-area img {{ width: 100%; height: auto; display: block; object-fit: contain; }}
                    
                    /* ฝั่งขวา: เมนูส้ม/น้ำตาล - กล่องเตือนภัยอุตสาหกรรมเหล็ก */
                    .right-sidebar-panel {{ display: flex; flex-direction: column; gap: 15px; }}
                    .info-button-link {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; padding: 15px; text-decoration: none; display: flex; justify-content: space-between; align-items: center; color: #333333; font-size: 13px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: 0.2s; }}
                    .info-button-link:hover {{ background: #fafafa; border-left: 4px solid #3b1e1b; }}
                    .info-button-link span.arrow {{ color: #3b1e1b; font-size: 16px; }}

                    .alert-status-container {{ background: #ffffff; border: 1px solid #e0e0e0; border-radius: 4px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
                    .alert-header-text {{ font-size: 12.5px; font-weight: bold; color: #3b1e1b; margin-bottom: 12px; border-bottom: 1px solid #f0f0f0; padding-bottom: 6px; }}
                    .alert-action-button {{ background-color: #9c847e; color: #ffffff; padding: 12px; margin-bottom: 8px; border-radius: 4px; font-size: 11.5px; font-weight: bold; text-decoration: none; display: flex; align-items: center; justify-content: space-between; transition: 0.2s; }}
                    .alert-action-button:hover {{ background-color: #836d68; }}

                    /* ส่วนหมวดหมู่เนื้อหาด้านล่าง: ข่าวสาร สถิติ วารสาร */
                    .sub-content-fullwidth {{ grid-column: span 2; display: grid; grid-template-columns: 2.1fr 0.9fr; gap: 20px; margin-top: 10px; }}
                    
                    .news-section-box {{ background: #ffffff; border: 1px solid #e0e0e0; padding: 20px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
                    .section-title-row {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3b1e1b; padding-bottom: 5px; margin-bottom: 18px; }}
                    .section-title-row h2 {{ margin: 0; font-size: 16px; color: #3b1e1b; font-weight: bold; }}
                    .section-title-row .more-link-btn {{ font-size: 11.5px; color: #666666; text-decoration: none; font-weight: bold; }}
                    
                    /* รายการกล่องการ์ดข่าวสาร */
                    .news-row-flex {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
                    .news-card {{ border: 1px solid #eef0f2; background-color: #ffffff; border-radius: 4px; overflow: hidden; }}
                    .card-image-area {{ width: 100%; height: 140px; background-color: #f0f0f0; position: relative; overflow: hidden; }}
                    .card-image-area img {{ width: 100%; height: 100%; object-fit: cover; }}
                    .card-date-tag {{ position: absolute; bottom: 8px; right: 8px; background: rgba(59, 30, 27, 0.85); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 2px; font-weight: bold; }}
                    .card-info-area {{ padding: 10px; }}
                    .card-news-title {{ font-size: 12.5px; font-weight: bold; color: #2c3e50; text-decoration: none; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 34px; }}
                    .card-news-title:hover {{ color: #3b1e1b; }}

                    /* บล็อกฝั่งขวา: ข้อมูลสถิติพรีวิว */
                    .stats-section-box {{ background: #ffffff; border: 1px solid #e0e0e0; padding: 20px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
                    .stats-preview-img-wrap {{ border: 1px solid #eaeaea; border-radius: 4px; overflow: hidden; margin-top: 10px; }}
                    .stats-preview-img-wrap img {{ width: 100%; height: auto; display: block; }}

                    /* ส่วนแบรนด์พาร์ทเนอร์สปอนเซอร์แถบล่างสุด */
                    .partners-section-container {{ grid-column: span 2; background: #ffffff; border: 1px solid #e0e0e0; padding: 20px; border-radius: 4px; }}
                    .partners-header-label {{ font-size: 12.5px; font-weight: bold; color: #555555; border-bottom: 1px solid #eeeeee; padding-bottom: 6px; margin-bottom: 15px; }}
                    .partners-logos-flex-row {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; align-items: center; }}
                    .partner-img-logo {{ height: 42px; width: auto; object-fit: contain; filter: saturate(90%); transition: 0.2s; }}
                    .partner-img-logo:hover {{ filter: saturate(100%); transform: scale(1.03); }}

                    /* ส่วนท้ายเว็บสีน้ำตาลเข้ม (Footer) */
                    .portal-footer {{ background-color: #3b1e1b; color: #d1c1bf; text-align: center; padding: 18px 20px; font-size: 11px; line-height: 1.6; margin-top: 40px; border-top: 3px solid #ffcc00; }}
                </style>
            </head>
            <body>
                <div class="top-line-accent"></div>

                <div class="header-main-container">
                    <div class="identity-group">
                        <div class="identity-logo-box">✦</div>
                        <div class="identity-text">
                            <h1>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</h1>
                            <p>IRON & STEEL INTELLIGENCE UNIT (ISIT IIU)</p>
                        </div>
                    </div>
                </div>

                <div class="menu-navigation-bar">
                    <a href="#" class="active">หน้าหลัก</a>
                    <a href="#">เกี่ยวกับเรา</a>
                    <a href="#">ข่าวสาร</a>
                    <a href="#">วารสารและรายงาน</a>
                    <a href="#">ข้อมูลสถิติ</a>
                </div>

                <div class="portal-content-grid">
                    
                    <div class="left-hero-slider-area">
                        <img src="{banner_img}" alt="ISIT Hero Image" onerror="this.src='https://iiu.isit.or.th/images/banner/Banner-IIU-2021.jpg'">
                    </div>

                    <div class="right-sidebar-panel">
                        <a href="#" class="info-button-link">
                            <span>💡 รู้จักศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็ก</span>
                            <span class="arrow">❯</span>
                        </a>
                        
                        <div class="alert-status-container">
                            <div class="alert-header-text">🔔 เตือนภัยอุตสาหกรรมเหล็ก มิถุนายน 2569</div>
                            <a href="https://iiu.isit.or.th/th/news/Iron%20Industry%20News.aspx" target="_blank" class="alert-action-button">
                                <span>📄 อุตสาหกรรมเหล็กกระแสบน</span> <span>➔</span>
                            </a>
                            <a href="https://iiu.isit.or.th/th/news/Press%20Releases%20News.aspx" target="_blank" class="alert-action-button">
                                <span>📄 อุตสาหกรรมเหล็กกระแสยาว</span> <span>➔</span>
                            </a>
                        </div>
                    </div>

                    <div class="sub-content-fullwidth">
                        
                        <div class="news-section-box">
                            <div class="section-title-row">
                                <h2>📰 ข่าวล่าสุดในวงการเหล็กไทยและเหล็กโลก</h2>
                                <a href="{TARGET_URL}" target="_blank" class="more-link-btn">เพิ่มเติม ➔</a>
                            </div>
                            <div class="news-row-flex">
                                {news_grid_html}
                            </div>
                        </div>

                        <div class="stats-section-box">
                            <div class="section-title-row">
                                <h2>📊 ข้อมูลสถิติ</h2>
                            </div>
                            <div class="stats-preview-img-wrap">
                                <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&auto=format&fit=crop" alt="Stats Graphic" style="opacity:0.85;">
                            </div>
                        </div>

                        <div class="partners-section-container">
                            <div class="partners-header-label">🤝 พันธมิตร / สมาชิกสถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย</div>
                            <div class="partners-logos-flex-row">
                                {sponsor_html}
                            </div>
                        </div>

                    </div>
                </div>

                <div class="portal-footer">
                    © 2026 IRON AND STEEL INSTITUTE OF THAILAND. ALL RIGHTS RESERVED.<br>
                    <span style="font-size:10px; opacity:0.7">ระบบจำลองเว็บพอร์ตอลและคัดกรองเนื้อหาอัจฉริยะอัตโนมัติ เชื่อมโยงฐานข้อมูลหลังบ้านผ่าน REST API (FastAPI)</span>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return HTMLResponse(content=f"<div style='padding:50px; text-align:center;'><h3>ขออภัย เกิดข้อผิดพลาดจากเครือข่าย: {str(e)}</h3></div>", status_code=500)

@app.get("/api/news")
def get_latest_news_data():
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
        return {"status": "success", "data": news_list[:2]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
