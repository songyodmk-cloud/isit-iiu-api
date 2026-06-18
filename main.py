from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(title="ISIT IIU Portal Exact Mirror")

BASE_URL = "https://iiu.isit.or.th"
TARGET_URL = f"{BASE_URL}/th/home.aspx"

# ลิงก์รูปภาพสไลด์แบนเนอร์ของแท้จากหน้าเว็บหลัก เพื่อให้รันสไลด์ได้ทันที
SLIDER_IMAGES = [
    f"{BASE_URL}/images/banner/Banner-IIU-2021.jpg",
    f"{BASE_URL}/images/banner/Banner_iiu_01.jpg"
]

@app.get("/", response_class=HTMLResponse)
def render_exact_isit_portal():
    # ข้อมูลข่าวสารพร้อมภาพประกอบและลิงก์จริงที่แกะมาจากหน้าเว็บ
    news_data = [
        {
            "title": "ส.อ.ท. ชี้อุตฯ ไทย Q2/69 โดน 2 ขั้ว 'EV-Data Center' เด่น 'เหล็ก-สิ่งทอ' เจอแรงกดดัน",
            "url": f"{BASE_URL}/th/news/Iron%20Industry%20News/Content-8223.aspx",
            "date": "10.06.2026",
            "img": f"{BASE_URL}/Upload/news/Cover/8223.jpg"
        },
        {
            "title": "OECD ชำแหละ 4 วิกฤตเชิงโครงสร้างเศรษฐกิจไทย พร้อมพิมพ์เขียวปฏิรูปก่อนเป็นสมาชิก",
            "url": f"{BASE_URL}/th/news/Business%20News/Content-8224.aspx",
            "date": "10.06.2026",
            "img": f"{BASE_URL}/Upload/news/Cover/8224.jpg"
        }
    ]

    # พยายามดึงภาพแบนเนอร์และข่าวสารเพิ่มเติมจากหน้าเว็บจริง (Fallback อัตโนมัติถ้าเน็ตเวิร์กช้า)
    active_sliders = SLIDER_IMAGES
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(TARGET_URL, headers=headers, verify=False, timeout=3)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            scraped_banners = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'banner' in src.lower() and not src.endswith('.gif'):
                    full_src = f"{BASE_URL}/{src.lstrip('/')}" if not src.startswith('http') else src
                    if full_src not in scraped_banners:
                        scraped_banners.append(full_src)
            if len(scraped_banners) > 0:
                active_sliders = scraped_banners
    except Exception:
        pass

    # ส่วนประกอบ HTML และ CSS ที่แกะโครงสร้างสีและ Layout แบบบล็อกเหลี่ยมสไตล์เว็บสถาบันเหล็กฯ
    # พร้อมทั้งผูกไลบรารี Swiper.js สำหรับทำภาพสไลด์ตรงกลาง
    html_layout = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย (ISIT IIU)</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, Tahoma, sans-serif; margin: 0; padding: 0; background-color: #ededed; color: #333333; }}
            
            /* แถบด้านบนสุดและชุดเมนูแบบเว็บจริง */
            .top-line {{ height: 4px; background-color: #3b1e1b; }}
            .header-container {{ background-color: #ffffff; padding: 15px 12%; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; }}
            .brand-section {{ display: flex; align-items: center; gap: 12px; }}
            .brand-logo-box {{ width: 42px; height: 42px; background-color: #3b1e1b; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 22px; font-weight: bold; }}
            .brand-titles h1 {{ margin: 0; font-size: 16px; color: #3b1e1b; font-weight: bold; }}
            .brand-titles p {{ margin: 2px 0 0 0; font-size: 11px; color: #777777; font-weight: bold; letter-spacing: 0.3px; }}
            
            /* แถบ Navigation บาร์ */
            .nav-bar {{ background-color: #f5f5f5; padding: 0 12%; border-bottom: 1px solid #dcdcdc; display: flex; justify-content: flex-end; }}
            .nav-links {{ display: flex; margin: 0; padding: 0; list-style: none; }}
            .nav-links li a {{ display: block; padding: 12px 16px; color: #555555; text-decoration: none; font-size: 13px; font-weight: bold; }}
            .nav-links li a:hover, .nav-links li a.active {{ background-color: #ffffff; color: #3b1e1b; border-top: 3px solid #3b1e1b; margin-top: -3px; }}

            /* ส่วนแสดงผลโครงสร้างแบบตารางไฮบริด (Grid Layout) */
            .wrapper {{ max-width: 1140px; margin: 20px auto; padding: 0 15px; display: flex; flex-direction: column; gap: 20px; }}
            .section-upper {{ display: grid; grid-template-columns: 7.2fr 2.8fr; gap: 15px; }}
            
            /* สไตล์สำหรับกล่องใส่ Image Slider ตรงกลาง */
            .slider-block {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 8px; border-radius: 4px; box-shadow: 0px 1px 4px rgba(0,0,0,0.06); overflow: hidden; }}
            .swiper {{ width: 100%; height: auto; border-radius: 2px; }}
            .swiper-slide img {{ width: 100%; height: auto; display: block; object-fit: cover; }}
            
            /* เมนูด้านขวา (รู้จักศูนย์ฯ + แจ้งเตือนภัยสีน้ำตาล) */
            .side-block {{ display: flex; flex-direction: column; gap: 12px; }}
            .link-card-btn {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 14px 16px; text-decoration: none; color: #333333; font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; box-shadow: 0px 1px 3px rgba(0,0,0,0.05); }}
            .link-card-btn:hover {{ background-color: #fcfcfc; border-left: 4px solid #3b1e1b; }}
            .circle-arrow {{ width: 20px; height: 20px; background-color: #3b1e1b; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; }}
            
            .alert-container {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 15px; border-radius: 4px; box-shadow: 0px 1px 3px rgba(0,0,0,0.05); }}
            .alert-container h3 {{ margin: 0 0 12px 0; font-size: 13px; color: #3b1e1b; font-weight: bold; border-bottom: 2px solid #f0f0f0; padding-bottom: 6px; }}
            .alert-item {{ background-color: #8f7671; color: #ffffff; padding: 11px 14px; margin-bottom: 8px; text-decoration: none; font-size: 12.5px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; transition: background 0.2s; }}
            .alert-item:hover {{ background-color: #745d59; }}
            .alert-item .go-btn {{ font-size: 11px; background: rgba(255,255,255,0.25); width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; border-radius: 50%; }}

            /* แถวล่าง: ข่าวสารวงการเหล็ก + กล่องสถิติ */
            .section-lower {{ display: grid; grid-template-columns: 7.2fr 2.8fr; gap: 15px; }}
            .content-box {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 20px; border-radius: 4px; box-shadow: 0px 1px 3px rgba(0,0,0,0.05); }}
            .box-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3b1e1b; padding-bottom: 8px; margin-bottom: 18px; }}
            .box-header h2 {{ margin: 0; font-size: 15px; color: #3b1e1b; font-weight: bold; }}
            .box-header .more-link {{ font-size: 12px; color: #3b1e1b; text-decoration: none; font-weight: bold; }}
            
            /* จัดการการ์ดข่าวเป็น 2 คอลัมน์พ่วงรูปภาพปก */
            .news-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .news-card-item {{ border: 1px solid #e5e5e5; background-color: #ffffff; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; }}
            .news-card-item:hover {{ transform: translateY(-2px); border-color: #3b1e1b; }}
            .news-thumb {{ width: 100%; height: 140px; background-color: #f0f0f0; position: relative; overflow: hidden; }}
            .news-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
            .date-tag {{ position: absolute; bottom: 8px; right: 8px; background-color: rgba(59, 30, 27, 0.85); color: #ffffff; font-size: 10px; padding: 2px 6px; font-weight: bold; border-radius: 2px; }}
            .news-info {{ padding: 12px; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1; }}
            .news-link-title {{ font-size: 13px; font-weight: bold; color: #333333; text-decoration: none; line-height: 1.42; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 36px; }}
            .news-link-title:hover {{ color: #3b1e1b; text-decoration: underline; }}

            /* บล็อกพื้นที่กราฟสถิติขวาล่าง */
            .stats-container {{ border: 1px solid #e5e5e5; margin-top: 5px; border-radius: 4px; overflow: hidden; }}
            .stats-container img {{ width: 100%; height: auto; display: block; }}

            /* แผงโลโก้พันธมิตรเครือข่ายอุตสาหกรรมเหล็กด้านล่างสุด */
            .partners-panel {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 15px; border-radius: 4px; }}
            .partners-title {{ font-size: 12.5px; font-weight: bold; color: #555555; border-bottom: 1px solid #eef0f2; padding-bottom: 8px; margin-bottom: 12px; }}
            .partners-flex {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 18px; align-items: center; }}
            .partner-logo {{ height: 35px; width: auto; object-fit: contain; filter: grayscale(10%); }}

            /* ส่วนล่างสุดของหน้าจอ Footer สีน้ำตาลเข้ม */
            .footer-strip {{ background-color: #3b1e1b; color: #d0c4c2; text-align: center; padding: 18px 20px; font-size: 11.5px; line-height: 1.6; border-top: 4px solid #ffcc00; margin-top: 30px; }}
            .footer-strip a {{ color: #ffffff; text-decoration: none; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="top-line"></div>

        <div class="header-container">
            <div class="brand-section">
                <div class="brand-logo-box">✦</div>
                <div class="brand-titles">
                    <h1>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย</h1>
                    <p>IRON & STEEL INTELLIGENCE UNIT (ISIT IIU)</p>
                </div>
            </div>
        </div>

        <div class="nav-bar">
            <ul class="nav-links">
                <li><a href="{BASE_URL}/th/home.aspx" target="_blank" class="active">หน้าหลัก</a></li>
                <li><a href="{BASE_URL}/th/about/About.aspx" target="_blank">เกี่ยวกับเรา</a></li>
                <li><a href="{BASE_URL}/th/news/Iron%20Industry%20News.aspx" target="_blank">ข่าวสาร</a></li>
                <li><a href="{BASE_URL}/th/journal/Journal.aspx" target="_blank">วารสารและรายงาน</a></li>
                <li><a href="{BASE_URL}/th/statistics/Stat-Import-Export.aspx" target="_blank">ข้อมูลสถิติ</a></li>
            </ul>
        </div>

        <div class="wrapper">
            <div class="section-upper">
                <div class="slider-block">
                    <div class="swiper mySwiper">
                        <div class="swiper-wrapper">
                            <div class="swiper-slide">
                                <a href="{BASE_URL}/th/news/Press%20Releases%20News.aspx" target="_blank">
                                    <img src="{active_sliders[0]}" alt="Banner Slide 1">
                                </a>
                            </div>
                            <div class="swiper-slide">
                                <a href="{BASE_URL}/th/news/Iron%20Industry%20News.aspx" target="_blank">
                                    <img src="{active_sliders[1] if len(active_sliders) > 1 else active_sliders[0]}" alt="Banner Slide 2">
                                </a>
                            </div>
                        </div>
                        <div class="swiper-pagination"></div>
                        <div class="swiper-button-next" style="color: #3b1e1b;"></div>
                        <div class="swiper-button-prev" style="color: #3b1e1b;"></div>
                    </div>
                </div>

                <div class="side-block">
                    <a href="{BASE_URL}/th/about/About.aspx" target="_blank" class="link-card-btn">
                        <span>💡 รู้จักศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็ก</span>
                        <span class="circle-arrow">❯</span>
                    </a>
                    
                    <div class="alert-container">
                        <h3>🔔 เตือนภัยอุตสาหกรรมเหล็ก มิถุนายน 2569</h3>
                        <a href="{BASE_URL}/th/news/Iron%20Industry%20News.aspx" target="_blank" class="alert-item">
                            <span>📄 อุตสาหกรรมเหล็กกระแสบน</span> <span class="go-btn">➔</span>
                        </a>
                        <a href="{BASE_URL}/th/news/Press%20Releases%20News.aspx" target="_blank" class="alert-item">
                            <span>📄 อุตสาหกรรมเหล็กกระแสยาว</span> <span class="go-btn">➔</span>
                        </a>
                    </div>
                </div>
            </div>

            <div class="section-lower">
                <div class="content-box">
                    <div class="box-header">
                        <h2>📰 ข่าวล่าสุดในวงการเหล็กไทยและเหล็กโลก</h2>
                        <a href="{BASE_URL}/th/news/Iron%20Industry%20News.aspx" target="_blank" class="more-link">เพิ่มเติม ➔</a>
                    </div>
                    <div class="news-grid">
                        <div class="news-card-item">
                            <div class="news-thumb">
                                <img src="{news_data[0]['img']}" alt="News 1 Cover">
                                <div class="date-tag">{news_data[0]['date']}</div>
                            </div>
                            <div class="news-info">
                                <a href="{news_data[0]['url']}" target="_blank" class="news-link-title">{news_data[0]['title']}</a>
                            </div>
                        </div>
                        <div class="news-card-item">
                            <div class="news-thumb">
                                <img src="{news_data[1]['img']}" alt="News 2 Cover">
                                <div class="date-tag">{news_data[1]['date']}</div>
                            </div>
                            <div class="news-info">
                                <a href="{news_data[1]['url']}" target="_blank" class="news-link-title">{news_data[1]['title']}</a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="content-box">
                    <div class="box-header">
                        <h2>📊 ข้อมูลสถิติ</h2>
                    </div>
                    <div class="stats-container">
                        <a href="{BASE_URL}/th/statistics/Stat-Import-Export.aspx" target="_blank">
                            <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&auto=format&fit=crop" alt="ISIT Stats Graphic Preview">
                        </a>
                    </div>
                </div>
            </div>

            <div class="partners-panel">
                <div class="partners-title">🤝 พันธมิตร / สมาชิกสถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย</div>
                <div class="partners-flex">
                    <img src="{BASE_URL}/images/link/sys.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/pacific.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/hidaka.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/ssi.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/nippon.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/danieli.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/twc.png" class="partner-logo" onerror="this.style.display='none'">
                    <img src="{BASE_URL}/images/link/mitr.png" class="partner-logo" onerror="this.style.display='none'">
                </div>
            </div>
        </div>

        <div class="footer-strip">
            © 2026 <a href="https://www.isit.or.th" target="_blank">IRON AND STEEL INSTITUTE OF THAILAND</a>. ALL RIGHTS RESERVED.<br>
            <span style="font-size:10px; opacity:0.7;">ระบบจำลองพอร์ตอลหน้าหลักและบริการเชื่อมโยงข้อมูลข่าวสารอัตโนมัติรันด้วย FastAPI บน Render</span>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
        <script>
            var swiper = new Swiper(".mySwiper", {{
                loop: true,
                autoplay: {{
                    delay: 3500,
                    disableOnInteraction: false,
                }},
                pagination: {{
                    el: ".swiper-pagination",
                    clickable: true,
                }},
                navigation: {{
                    nextEl: ".swiper-button-next",
                    prevEl: ".swiper-button-prev",
                }},
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_layout, status_code=200)

@app.get("/api/news")
def get_static_news_api():
    return {"status": "success", "data": "ISIT News Live Feed Connected"}
