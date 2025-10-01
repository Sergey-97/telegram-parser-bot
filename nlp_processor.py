from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from config import SUMMARY_MODEL, COMMENT_MODEL, PROCESSING_BATCH_SIZE
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        self.summarizer = None
        self.comment_analyzer = None
        self.models_loaded = False
        
    def load_models(self):
        """Загружает NLP модели"""
        if self.models_loaded:
            return
            
        try:
            logger.info("Загружаем NLP модели...")
            
            # Модель для суммаризации
            self.summarizer = pipeline(
                "summarization",
                model=SUMMARY_MODEL,
                tokenizer=SUMMARY_MODEL,
                device=-1,  # Используем CPU
                torch_dtype=torch.float32
            )
            
            # Модель для анализа тональности
            self.comment_analyzer = pipeline(
                "text-classification",
                model=COMMENT_MODEL,
                device=-1
            )
            
            self.models_loaded = True
            logger.info("NLP модели успешно загружены")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке моделей: {e}")
            # Создаем заглушки для продолжения работы
            self.models_loaded = False
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """Суммаризирует текст"""
        if not self.models_loaded:
            self.load_models()
            
        if not self.summarizer:
            # Возвращаем обрезанный текст если модель не загружена
            return text[:200] + "..." if len(text) > 200 else text
            
        try:
            # Ограничиваем длину текста для обработки
            if len(text) > 1024:
                text = text[:1024]
                
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Ошибка при суммаризации: {e}")
            return text[:200] + "..."  # Возвращаем обрезанный текст в случае ошибки
    
    def analyze_discussion_tone(self, texts: List[str]) -> str:
        """Анализирует тональность обсуждений"""
        if not self.models_loaded:
            self.load_models()
            
        if not self.comment_analyzer or not texts:
            return "Не удалось определить"
            
        try:
            sentiments = []
            # Анализируем только первые N текстов для экономии ресурсов
            for text in texts[:PROCESSING_BATCH_SIZE]:
                if len(text) > 512:
                    text = text[:512]
                    
                result = self.comment_analyzer(text)
                sentiments.append(result[0])
                
            # Анализируем результаты (зависит от модели)
            if sentiments and 'label' in sentiments[0]:
                # Для rubert-tiny2: LABEL_0 - негативный, LABEL_1 - позитивный
                positive_count = sum(1 for s in sentiments if s['label'] == 'LABEL_1')
                negative_count = sum(1 for s in sentiments if s['label'] == 'LABEL_0')
                
                total = len(sentiments)
                if total > 0:
                    positive_percent = (positive_count / total) * 100
                    
                    if positive_percent > 60:
                        return "📈 Преимущественно положительные"
                    elif positive_percent > 40:
                        return "📊 Смешанные настроения"
                    else:
                        return "📉 Преимущественно отрицательные"
            
            return "🤔 Нейтральные или смешанные"
                
        except Exception as e:
            logger.error(f"Ошибка при анализе тональности: {e}")
            return "Не удалось определить"
    
    def process_posts(self, main_posts, discussion_posts):
        """Обрабатывает посты и создает финальный контент"""
        if not main_posts:
            return "❌ Нет новых постов для обработки за указанный период."
        
        self.load_models()
        
        # Суммаризируем основные посты
        summarized_content = []
        logger.info(f"Обрабатываем {len(main_posts[:3])} основных постов...")
        
        for i, post in enumerate(main_posts[:3]):  # Берем 3 самых свежих поста
            logger.info(f"Суммаризируем пост {i+1}...")
            summary = self.summarize_text(post.text)
            summarized_content.append(f"• {summary}")
        
        # Анализируем обсуждения
        discussion_texts = [post.text for post in discussion_posts]
        tone = self.analyze_discussion_tone(discussion_texts)
        
        # Формируем финальный пост
        final_post = "📊 **Еженедельный обзор новостей**\n\n"
        final_post += "**🎯 Основные события:**\n"
        final_post += "\n".join(summarized_content)
        
        if discussion_posts:
            final_post += f"\n\n**💭 Общественное мнение:** {tone}\n"
            final_post += f"*На основе анализа {min(len(discussion_posts), PROCESSING_BATCH_SIZE)} обсуждений*"
        
        final_post += f"\n\n📅 **Период обзора:** последние {len(main_posts)} дней"
        final_post += "\n\n#обзор #новости #аналитика #автоматизация"
        
        logger.info("Пост успешно сформирован")
        return final_post