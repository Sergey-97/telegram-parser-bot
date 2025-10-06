# ai_processor_fixed.py
import logging
import re
from typing import List, Dict
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIProcessorFixed:
    def __init__(self):
        # Используем официальный InferenceClient
        self.client = InferenceClient(
            token=os.getenv('HUGGINGFACE_TOKEN')
        )
        
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """Суммаризирует текст через официальный Hugging Face API"""
        try:
            clean_text = self.clean_text(text)
            
            # Для очень коротких текстов возвращаем как есть
            if len(clean_text.split()) < 15:
                return clean_text
            
            # Используем официальный клиент для суммаризации
            summary = self.client.summarization(
                clean_text,
                max_length=max_length,
                min_length=30,
                do_sample=False
            )
            
            if hasattr(summary, 'summary_text'):
                return summary.summary_text
            else:
                # Fallback на локальную логику
                return self.simple_summarize(clean_text)
                
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self.simple_summarize(text)
    
    def analyze_sentiment(self, text: str) -> str:
        """Анализирует тональность текста"""
        try:
            # Используем модель для анализа sentiment
            result = self.client.text_classification(
                text[:512],  # Ограничиваем длину
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            if result and len(result) > 0:
                # Берем предсказание с наибольшей вероятностью
                top_label = result[0]
                label_map = {
                    'LABEL_0': 'негативный',
                    'LABEL_1': 'нейтральный', 
                    'LABEL_2': 'позитивный'
                }
                return label_map.get(top_label['label'], 'нейтральный')
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
        
        # Fallback на простой анализ
        return self.simple_sentiment(text)
    
    def simple_summarize(self, text: str) -> str:
        """Простая локальная суммаризация"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= 2:
            return text
        
        # Берем первое и последнее предложение
        if len(sentences) >= 3:
            return f"{sentences[0]}. {sentences[-1]}."
        else:
            return sentences[0] + '.'
    
    def simple_sentiment(self, text: str) -> str:
        """Простой анализ тональности"""
        positive_words = ['отличн', 'хорош', 'успех', 'прекрасн', 'рекоменд', 'доволен', 'супер']
        negative_words = ['проблем', 'ошибк', 'плох', 'сложн', 'неудобн', 'ужасн']
        
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
            'акции': ['скидк', 'распродаж', 'акци', 'бонус', 'промокод'],
            'новости': ['запуск', 'обновлен', 'новый', 'анонс', 'релиз'],
            'партнерство': ['партнер', 'сотрудничество', 'интеграция'],
            'доставка': ['доставк', 'отправк', 'получен', 'курьер']
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
                    logger.info(f"✅ Обработан основной пост: {topic}")
            
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
                        logger.info(f"✅ Добавлен инсайт: {sentiment}")
            
            return {
                'main_topic': ' | '.join(list(main_topics)[:2]) if main_topics else 'новости',
                'main_content': main_summaries,
                'discussion_insights': discussion_insights[:3],
                'has_ai_analysis': len(main_summaries) > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка структурирования: {e}")
            return {
                'main_topic': 'новости',
                'main_content': main_posts[:2],
                'discussion_insights': [],
                'has_ai_analysis': False
            }

# Тест исправленного процессора
def test_fixed_processor():
    processor = AIProcessorFixed()
    
    test_posts = [
        "Ozon запускает новую программу лояльности для продавцов. Теперь участники маркетплейса смогут получать дополнительные бонусы за объем продаж и положительные отзывы. Программа начнет работать с следующего месяца.",
        "Скидки до 50% на электронику в этом месяце! Успейте приобрести смартфоны, ноутбуки и планшеты по выгодным ценам. Акция действует до конца месяца.",
        "Wildberries улучшает систему доставки: теперь доступна бесплатная доставка заказов от 1000 рублей. Также добавлены новые пункты выдачи в Москве и Санкт-Петербурге."
    ]
    
    discussion_posts = [
        "Отличная новость про Ozon! Я как продавец очень доволен новыми условиями программы лояльности.",
        "Скидки на электронику просто супер! Уже присмотрел себе новый ноутбук по отличной цене.",
        "Были небольшие проблемы с доставкой на Wildberries, но в целом сервис становится лучше."
    ]
    
    print("🧠 ТЕСТ ИСПРАВЛЕННОГО AI ПРОЦЕССОРА")
    print("=" * 50)
    
    # Тест суммаризации
    for i, post in enumerate(test_posts, 1):
        summary = processor.summarize_text(post)
        sentiment = processor.analyze_sentiment(post)
        topic = processor.extract_topic(post)
        
        print(f"\n📝 Пример {i} ({topic}, {sentiment}):")
        print(f"Оригинал: {post[:100]}...")
        print(f"📋 AI-суммаризация: {summary}")
    
    # Тест структурирования
    print(f"\n🎯 ТЕСТ СТРУКТУРИРОВАНИЯ:")
    structured = processor.structure_content(test_posts, discussion_posts)
    
    print(f"Тема: {structured['main_topic']}")
    print(f"Основной контент: {len(structured['main_content'])} постов")
    print(f"Инсайты: {len(structured['discussion_insights'])} комментариев")
    
    for insight in structured['discussion_insights']:
        print(f"  - {insight['sentiment']}: {insight['text']}")

if __name__ == "__main__":
    test_fixed_processor()