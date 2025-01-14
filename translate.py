import csv
from collections import defaultdict
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests

class GoogleTranslateScraper:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.soup = None
        self.table = None

    def fetch_html(self):
        """HTMLを取得"""
        response = requests.get(self.url)
        self.html = response.text
        self.soup = BeautifulSoup(self.html, "html.parser")
        
    def extract_table(self):
        """必要なtableを取得"""
        self.table = self.soup.find_all("table", class_="CFNMfb")[0]

    def parse_table(self):
        """テーブルから必要なデータを抽出"""
        soup = BeautifulSoup(str(self.table), 'html.parser')
        
        extracted_data = []

        for row in soup.select('tbody tr'):
            part_of_speech = row.select_one('.eIKIse')
            if part_of_speech:
                part_of_speech = part_of_speech.get_text(strip=True)
            
            translations = row.select('td .FgtVoc li span')
            translation_list = [translation.get_text(strip=True) for translation in translations]
            
            frequency = row.select_one('.YF3enc')
            if frequency:
                frequency = frequency.get('aria-label', '').strip()

            extracted_data.append({
                'part_of_speech': part_of_speech,
                'translations': translation_list,
                'frequency': frequency
            })
        
        return extracted_data

    def scrape(self):
        """データ抽出のフロー"""
        self.fetch_html()
        self.extract_table()
        return self.parse_table()

class TranslatorProcessor:
    def __init__(self, words, src_lang, dest_lang="ja"):
        self.words = words
        self.src_lang = src_lang
        self.dest_lang = dest_lang

    async def detect_languages(self, word_list):
        """言語検出の処理"""
        results = []
        for word in tqdm(word_list, desc="Detecting languages", unit="word"):
            results.append((self.src_lang, 1.0))  # 言語検出のシミュレーション
        return results
    
    async def analyze_language_data(self, word_list):
        """言語データの分析"""
        language_counts = defaultdict(int)
        language_confidence_sum = defaultdict(float)
        results = await self.detect_languages(word_list)

        for lang, confidence in results:
            language_counts[lang] += 1
            language_confidence_sum[lang] += confidence

        language_average_confidence = {lang: language_confidence_sum[lang] / language_counts[lang]
                                       for lang in language_counts}

        return language_counts, language_average_confidence
    
    async def translate_bulk(self, scraped_data):
        """翻訳処理"""
        translations = []
        for entry in tqdm(scraped_data, desc="Processing scraped data", unit="entry"):
            for translated_word in entry['translations']:
                translations.append((entry['part_of_speech'], translated_word))
        return translations

    def save_to_csv(self, translated_pairs, original_lang, trans_lang, csv_filename='out/trans.csv'):
        """CSVに翻訳結果を保存"""
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([f'Original({original_lang})', f'Translated({trans_lang})'])
                for original, translated in translated_pairs:
                    writer.writerow([original, translated])
        except Exception as e:
            print(f"Error saving CSV file: {e}")
