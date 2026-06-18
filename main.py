from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="ISIT IIU Portal - 100% Stable Presentation")

BASE_URL = "https://iiu.isit.or.th"

@app.get("/", response_class=HTMLResponse)
def render_exact_isit_portal():
    # =========================================================================
    # เปลี่ยนมาใช้ CDN รูปภาพความละเอียดสูงที่เสถียรและตรงตามบริบทของสถาบันเหล็ก
    # วิธีนี้จะแก้ปัญหาภาพพังจากเซิร์ฟเวอร์ต้นทางได้อย่างเด็ดขาด 100%
    # =========================================================================
    
    # ภาพแบนเนอร์สไลเดอร์ (ภาพแนวโรงงานอุตสาหกรรมเหล็กและนวัตกรรมดิจิทัล)
    slide1_url = "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&q=80"
    slide2_url = "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=1200&q=80"
    
    # ภาพประกอบข่าว (ข่าวสภาอุตสาหกรรม และวิกฤตเศรษฐกิจโครงสร้างไทย)
    news1_url = "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&q=80"
    news2_url = "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80"
    
    # ภาพกราฟข้อมูลสถิติ
    stats_url = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500&q=80" 

    # โลโก้พันธมิตรและสมาชิกสถาบัน (ใช้ภาพสัญลักษณ์ Placeholder สไตล์มินิมอล โทนสีน้ำตาลเข้ากับเว็บ)
    partner_logos = [
        "SYS+Steel", "Pacific+Pipe", "Hidaka+Yookoo", "SSI+Steel", 
        "Nippon+Steel", "Danieli", "TWC", "Mitr+Steel"
    ]
    partner_html = ""
    for logo_name in partner_logos:
        partner_html += f'<img src="https://placehold.co/140x50/3b1e1b/ffffff?text={logo_name}" class="partner-logo" alt="{logo_name}">'

    html_layout = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็กไทย (ISIT IIU)</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
        <style>
            body {{ font-family: Tahoma, Geneva, sans-serif; margin: 0; padding: 0; background-color: #ededed; color: #333333; }}
            .top-line {{ height: 4px; background-color: #3b1e1b; }}
            .header-container {{ background-color: #ffffff; padding: 15px 12%; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; }}
            .brand-section {{ display: flex; align-items: center; gap: 12px; }}
            .brand-logo-box {{ width: 42px; height: 42px; background-color: #3b1e1b; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #ffffff; font-size: 22px; font-weight: bold; }}
            .brand-titles h1 {{ margin: 0; font-size: 16px; color: #3b1e1b; font-weight: bold; }}
            .brand-titles p {{ margin: 2px 0 0 0; font-size: 11px; color: #777777; font-weight: bold; letter-spacing: 0.3px; }}
            
            .nav-bar {{ background-color: #f5f5f5; padding: 0 12%; border-bottom: 1px solid #dcdcdc; display: flex; justify-content: flex-end; }}
            .nav-links {{ display: flex; margin: 0; padding: 0; list-style: none; }}
            .nav-links li a {{ display: block; padding: 12px 16px; color: #555555; text-decoration: none; font-size: 13px; font-weight: bold; }}
            .nav-links li a:hover, .nav-links li a.active {{ background-color: #ffffff; color: #3b1e1b; border-top: 3px solid #3b1e1b; margin-top: -3px; }}

            .wrapper {{ max-width: 1140px; margin: 20px auto; padding: 0 15px; display: flex; flex-direction: column; gap: 20px; }}
            .section-upper {{ display: grid; grid-template-columns: 7.2fr 2.8fr; gap: 15px; }}
            
            .slider-block {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 8px; border-radius: 4px; box-shadow: 0px 1px 4px rgba(0,0,0,0.06); overflow: hidden; height: 350px; }}
            .swiper {{ width: 100%; height: 100%; border-radius: 2px; }}
            .swiper-slide img {{ width: 100%; height: 100%; display: block; object-fit: cover; }}
            
            .side-block {{ display: flex; flex-direction: column; gap: 12px; }}
            .link-card-btn {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 14px 16px; text-decoration: none; color: #333333; font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; }}
            .link-card-btn:hover {{ background-color: #fcfcfc; border-left: 4px solid #3b1e1b; }}
            .circle-arrow {{ width: 20px; height: 20px; background-color: #3b1e1b; color: #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; }}
            
            .alert-container {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 15px; border-radius: 4px; }}
            .alert-container h3 {{ margin: 0 0 12px 0; font-size: 13px; color: #3b1e1b; font-weight: bold; border-bottom: 2px solid #f0f0f0; padding-bottom: 6px; }}
            .alert-item {{ background-color: #8f7671; color: #ffffff; padding: 11px 14px; margin-bottom: 8px; text-decoration: none; font-size: 12.5px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; }}
            .alert-item:hover {{ background-color: #745d59; }}

            .section-lower {{ display: grid; grid-template-columns: 7.2fr 2.8fr; gap: 15px; }}
            .content-box {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 20px; border-radius: 4px; }}
            .box-header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3b1e1b; padding-bottom: 8px; margin-bottom: 18px; }}
            .box-header h2 {{ margin: 0; font-size: 15px; color: #3b1e1b; font-weight: bold; }}
            
            .news-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .news-card-item {{ border: 1px solid #e5e5e5; background-color: #ffffff; border-radius: 4px; overflow: hidden; display: flex; flex-direction: column; }}
            .news-thumb {{ width: 100%; height: 160px; background-color: #f5f5f5; position: relative; overflow: hidden; }}
            .news-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
            .date-tag {{ position: absolute; bottom: 8px; right: 8px; background-color: rgba(59, 30, 27, 0.85); color: #ffffff; font-size: 10px; padding: 2px 6px; font-weight: bold; border-radius: 2px; }}
            .news-info {{ padding: 12px; display: flex; flex-direction: column; justify-content: space-between; flex-grow: 1; }}
            .news-link-title {{ font-size: 13px; font-weight: bold; color: #333333; text-decoration: none; line-height: 1.42; }}

            .stats-container {{ border: 1px solid #e5e5e5; border-radius: 4px; overflow: hidden; }}
            .stats-container img {{ width: 100%; height: auto; display: block; }}

            .partners-panel {{ background-color: #ffffff; border: 1px solid #cccccc; padding: 15px; border-radius: 4px; }}
            .partners-title {{ font-size: 12.5px; font-weight: bold; color: #555555; border-bottom: 1px solid #eef0f2; padding-bottom: 8px; margin-bottom: 12px; }}
            .partners-flex {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; align-items: center; }}
            .partner-logo {{ height: 34px; width: auto; object-fit: contain; border-radius: 3px; }}

            .footer-strip {{ background-color: #3b1e1b; color: #d0c4c2; text-align: center; padding: 18px 20px; font-size: 11.5px; line-height: 1.6; border-top: 4px solid #ffcc00; margin-top: 30px; }}
            .footer-strip a {{ color: #ffffff; text-decoration: none; }}
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
                <li><a href="#" class="active">หน้าหลัก</a></li>
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
                                <img src="{slide1_url}" alt="Banner 1">
                            </div>
                            <div class="swiper-slide">
                                <img src="{slide2_url}" alt="Banner 2">
                            </div>
                        </div>
                        <div class="swiper-pagination"></div>
                        <div class="swiper-button-next"></div>
                        <div class="swiper-button-prev"></div>
                    </div>
                </div>

                <div class="side-block">
                    <a href="{BASE_URL}/th/about/About.aspx" target="_blank" class="link-card-btn">
                        <span>💡 รู้จักศูนย์ข้อมูลเชิงลึกอุตสาหกรรมเหล็ก</span>
                        <span class="circle-arrow">❯</span>
                    </a>
                    <div class="alert-container">
                        <h3>🔔 เตือนภัยอุตสาหกรรมเหล็ก มิถุนายน 2569</h3>
                        <div class="alert-item">📄 อุตสาหกรรมเหล็กกระแสบน</div>
                        <div class="alert-item">📄 อุตสาหกรรมเหล็กกระแสยาว</div>
                    </div>
                </div>
            </div>

            <div class="section-lower">
                <div class="content-box">
                    <div class="box-header">
                        <h2>📰 ข่าวล่าสุดในวงการเหล็กไทยและเหล็กโลก</h2>
                    </div>
                    <div class="news-grid">
                        <div class="news-card-item">
                            <div class="news-thumb">
                                <img src="{news1_url}" alt="News 1">
                                <div class="date-tag">10.06.2026</div>
                            </div>
                            <div class="news-info">
                                <a href="{BASE_URL}/th/news/Iron%20Industry%20News/Content-8223.aspx" target="_blank" class="news-link-title">ส.อ.ท. ชี้อุตฯ ไทย Q2/69 โดน 2 ขั้ว 'EV-Data Center' เด่น 'เหล็ก-สิ่งทอ' เจอแรงกดดัน</a>
                            </div>
                        </div>
                        <div class="news-card-item">
                            <div class="news-thumb">
                                <img src="{news2_url}" alt="News 2">
                                <div class="date-tag">10.06.2026</div>
                            </div>
                            <div class="news-info">
                                <a href="{BASE_URL}/th/news/Business%20News/Content-8224.aspx" target="_blank" class="news-link-title">OECD ชำแหละ 4 วิกฤตเชิงโครงสร้างเศรษฐกิจไทย พร้อมพิมพ์เขียวปฏิรูปก่อนเป็นสมาชิก</a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="content-box">
                    <div class="box-header">
                        <h2>📊 ข้อมูลสถิติ</h2>
                    </div>
                    <div class="stats-container">
                        <img src="{stats_url}" alt="Stats Graph">
                    </div>
                </div>
            </div>

            <div class="partners-panel">
                <div class="partners-title">🤝 พันธมิตร / สมาชิกสถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย</div>
                <div class="partners-flex">
                    {partner_html}
                </div>
            </div>
        </div>

        <div class="footer-strip">
            © 2026 <a href="https://www.isit.or.th" target="_blank" style="color:#fff;">IRON AND STEEL INSTITUTE OF THAILAND</a>. ALL RIGHTS RESERVED.
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
