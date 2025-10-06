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
            
            # Используем официальный клиент для суммаризации с правильными параметрами
            summary = self.client.summarization(
                clean_text,
                parameters={
                    'max_length': 150,
                    'min_length': 30,
                    'do_sample': False
                }
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
                text[:512]  # Ограничиваем длину
            )  # Модель по умолчанию для sentiment analysis
            
            if result and len(result) > 0:
                # Берем предсказание с наибольшей вероятностью
                top_label = result[0]
                label_map = {
                    'LABEL_0': 'негативный',
                    'LABEL_1': 'нейтральный', 
                    'LABEL_2': 'позитивный',
                    'NEGATIVE': 'негативный',
                    'POSITIVE': 'позитивный'
                }
                return label_map.get(top_label['label'], 'нейтральный')
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
        
        # Fallback на простой анализ
        return self.simple_sentiment(text)
    
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
        result = '. '.join(key_sentences[:3]) + '.'
        if len(result) > 400:
            result = result[:397] + '...'
        
        return result
    
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
                        if len(discussion_insights) >= 3:  # Максимум 3 инсайта
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

# Тест финального процессора
def test_final_processor():
    processor = AIProcessorFinal()
    
    test_posts = [
        "Ozon запускает новую программу лояльности для продавцов. Теперь участники маркетплейса смогут получать дополнительные бонусы за объем продаж и положительные отзывы. Программа начнет работать с следующего месяца и включает в себя специальные условия для новых продавцов.",
        "Скидки до 50% на электронику в этом месяце! Успейте приобрести смартфоны, ноутбуки и планшеты по выгодным ценам. Акция действует до конца месяца. Только для зарегистрированных пользователей.",
        "Wildberries улучшает систему доставки: теперь доступна бесплатная доставка заказов от 1000 рублей. Также добавлены новые пункты выдачи в Москве и Санкт-Петербурге. Это сделает процесс получения товаров еще удобнее для покупателей."
    ]
    
    discussion_posts = [
        "Отличная новость про Ozon! Я как продавец очень доволен новыми условиями программы лояльности. Это мотивирует развивать бизнес на платформе.",
        "Скидки на электронику просто супер! Уже присмотрел себе новый ноутбук по отличной цене. Жду не дождусь начала акции!",
        "Были небольшие проблемы с доставкой на Wildberries, но в целом сервис становится лучше. Новые пункты выдачи - это удобно!",
        "Ozon постоянно развивается, это радует. Новые программы для продавцов помогают расти вместе с маркетплейсом."
    ]
    
    print("🧠 ФИНАЛЬНЫЙ AI ПРОЦЕССОР С ИСПРАВЛЕННЫМИ ПАРАМЕТРАМИ")
    print("=" * 60)
    
    # Тест суммаризации
    print("\n📊 ТЕСТ СУММАРИЗАЦИИ:")
    for i, post in enumerate(test_posts, 1):
        summary = processor.summarize_text(post)
        sentiment = processor.analyze_sentiment(post)
        topic = processor.extract_topic(post)
        
        print(f"\n📝 Пример {i} ({topic.upper()}, {sentiment}):")
        print(f"Оригинал: {post[:120]}...")
        print(f"📋 AI-суммаризация: {summary}")
    
    # Тест структурирования
    print(f"\n🎯 ТЕСТ ПОЛНОГО СТРУКТУРИРОВАНИЯ:")
    print("Собираем и структурируем контент...")
    
    structured = processor.structure_content(test_posts, discussion_posts)
    
    print(f"\n📈 РЕЗУЛЬТАТ СТРУКТУРИРОВАНИЯ:")
    print(f"🏷️  Основная тема: {structured['main_topic']}")
    print(f"📋 Основных постов: {len(structured['main_content'])}")
    print(f"💭 Инсайтов: {len(structured['discussion_insights'])}")
    
    print(f"\n📰 ОСНОВНОЙ КОНТЕНТ:")
    for i, content in enumerate(structured['main_content'], 1):
        print(f"  {i}. {content}")
    
    if structured['discussion_insights']:
        print(f"\n👥 ЧТО ДУМАЮТ ДРУГИЕ:")
        for insight in structured['discussion_insights']:
            emoji = "😊" if insight['sentiment'] == 'позитивный' else "😐" if insight['sentiment'] == 'нейтральный' else "😟"
            print(f"  {emoji} {insight['text']}")

if __name__ == "__main__":
    test_final_processor()