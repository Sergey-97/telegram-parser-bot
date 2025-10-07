# ai_processor_final.py
import logging
import re
from typing import List, Dict
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIProcessorFinal:
    def __init__(self):
        # Используем официальный InferenceClient
        self.client = InferenceClient(
            token=os.getenv('HUGGINGFACE_TOKEN')
        )
        
    def summarize_text(self, text: str) -> str:
        """Суммаризирует текст через официальный Hugging Face API"""
        try:
            clean_text = self.clean_text(text)
            
            # Для очень коротких текстов возвращаем как есть
            if len(clean_text.split()) < 15:
                return clean_text
            
            # Используем официальный клиент для суммаризации с правильным синтаксисом
            summary = self.client.summarization(clean_text)
            
            if hasattr(summary, 'summary_text'):
                return summary.summary_text
            else:
                # Fallback на локальную логику
                return self.simple_summarize(clean_text)
                
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self.simple_summarize(text)
    
    def simple_summarize(self, text: str) -> str:
        """Умная локальная суммаризация"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= 2:
            return text
        
        # Эвристики для лучшей суммаризации
        key_sentences = []
        
        # 1. Первое предложение (обычно введение)
        if sentences:
            key_sentences.append(sentences[0])
        
        # 2. Предложения с ключевыми словами
        key_words = ['новый', 'запуск', 'скидк', 'акци', 'важно', 'изменен', 'улучшени']
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in key_words):
                if sentence not in key_sentences:
                    key_sentences.append(sentence)
                    if len(key_sentences) >= 2:  # Максимум 2 ключевых предложения
                        break
        
        # 3. Если мало ключевых, добавляем последнее
        if len(key_sentences) < 2 and len(sentences) > 1:
            key_sentences.append(sentences[-1])
        
        # Ограничиваем длину
        result = '. '.join(key_sentences[:3])
        if len(result) > 400:
            result = result[:397] + '...'
        
        return result
    
    def analyze_sentiment(self, text: str) -> str:
        """Анализирует тональность текста"""
        return self.simple_sentiment(text)
    
    def simple_sentiment(self, text: str) -> str:
        """Простой анализ тональности"""
        positive_words = ['отличн', 'хорош', 'успех', 'прекрасн', 'рекоменд', 'доволен', 'супер', 'замечательн']
        negative_words = ['проблем', 'ошибк', 'плох', 'сложн', 'неудобн', 'ужасн', 'разочарован']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'позитивный'
        elif neg_count > pos_count:
            return 'негативный'
        else:
            return 'нейтральный'
    
    def extract_topic(self, text: str) -> str:
        """Извлекает тему текста"""
        topics = {
            'акции': ['скидк', 'распродаж', 'акци', 'бонус', 'промокод', '%'],
            'новости': ['запуск', 'обновлен', 'новый', 'анонс', 'релиз', 'представляем'],
            'партнерство': ['партнер', 'сотрудничество', 'интеграция', 'объединение'],
            'доставка': ['доставк', 'отправк', 'получен', 'курьер', 'пункт выдачи'],
            'маркетплейс': ['ozon', 'wildberries', 'яндекс маркет', 'marketplace']
        }
        
        text_lower = text.lower()
        for topic, keywords in topics.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return 'новости'
    
    def clean_text(self, text: str) -> str:
        """Очищает текст"""
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[@#]\w+', '', text)
        text = re.sub(r'[^\w\s\.\!\?,:;-]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def structure_content(self, main_posts: List[str], discussion_posts: List[str]) -> Dict:
        """Структурирует контент с помощью AI"""
        logger.info("🧠 AI структурирование контента...")
        
        try:
            main_summaries = []
            main_topics = set()
            
            # Обрабатываем основные посты
            for post in main_posts[:3]:
                if len(post.strip()) > 20:
                    summary = self.summarize_text(post)
                    topic = self.extract_topic(post)
                    main_summaries.append(summary)
                    main_topics.add(topic)
            
            # Обрабатываем дискуссионные посты по теме
            discussion_insights = []
            for post in discussion_posts:
                if len(post.strip()) > 20:
                    post_topic = self.extract_topic(post)
                    # Добавляем только релевантные посты
                    if any(topic in post_topic for topic in main_topics) or not main_topics:
                        sentiment = self.analyze_sentiment(post)
                        summary = self.summarize_text(post)
                        discussion_insights.append({
                            'text': summary,
                            'sentiment': sentiment
                        })
                        if len(discussion_insights) >= 2:  # Максимум 2 инсайта
                            break
            
            return {
                'main_topic': ' | '.join(list(main_topics)[:2]) if main_topics else 'новости',
                'main_content': main_summaries,
                'discussion_insights': discussion_insights,
                'has_ai_analysis': len(main_summaries) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка структурирования: {e}")
            return {
                'main_topic': 'новости',
                'main_content': [self.simple_summarize(post) for post in main_posts[:2]],
                'discussion_insights': [],
                'has_ai_analysis': False
            }