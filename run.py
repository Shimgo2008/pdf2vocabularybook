import asyncio
import os
from pdf2csv import PDFProcessor
from translate import TranslatorProcessor

def main():
    pdf_path = os.environ["PDF_PATH"]

    # PDF処理
    pdf_processor = PDFProcessor(pdf_path)
    text = pdf_processor.extract_text_from_pdf()
    cleaned_text = pdf_processor.clean_text(text)
    top_words = pdf_processor.get_most_common_words(cleaned_text)

    # CSVに保存
    pdf_processor.save_to_csv(top_words, 2)
    
    # CSVから単語を抽出
    words = pdf_processor.extract_keys_from_csv('out/word_frequencies.csv')

    # 翻訳処理
    trans_lang = "ja"
    translator_processor = TranslatorProcessor(words, src_lang="en", dest_lang=trans_lang)
    
    # 言語解析
    language_counts, language_average_confidence = asyncio.run(translator_processor.analyze_language_data(words))
    print("Language counts:")
    total_words = len(words)
    for lang, count in language_counts.items():
        print(f"{lang}: {count}/{total_words} ({(count/total_words)*100:.2f}%)")
    
    print("\nAccuracy (Confidence):")
    for lang, avg_conf in language_average_confidence.items():
        print(f"{lang}: {avg_conf*100:.3f}%")
    
    # 最も多い言語を出力
    most_common_language = max(language_counts, key=language_counts.get)
    print(f"\nMost common language: {most_common_language}")

    # 翻訳
    trans_list = asyncio.run(translator_processor.translate_bulk())
    
    # 翻訳結果をCSVに保存
    translator_processor.save_to_csv(trans_list, original_lang="en", trans_lang=trans_lang)

if __name__ == '__main__':
    main()
