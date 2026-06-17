from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup
import urllib3

# ปิดคำเตือนเรื่อง SSL (เผื่อกรณีที่ใบรับรองของเว็บปลายทางมีปัญหาชั่วคราว)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI(
    title="ISIT IIU News API",
    description="API สำหรับดึงข้อมูลข่าวสารล่าสุดจากเว็บไซต์ สถาบันเหล็กและเหล็กกล้าแห่งประเทศไทย",
    version="1.0.0"
)

TARGET_URL = "https://iiu.isit.or.th/th/home.aspx"

@app.get("/")
def root():
    return {"message": "Welcome to ISIT IIU Scraping API. Go to /api/news to get latest news."}

@app.get("/api/news")
def get_latest_news():
    try:
        # 1. ส่ง Request ไปยังเว็บเป้าหมาย
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(TARGET_URL, headers=headers, verify=False, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="ไม่สามารถเข้าถึงเว็บไซต์เป้าหมายได้")
            
        # 2. นำ HTML ที่ได้มา Parse ด้วย BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ค้นหาข้อมูลข่าวสาร 
        # (หมายเหตุ: จุดนี้ต้องปรับเปลี่ยนตามโครงสร้าง HTML จริงของหน้าเว็บ เช่น ค้นหาจาก ID, Class หรือแท็ก <a>)
        news_list = []
        
        # ตัวอย่างการดึงข้อมูลจากแท็กลิงก์ที่มีคำว่า 'news' หรือ 'detail' อยู่ใน url
        # หรือปรับตรรกะตามโครงสร้างตาราง/กล่องข่าวของเว็บ iiu.isit.or.th
        for link in soup.find_all('a', href=True):
            href = link['href']
            title = link.get_text(strip=True)
            
            # กรองเอาเฉพาะลิงก์ที่น่าจะเป็นข่าวสาร และมีหัวข้อไม่ว่างเปล่า
            if ("news" in href.lower() or "detail" in href.lower()) and len(title) > 10:
                # ทำลิงก์ให้เป็นแบบ Absolute URL
                if href.startswith('/'):
                    full_url = f"https://iiu.isit.or.th{href}"
                elif not href.startswith('http'):
                    full_url = f"https://iiu.isit.or.th/th/{href}"
                else:
                    full_url = href
                    
                news_item = {
                    "title": title,
                    "url": full_url
                }
                
                # ป้องกันข้อมูลซ้ำ
                if news_item not in news_list:
                    news_list.append(news_item)
        
        # คืนค่ากลับไปเป็น JSON ล่าสุดสัก 10 ข่าว
        return {
            "status": "success",
            "source": TARGET_URL,
            "count": len(news_list[:10]),
            "data": news_list[:10]
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: {str(e)}")