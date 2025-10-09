# ai_processor.py
import logging
import re
from typing import List, Dict
import config

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        self.keywords = {
            'акции': ['скидк', 'распродаж', 'акци', 'бонус', 'промокод', '%'],
            'новости': ['запуск', 'обновлен', 'новый', 'анонс', 'релиз'],
            'доставка': ['доставк', 'отправк', 'получен', 'курьер', 'пункт выдачи'],
            'маркетплейс': ['ozon', 'wildberries', 'яндекс маркет']
        }
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'[^\w\s\.\!\?,:;-а-яА-Я]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def detect_marketplace(self, text: str) -> str:
        """Определяет маркетплейс для текста"""
        text_lower = text.lower()
        
        for marketplace, keywords in config.MARKETPLACE_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return marketplace
        
        return 'other'
    
    def group_by_marketplace(self, messages: List[Dict]) -> Dict[str, List[str]]:
        """Группирует сообщения по маркетплейсам"""
        grouped = {'OZON': [], 'WB': [], 'other': []}
        
        for msg in messages:
            if isinstance(msg, dict):
                text = msg['text']
                marketplace = msg.get('marketplace', self.detect_marketplace(text))
            else:
                text = msg
                marketplace = self.detect_marketplace(text)
            
            grouped[marketplace].append(text)
        
        return grouped
    
    def summarize_text(self, text: str) -> str:
        clean_text = self.clean_text(text)
        sentences = re.split(r'[.!?]+', clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= 2:
            return clean_text
        
        important_sentences = []
        if sentences:
            important_sentences.append(sentences[0])
        
        key_phrases = ['новый', 'запуск', 'скидк', 'акци', 'важно']
        for sentence in sentences[1:]:
            if any(phrase in sentence.lower() for phrase in key_phrases):
                if sentence not in important_sentences:
                    important_sentences.append(sentence)
                    if len(important_sentences) >= 2:
                        break
        
        if len(important_sentences) < 2 and len(sentences) > 1:
            important_sentences.append(sentences[-1])
        
        result = '. '.join(important_sentences[:2])
        return result if len(result) > 20 else clean_text[:200] + "..."
    
    def analyze_sentiment(self, text: str) -> str:
        positive = ['отличн', 'хорош', 'успех', 'прекрасн', 'рекоменд', 'доволен', 'супер']
        negative = ['проблем', 'ошибк', 'плох', 'сложн', 'неудобн', 'ужасн']
        
        text_lower = text.lower()
        pos = sum(1 for word in positive if word in text_lower)
        neg = sum(1 for word in negative if word in text_lower)
        
        if pos > neg:
            return 'позитивный'
        elif neg > pos:
            return 'негативный'
        else:
            return 'нейтральный'
    
    def extract_topic(self, text: str) -> str:
        text_lower = text.lower()
        for topic, keywords in self.keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        return 'новости'
    
    def structure_content_by_marketplace(self, main_posts: List[Dict], discussion_posts: List[Dict]) -> Dict:
        """Структурирует контент с разделением по маркетплейсам"""
        logger.info("🧠 Обработка контента с разделением по маркетплейсам...")
        
        try:
            # Группируем по маркетплейсам
            main_grouped = self.group_by_marketplace(main_posts)
            discussion_grouped = self.group_by_marketplace(discussion_posts)
            
            structured_content = {}
            
            # Обрабатываем каждый маркетплейс отдельно
            for marketplace in ['OZON', 'WB']:
                marketplace_main = main_grouped[marketplace]
                marketplace_discussion = discussion_grouped[marketplace]
                
                if not marketplace_main:
                    continue
                
                main_summaries = []
                main_topics = set()
                
                for post in marketplace_main[:3]:
                    if len(post.strip()) > 20:
                        summary = self.summarize_text(post)
                        topic = self.extract_topic(post)
                        main_summaries.append(summary)
                        main_topics.add(topic)
                
                discussion_insights = []
                for post in marketplace_discussion[:5]:
                    if len(post.strip()) > 20:
                        sentiment = self.analyze_sentiment(post)
                        summary = self.summarize_text(post)
                        discussion_insights.append({
                            'text': summary,
                            'sentiment': sentiment
                        })
                        if len(discussion_insights) >= 2:
                            break
                
                structured_content[marketplace] = {
                    'main_topic': ' | '.join(list(main_topics)[:2]) if main_topics else 'новости',
                    'main_content': main_summaries,
                    'discussion_insights': discussion_insights,
                    'has_ai_analysis': len(main_summaries) > 0,
                    'message_count': len(marketplace_main)
                }
            
            return structured_content
            
        except Exception as e:
            logger.error(f"Ошибка обработки: {e}")
            return {}