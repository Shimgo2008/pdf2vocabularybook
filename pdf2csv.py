import re
import nltk
from collections import Counter
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords
import csv

nltk.download('punkt')
nltk.download('stopwords')

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = ""
    
    def extract_text_from_pdf(self):
        """ PDFからテキストを抽出 """
        self.text = extract_text(self.pdf_path)
        return self.text
    
    def clean_text(self, text):
        """ テキストをクリーンアップ """
        text = re.sub(r'\x04', '', text)  # EOF削除
        text = text.lower()  # 小文字化
        cleaned_text = re.sub(r'\s+', ' ', text).strip()  # 空白や改行を整形
        return cleaned_text

    def get_most_common_words(self, text, num_words=1000):
        """ 最も頻出する単語を取得 """
        words = nltk.word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.lower() not in stop_words and word.isalpha()]
        word_counts = Counter(filtered_words)
        top_words = word_counts.most_common(num_words)
        return top_words
    
    def save_to_csv(self, top_words, ignore_len: int, csv_filename='out/word_frequencies.csv'):
        """ 頻出単語をCSVに保存 """
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Word', 'Frequency'])
            words = [(word, count) for word, count in top_words if len(word) > ignore_len]
            for word, count in words:
                writer.writerow([word, count])
    
    def extract_keys_from_csv(self, csv_filename):
        """ CSVから単語リストを抽出 """
        keys = []
        with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # ヘッダーをスキップ
            for row in reader:
                if row:
                    keys.append(row[0])
        return keys
