import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os
from urllib.parse import urljoin
import random

class WebScraper:
    def __init__(self, db_name="scraped_data.db"):
        self.db_name = db_name
        self.setup_database()
    
    def setup_database(self):
        """Create database and table if they don't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS objects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                audio TEXT,
                image TEXT,
                text TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database '{self.db_name}' created/connected successfully")
    
    def scrape_books_to_scrape(self, max_objects=100):
        """Scrape books from books.toscrape.com"""
        base_url = "http://books.toscrape.com/catalogue/page-{}.html"
        scraped_data = []
        page = 1
        
        print("Starting to scrape books.toscrape.com...")
        
        while len(scraped_data) < max_objects:
            url = base_url.format(page)
            print(f"Scraping page {page}: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                books = soup.find_all('article', class_='product_pod')
                
                if not books:
                    print("No more books found")
                    break
                
                for book in books:
                    if len(scraped_data) >= max_objects:
                        break
                    
                    # Extract book data
                    title = book.h3.a['title']
                    relative_url = book.h3.a['href']
                    full_url = urljoin("http://books.toscrape.com/catalogue/", relative_url)
                    
                    # Get detailed book information
                    try:
                        book_response = requests.get(full_url, timeout=10)
                        book_soup = BeautifulSoup(book_response.content, 'html.parser')
                        
                        # Extract image URL
                        image_elem = book_soup.find('div', class_='item').find('img')
                        image_url = urljoin("http://books.toscrape.com/", image_elem['src']) if image_elem else ""
                        
                        # Extract description/text
                        description_elem = book_soup.find('div', id='product_description')
                        if description_elem:
                            text = description_elem.find_next_sibling('p').text.strip()
                        else:
                            text = "No description available"
                        
                        # Generate audio URL (mock data since books.toscrape doesn't have audio)
                        audio_url = f"https://example.com/audio/{len(scraped_data) + 1}.mp3"
                        
                        scraped_data.append({
                            'id': len(scraped_data) + 1,
                            'name': title,
                            'audio': audio_url,
                            'image': image_url,
                            'text': text
                        })
                        
                        print(f"Scraped {len(scraped_data)}/{max_objects}: {title}")
                        
                    except Exception as e:
                        print(f"Error getting details for {title}: {e}")
                        continue
                
                page += 1
                time.sleep(1)  # Be respectful to the server
                
            except requests.RequestException as e:
                print(f"Error scraping page {page}: {e}")
                break
        
        return scraped_data[:max_objects]
    
    def save_to_database(self, data):
        """Save scraped data to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM objects")
        
        # Insert new data
        for item in data:
            cursor.execute('''
                INSERT INTO objects (id, name, audio, image, text)
                VALUES (?, ?, ?, ?, ?)
            ''', (item['id'], item['name'], item['audio'], item['image'], item['text']))
        
        conn.commit()
        conn.close()
        print(f"Successfully saved {len(data)} items to database")
    
    def display_data(self, limit=10):
        """Display data from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, audio, image, text FROM objects ORDER BY id LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        print("\n" + "="*80)
        print(f"{'ID':<5} | {'Name':<30} | {'Audio':<25} | {'Image':<25} | {'Text':<30}")
        print("-"*80)
        
        for row in rows:
            id_val, name, audio, image, text = row
            # Truncate long strings for display
            name_display = name[:27] + "..." if len(name) > 30 else name
            audio_display = audio[:22] + "..." if len(audio) > 25 else audio
            image_display = image[:22] + "..." if len(image) > 25 else image
            text_display = text[:27] + "..." if len(text) > 30 else text
            
            print(f"{id_val:<5} | {name_display:<30} | {audio_display:<25} | {image_display:<25} | {text_display:<30}")
        
        print("-"*80)
        
        cursor.execute("SELECT COUNT(*) FROM objects")
        total_count = cursor.fetchone()[0]
        print(f"Total records in database: {total_count}")
        
        conn.close()
    
    def run(self, max_objects=100):
        """Main method to run the scraper"""
        print(f"Starting web scraper to collect {max_objects} objects...")
        
        # Scrape data
        data = self.scrape_books_to_scrape(max_objects)
        
        if data:
            # Save to database
            self.save_to_database(data)
            
            # Display first few records
            self.display_data()
            
            print(f"\nScraping completed successfully!")
            print(f"Data saved to '{self.db_name}'")
        else:
            print("No data was scraped")

if __name__ == "__main__":
    scraper = WebScraper()
    scraper.run(100)
