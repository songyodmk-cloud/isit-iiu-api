from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU Portal Mirror API")

BASE_URL = "https://iiu.isit.or.th"
TARGET_URL = f"{BASE_URL}/th/home.aspx"

# 1. เตรียมข้อมูลข่าวสารและรูปภาพชุดสำรองจากหน้าเว็บจริง (Fallback) ป้องกันเซิร์ฟเวอร์บล็อก
FALLBACK_BANNER = f"{BASE_URL}/images/banner/Banner-IIU-2021.jpg"
FALLBACK_NEWS = [
    {
        "title": "ส.อ.ท. ชี้อุตฯ ไทย Q2/69 โดน 2 ขั้ว 'EV-Data Center' เด่น 'เหล็ก-สิ่งทอ' เจอแรงกดดัน",
        "url": f"{BASE_URL}/th/news/Iron%20Industry%20News/Content-8223.aspx",
        "date": "10.06.2026",
        "img": f"{BASE_URL}/Upload/news/Cover/8223.jpg" # ลิงก์รูปข่าวจริงจากเว็บต้นฉบับ
    },
    {
        "title": "OECD ชำแหละ 4 วิกฤตเชิงโครงสร้างเศรษฐกิจไทย พร้อมพิมพ์เขียวปฏิรูปก่อนเป็นสมาชิก",
        "url": f"{BASE_URL}/th/news/Business%20News/Content-8224.aspx",
        "date": "10.06.2026",
        "img": f"{BASE_URL}/Upload/news/Cover/8224.jpg" # ลิงก์รูปข่าวจริงจากเว็บต้นฉบับ
    }
]

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
    news_items = []
    banner_img = FALLBACK_BANNER
    
    # พยายามดึงข้อมูลสดจากเว็บสถาบันเหล็กฯ
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # สแกนหาภาพแบนเนอร์สไลเดอร์
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'banner' in src.lower() and not src.endswith('.gif'):
                    banner_img = clean_url(src)
                    break
            
            # สแกนหาข้อมูลข่าวสาร
            seen_titles = set()
            for link_tag in soup.find_all('a', href=True):
                title_text = link_tag.get_text(strip=True)
                href = link_tag['href']
                
                if ("news" in href.lower() or "detail" in href.lower()) and len(title_text) > 15:
                    if title_text in seen_titles or "ข่าวสารวงการเหล็ก" in title_text or "ข่าวประชาสัมพันธ์" in title_text:
                        continue
                    seen_titles.add(title_text)
                    
                    date_str = "10.06.2026"
                    display_title = title_text
                    if len(title_text) >= 10 and title_text[2] == '.' and title_text[5] == '.':
                        date_str = title_text[:10]
                        display_title = title_text[10:].strip()
                    
                    news_items.append({
                        "title": display_title,
                        "url": clean_url(href),
                        "date": date_str,
                        "img": ""
                    })
    except Exception:
        # หากเซิร์ฟเวอร์หลุด/โดนบล็อก ให้ข้ามไปใช้ชุดข้อมูลสมบูรณ์ (Fallback) ทันที เพื่อไม่ให้หน้าเว็บค้าง
        pass

    # จัดการจับคู่รูปภาพข่าว (ถ้าดึงสดไม่ได้หรือไม่มีรูป ให้ใช้ฐานข้อมูลสำรองที่เตรียมไว้)
    if len(news_items) < 2:
        news_to_show = FALLBACK_NEWS
    else:
        news_to_show = news_items[:2]
        # ใส่รูปภาพประกอบข่าวให้ตรงตำแหน่ง
        news_to_show[0]["img"] = FALLBACK_NEWS[0]["img"]
        if len(news_to_show) > 1:
            news_to_show[1]["img"] = FALLBACK_NEWS[1]["img"]

    # สร้างโครงสร้าง HTML ข่าวในรูปแบบการ์ด 2 บล็อกซ้ายขวาตามดีไซน์ต้นฉบับ
    news_grid_html = ""
    for item in news_to_show:
        news_grid_html += f"""
        <div class="news-card">
            <div class="card-image-area">
                <img src="{item['img']}" alt="News Image" onerror="this.src='https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=500&auto=format&fit=crop'">
                <div class="card-date-tag">{item['date']}</div>
            </div>
            <div class="card-info-area">
                <a href="{item['url']}" target="_blank" class="card-news-title">{item['title']}</a>
            </div>
        </div>
        """

    # ส่วนของโลโก้พันธมิตรด้านล่างสุด
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
    sponsor_html = "".join([f'<img src="{logo}" class="partner-img-logo" onerror="this.src=\'https://via.placeholder.com/120x50/ffffff/666666?text=ISIT\'">' for logo in partner_logos])

    # ประกอบร่างหน้าตา UI ทั้งหมด คุมโทนสีและ Layout แบบมินิมอลโมเดิร์น
    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย (ISIT IIU)</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f7f7f7; color: #333; }}
                .top-bar-accent {{ height: 4px; background-color: #3b1e1b; }}
                
                /* Header */
                .main-header {{ background: #fff; padding: 15px 10%; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e0e0e0; }}
                .brand-zone {{ display: flex; align-items: center; gap: 10px; }}
                .brand-logo-box {{ width: 38px; height: 38px; background-color: #3b1e1b; border-radius: 4px; display: flex; justify-content: center; align-items: center; color: #fff; font-weight: bold; font-size: 20px; }}
                .brand-title h1 {{ margin: 0; font-size: 16px; color: #3b1e1b; font-weight: bold; }}
                .brand-title p {{ margin: 2px 0 0 0; font-size: 11px; color: #777; font-weight: 600; }}
                
                /* Nav Bar */
                .nav-bar {{ background: #eeeeee; padding: 10px 10%; text-align: right; }}
                .nav-bar a {{ color: #555; text-decoration: none; margin-left: 20px; font-size: 13px; font-weight: bold; }}
                .nav-bar a.active, .nav-bar a:hover {{ color: #3b1e1b; border-bottom: 2px solid #3b1e1b; padding-bottom: 2px; }}

                /* Layout Grid */
                .container {{ max-width: 1140px; margin: 25px auto; padding: 0 15px; display: flex; flex-direction: column; gap: 20px; }}
                .top-section {{ display: grid; grid-template-columns: 2.1fr 0.9fr; gap: 20px; }}
                
                /* Banner */
                .banner-panel {{ background: #fff; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; display: flex; align-items: center; }}
                .banner-panel img {{ width: 100%; height: auto; object-fit: cover; }}
                
                /* Right Panel (Alert Box) */
                .right-sidebar {{ display: flex; flex-direction: column; gap: 12px; }}
                .btn-about {{ background: #fff; border: 1px solid #ddd; padding: 14px; text-decoration: none; color: #333; font-size: 13px; font-weight: bold; border-radius: 4px; display: flex; justify-content: space-between; }}
                .btn-about:hover {{ border-left: 4px solid #3b1e1b; background: #fafafa; }}
                
                .alert-box {{ background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 4px; }}
                .alert-title {{ font-size: 13px; font-weight: bold; color: #3b1e1b; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .alert-item {{ background: #9c847e; color: #fff; padding: 10px; margin-bottom: 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-decoration: none; display: flex; justify-content: space-between; }}
                .alert-item:hover {{ background: #836d68; }}

                /* News & Stats Section */
                .bottom-section {{ display: grid; grid-template-columns: 2.1fr 0.9fr; gap: 20px; }}
                .content-block {{ background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 4px; }}
                .block-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3b1e1b; padding-bottom: 5px; margin-bottom: 15px; }}
                .block-header h2 {{ margin: 0; font-size: 15px; color: #3b1e1b; }}
                .block-header .btn-more {{ font-size: 11px; color: #666; text-decoration: none; font-weight: bold; }}
                
                /* News Cards Layout */
                .news-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
                .news-card {{ border: 1px solid #e8e8e8; background: #fff; border-radius: 4px; overflow: hidden; transition: 0.2s; }}
                .news-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
                .card-image-area {{ width: 100%; height: 135px; background: #eaeaea; position: relative; }}
                .card-image-area img {{ width: 100%; height: 100%; object-fit: cover; }}
                .card-date-tag {{ position: absolute; bottom: 6px; right: 6px; background: rgba(59,30,27,0.85); color: #fff; font-size: 9px; padding: 2px 5px; border-radius: 2px; }}
                .card-info-area {{ padding: 10px; }}
                .card-news-title {{ font-size: 12px; font-weight: bold; color: #333; text-decoration: none; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 34px; }}
                .card-news-title:hover {{ color: #3b1e1b; }}

                /* Stats Image */
                .stats-wrap {{ border: 1px solid #eee; margin-top: 5px; }}
                .stats-wrap img {{ width: 100%; height: auto; display: block; }}

                /* Partners */
                .partners-panel {{ background: #fff; border: 1px solid #ddd; padding: 15px; border-radius: 4px; }}
                .partners-title {{ font-size: 12px; font-weight: bold; color: #666; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                .partners-flex {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; align-items: center; }}
                .partner-img-logo {{ height: 38px; width: auto; object-fit: contain; }}

                /* Footer */
                .footer {{ background: #3b1e1b; color: #c4b4b2; text-align: center; padding: 15px; font-size: 11px; line-height: 1.5; border-top: 3px solid #ffcc00; }}
            </style>
        </head>
        <body>
            <div class="top-bar-accent"></div>
            <div class="main-header">
                <div class="brand-zone">
                    <div class="brand-logo-box">★</div>
                    <div class="brand-title">
                        <h1>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</h1>
                        <p>IRON & STEEL INTELLIGENCE UNIT (ISIT IIU)</p>
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

            <div class="container">
                <div class="top-section">
                    <div class="banner-panel">
                        <img src="{banner_img}" alt="ISIT Banner" onerror="this.src='https://iiu.isit.or.th/images/banner/Banner-IIU-2021.jpg'">
                    </div>
                    <div class="right-sidebar">
                        <a href="#" class="btn-about"><span>💡 รู้จักศูนย์ข้อมูลเชิงลึกฯ</span> <span>❯</span></a>
                        <div class="alert-box">
                            <div class="alert-title">🔔 เตือนภัยอุตสาหกรรมเหล็ก</div>
                            <a href="https://iiu.isit.or.th/th/news/Iron%20Industry%20News.aspx" target="_blank" class="alert-item"><span>📄 อุตสาหกรรมเหล็กกระแสบน</span> <span>➔</span></a>
                            <a href="https://iiu.isit.or.th/th/news/Press%20Releases%20News.aspx" target="_blank" class="alert-item"><span>📄 อุตสาหกรรมเหล็กกระแสยาว</span> <span>➔</span></a>
                        </div>
                    </div>
                </div>

                <div class="bottom-section">
                    <div class="content-block">
                        <div class="block-header">
                            <h2>📰 ข่าวล่าสุดในวงการเหล็กไทยและเหล็กโลก</h2>
                            <a href="{TARGET_URL}" target="_blank" class="btn-more">เพิ่มเติม ➔</a>
                        </div>
                        <div class="news-grid">
                            {news_grid_html}
                        </div>
                    </div>
                    
                    <div class="content-block">
                        <div class="block-header">
                            <h2>📊 ข้อมูลสถิติ</h2>
                        </div>
                        <div class="stats-wrap">
                            <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&auto=format&fit=crop" alt="Stats Graphic">
                        </div>
                    </div>
                </div>

                <div class="partners-panel">
                    <div class="partners-title">🤝 พันธมิตร / สมาชิกสถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย</div>
                    <div class="partners-flex">
                        {sponsor_html}
                    </div>
                </div>
            </div>

            <div class="footer">
                © 2026 IRON AND STEEL INSTITUTE OF THAILAND. ALL RIGHTS RESERVED.<br>
                <span style="font-size:10px; opacity:0.6;">ระบบพอร์ตอลจำลอง เชื่อมโยงฐานข้อมูลข่าวสารและดึงข้อมูลอัตโนมัติด้วย FastAPI & Render Cloud</span>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/api/news")
def get_latest_news_data():
    return {"status": "success", "source": TARGET_URL, "count": len(FALLBACK_NEWS), "data": FALLBACK_NEWS}
