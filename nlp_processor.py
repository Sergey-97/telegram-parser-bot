import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        self.models_loaded = False
        
    def load_models(self):
        """Заглушка для NLP моделей"""
        logger.info("NLP models disabled for initial deployment")
        self.models_loaded = True
    
    def summarize_text(self, text, max_length=150, min_length=30):
        """Упрощенная суммаризация"""
        if len(text) > 200:
            # Берем первые 100 символов и последние 50 для контекста
            return text[:100] + "..." + text[-50:]
        return text
    
    def extract_keywords(self, text, num_keywords=5):
        """Извлекает ключевые слова из текста (упрощенная версия)"""
        # Убираем стоп-слова и берем самые частые слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'о', 'для', 'не', 'что', 'это', 'как', 'а', 'но', 'или', 'из', 'у', 'к', 'же', 'за', 'вы', 'так', 'вот', 'от', 'бы', 'до', 'мы', 'то', 'был', 'ему', 'только', 'еще', 'мне', 'было', 'время', 'когда', 'даже', 'нет', 'если', 'они', 'ему', 'теперь', 'уже', 'ли', 'ее', 'может', 'после', 'над', 'без', 'тот', 'тем', 'чем', 'во', 'со', 'при', 'до', 'после', 'через', 'между'}
        words = text.lower().split()
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:num_keywords]
    
    def find_relevant_discussions(self, main_post_text, discussion_posts):
        """Находит обсуждения, релевантные основному посту"""
        main_keywords = self.extract_keywords(main_post_text)
        relevant_posts = []
        
        for post in discussion_posts:
            post_keywords = self.extract_keywords(post.text)
            # Проверяем пересечение ключевых слов
            common_keywords = set(main_keywords) & set(post_keywords)
            if len(common_keywords) >= 2:  # Если есть хотя бы 2 общих ключевых слова
                relevant_posts.append(post)
                
        return relevant_posts
    
    def analyze_discussion_tone(self, texts):
        """Упрощенный анализ тональности"""
        if not texts:
            return "Недостаточно данных для анализа"
            
        positive_words = {'хорошо', 'отлично', 'прекрасно', 'замечательно', 'супер', 'отличный', 'хороший', 'позитивный', 'рад', 'доволен', 'успех', 'победа', 'прогресс'}
        negative_words = {'плохо', 'ужасно', 'кошмар', 'проблема', 'ошибка', 'негативный', 'грустно', 'разочарован', 'провал', 'поражение', 'кризис'}
        
        positive_count = 0
        negative_count = 0
        
        for text in texts:
            text_lower = text.lower()
            for word in positive_words:
                if word in text_lower:
                    positive_count += 1
            for word in negative_words:
                if word in text_lower:
                    negative_count += 1
        
        total = positive_count + negative_count
        if total == 0:
            return "Нейтральные"
        
        positive_ratio = positive_count / total
        
        if positive_ratio > 0.6:
            return "📈 Преимущественно положительные"
        elif positive_ratio > 0.4:
            return "📊 Смешанные настроения"
        else:
            return "📉 Преимущественно отрицательные"
    
    def process_posts(self, main_posts, discussion_posts):
        """Обрабатывает посты и создает финальный контент"""
        if not main_posts:
            return "❌ Нет новых основных постов для обработки."
        
        # Берем только последние 3 основных поста
        recent_main_posts = main_posts[:3]
        
        summarized_content = []
        
        for i, post in enumerate(recent_main_posts):
            summary = self.summarize_text(post.text)
            
            # Находим релевантные обсуждения для этого поста
            relevant_discussions = self.find_relevant_discussions(post.text, discussion_posts)
            tone = self.analyze_discussion_tone([d.text for d in relevant_discussions[:5]])  # Берем до 5 релевантных
            
            summarized_content.append({
                'summary': summary,
                'tone': tone,
                'discussion_count': len(relevant_discussions)
            })
        
        # Формируем финальный пост
        final_post = "📊 **Ежедневный обзор новостей**\n\n"
        final_post += f"📅 *{datetime.now().strftime('%d.%m.%Y')}*\n\n"
        
        final_post += "**🎯 Основные события:**\n"
        for i, content in enumerate(summaried_content, 1):
            final_post += f"\n{i}. {content['summary']}\n"
            final_post += f"   💬 Настроения: {content['tone']} "
            final_post += f"({content['discussion_count']} обсуждений)\n"
        
        final_post += f"\n📊 **Статистика:**\n"
        final_post += f"• Обработано основных постов: {len(recent_main_posts)}\n"
        final_post += f"• Всего обсуждений: {len(discussion_posts)}\n"
        final_post += f"• Релевантных обсуждений: {sum(c['discussion_count'] for c in summarized_content)}\n"
        
        final_post += "\n#обзор #новости #аналитика #автоматизация"
        
        logger.info("Пост сформирован с релевантными обсуждениями")
        return final_post