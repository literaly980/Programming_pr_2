import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import os
from urllib.parse import urljoin
import json
import random

class WebScraperDemo:
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
    
    def generate_mock_data(self, max_objects=100):
        """Generate mock data for demonstration"""
        print("Generating mock data for demonstration...")
        
        mock_data = []
        categories = ["Science Fiction", "Fantasy", "Mystery", "Romance", "Thriller", 
                     "Biography", "History", "Technology", "Art", "Philosophy"]
        
        for i in range(1, max_objects + 1):
            category = random.choice(categories)
            
            # Generate realistic book titles
            title_templates = [
                f"The {random.choice(['Great', 'Lost', 'Hidden', 'Ancient', 'Modern'])} {random.choice(['Journey', 'Mystery', 'Adventure', 'Story', 'Tale'])}",
                f"{random.choice(['Understanding', 'Exploring', 'Discovering', 'Mastering'])} {category}",
                f"{random.choice(['Secrets', 'Principles', 'Foundations', 'Essentials'])} of {category}",
                f"The {random.choice(['Art', 'Science', 'Philosophy', 'History'])} of {random.choice(['Success', 'Innovation', 'Creativity', 'Leadership'])}"
            ]
            
            name = random.choice(title_templates)
            
            # Generate mock audio URL
            audio = f"https://example.com/audio/book_{i:03d}.mp3"
            
            # Generate mock image URL
            image = f"https://picsum.photos/seed/book{i}/200/300.jpg"
            
            # Generate mock description
            descriptions = [
                f"A comprehensive guide to {category.lower()} that explores fundamental concepts and practical applications.",
                f"This fascinating book delves into the world of {category.lower()}, offering unique insights and perspectives.",
                f"An essential read for anyone interested in {category.lower()}, combining theory with real-world examples.",
                f"Discover the latest trends and innovations in {category.lower()} through this engaging and informative work.",
                f"A masterful exploration of {category.lower()} that challenges conventional thinking and inspires new ideas."
            ]
            text = random.choice(descriptions)
            
            mock_data.append({
                'id': i,
                'name': name,
                'audio': audio,
                'image': image,
                'text': text
            })
            
            if i % 10 == 0:
                print(f"Generated {i}/{max_objects} mock objects")
        
        return mock_data
    
    def try_jsonplaceholder(self, max_objects=100):
        """Try to get data from JSONPlaceholder API"""
        print("Attempting to use JSONPlaceholder API...")
        
        try:
            # Get posts from JSONPlaceholder
            response = requests.get("https://jsonplaceholder.typicode.com/posts", timeout=10)
            response.raise_for_status()
            posts = response.json()
            
            # Get photos for images
            photos_response = requests.get("https://jsonplaceholder.typicode.com/photos", timeout=10)
            photos_response.raise_for_status()
            photos = photos_response.json()
            
            scraped_data = []
            
            for i, post in enumerate(posts[:max_objects]):
                # Get corresponding photo
                photo = photos[i] if i < len(photos) else photos[0]
                
                scraped_data.append({
                    'id': post['id'],
                    'name': post['title'].title(),
                    'audio': f"https://example.com/audio/post_{post['id']}.mp3",
                    'image': photo['url'],
                    'text': post['body']
                })
            
            print(f"Successfully retrieved {len(scraped_data)} items from JSONPlaceholder")
            return scraped_data
            
        except Exception as e:
            print(f"Error using JSONPlaceholder: {e}")
            return None
    
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
        
        # Try real API first
        data = self.try_jsonplaceholder(max_objects)
        
        # If that fails, use mock data
        if not data:
            print("Using mock data for demonstration...")
            data = self.generate_mock_data(max_objects)
        
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
    scraper = WebScraperDemo()
    scraper.run(100)
