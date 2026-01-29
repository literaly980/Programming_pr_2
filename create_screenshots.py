import subprocess
import time
import os

def create_screenshots():
    """Create screenshots of the program running"""
    
    print("📸 Создание скриншотов для GitHub...")
    
    # Screenshot 1: Run main scraper
    print("\n📸 Скриншот 1: Запуск основного скрапера")
    os.system('python khpet27_scraper.py')
    time.sleep(2)
    
    # Screenshot 2: Verify data
    print("\n📸 Скриншот 2: Проверка данных в БД")
    os.system('python verify_data.py')
    time.sleep(2)
    
    # Screenshot 3: Run demo scraper
    print("\n📸 Скриншот 3: Запуск демо-скрапера")
    os.system('python scraper_demo.py')
    time.sleep(2)
    
    print("\n✅ Скриншоты созданы!")

if __name__ == "__main__":
    create_screenshots()
