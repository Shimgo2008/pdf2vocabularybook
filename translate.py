import csv
from googletrans import Translator
from collections import defaultdict
from tqdm import tqdm

class TranslatorProcessor:
    def __init__(self, words, src_lang, dest_lang="ja"):
        self.words = words
        self.src_lang = src_lang
        self.dest_lang = dest_lang

    async def detect_languages(self, word_list):
        async with Translator() as translator:
            results = []
            for word in tqdm(word_list, desc="Detecting languages", unit="word"):
                result = await translator.detect(word)
                results.append((result.lang, result.confidence))
            return results
    
    async def analyze_language_data(self, word_list):
        language_counts = defaultdict(int)
        language_confidence_sum = defaultdict(float)
        results = await self.detect_languages(word_list)

        for lang, confidence in results:
            language_counts[lang] += 1
            language_confidence_sum[lang] += confidence

        language_average_confidence = {lang: language_confidence_sum[lang] / language_counts[lang]
                                       for lang in language_counts}

        return language_counts, language_average_confidence
    
    async def translate_bulk(self):
        async with Translator() as translator:
            translations = []
            for word in tqdm(self.words, desc="Translating", unit="word"):
                translation = await translator.translate(word, src=self.src_lang, dest=self.dest_lang)
                translations.append((translation.origin, translation.text))
            return translations

    def save_to_csv(self, translated_pairs, original_lang, trans_lang, csv_filename='out/trans.csv'):
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([f'Original({original_lang})', f'Translated({trans_lang})'])
                for original, translated in translated_pairs:
                    writer.writerow([original, translated])
        except Exception as e:
            print(f"Error saving CSV file: {e}")
