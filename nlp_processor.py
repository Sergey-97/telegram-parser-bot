from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from config import SUMMARY_MODEL, COMMENT_MODEL
import re

class NLPProcessor:
    def __init__(self):
        self.summarizer = None
        self.comment_analyzer = None
        self.tokenizer = None
        
    def load_models(self):
        """Загружает NLP модели"""
        try:
            # Модель для суммаризации
            self.summarizer = pipeline(
                "summarization",
                model=SUMMARY_MODEL,
                tokenizer=SUMMARY_MODEL,
                device=-1  # Используем CPU (бесплатно)
            )
            
            # Модель для анализа тональности/комментариев
            self.comment_analyzer = pipeline(
                "text-classification",
                model=COMMENT_MODEL,
                device=-1
            )
            
            print("NLP модели загружены успешно")
            
        except Exception as e:
            print(f"Ошибка при загрузке моделей: {e}")
    
    def summarize_text(self, text, max_length=150, min_length=30):
        """Суммаризирует текст"""
        if not self.summarizer:
            self.load_models()
            
        try:
            # Ограничиваем длину текста для обработки
            if len(text) > 1024:
                text = text[:1024]
                
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            print(f"Ошибка при суммаризации: {e}")
            return text[:200] + "..."  # Возвращаем обрезанный текст в случае ошибки
    
    def analyze_discussion_tone(self, texts):
        """Анализирует тональность обсуждений"""
        if not self.comment_analyzer:
            self.load_models()
            
        try:
            sentiments = []
            for text in texts[:10]:  # Анализируем первые 10 текстов
                if len(text) > 512:
                    text = text[:512]
                    
                result = self.comment_analyzer(text)
                sentiments.append(result[0])
                
            # Определяем преобладающую тональность
            positive_count = sum(1 for s in sentiments if s['label'] == 'LABEL_1')
            negative_count = sum(1 for s in sentiments if s['label'] == 'LABEL_0')
            
            if positive_count > negative_count:
                return "В основном положительные"
            elif negative_count > positive_count:
                return "В основном отрицательные"
            else:
                return "Смешанные"
                
        except Exception as e:
            print(f"Ошибка при анализе тональности: {e}")
            return "Не удалось определить"
    
    def process_posts(self, main_posts, discussion_posts):
        """Обрабатывает посты и создает финальный контент"""
        if not main_posts:
            return "Нет новых постов для обработки"
        
        # Суммаризируем основные посты
        summarized_content = []
        for post in main_posts[:5]:  # Берем 5 самых свежих постов
            summary = self.summarize_text(post.text)
            summarized_content.append(f"• {summary}")
        
        # Анализируем обсуждения
        discussion_texts = [post.text for post in discussion_posts]
        tone = self.analyze_discussion_tone(discussion_texts)
        
        # Формируем финальный пост
        final_post = "📊 **Еженедельный обзор новостей**\n\n"
        final_post += "**Основные события:**\n"
        final_post += "\n".join(summarized_content)
        final_post += f"\n\n💭 **Общественное мнение:** {tone}\n"
        final_post += f"\n📅 Период: последние {len(main_posts)} дней\n"
        final_post += "#обзор #новости #аналитика"
        
        return final_post