# post_formatter.py
import logging
from typing import List, Dict
import config

logger = logging.getLogger(__name__)

class PostFormatter:
    def __init__(self):
        self.emoji_map = {
            'позитивный': '😊',
            'нейтральный': '😐', 
            'негативный': '😟'
        }
        self.marketplace_emojis = {
            'OZON': '🟠',
            'WB': '🔵'
        }
    
    def format_marketplace_post(self, marketplace: str, content: Dict, source_channels: List[str]) -> str:
        """Форматирует пост для конкретного маркетплейса"""
        if not content['has_ai_analysis']:
            return ""
        
        post_parts = []
        emoji = self.marketplace_emojis.get(marketplace, '⚪')
        
        # Заголовок маркетплейса
        post_parts.append(f"{emoji} **{marketplace}**")
        
        # Основной контент
        if content['main_content']:
            post_parts.append("\n📋 **ОСНОВНОЕ:**")
            for i, item in enumerate(content['main_content'][:2], 1):
                post_parts.append(f"{i}. {item}")
        
        # Комментарии
        if content['discussion_insights']:
            post_parts.append("\n💭 **МНЕНИЯ:**")
            for insight in content['discussion_insights']:
                sentiment_emoji = self.emoji_map.get(insight['sentiment'], '😐')
                post_parts.append(f"• {sentiment_emoji} {insight['text']}")
        
        return '\n'.join(post_parts)
    
    def format_structured_post(self, structured_content: Dict, source_channels: List[str]) -> str:
        """Форматирует общий пост с разделением по маркетплейсам"""
        
        post_parts = ["🚀 **СВЕЖИЕ НОВОСТИ МАРКЕТПЛЕЙСОВ**\n"]
        
        # Добавляем посты для каждого маркетплейса
        for marketplace in ['OZON', 'WB']:
            if marketplace in structured_content and structured_content[marketplace]['has_ai_analysis']:
                marketplace_post = self.format_marketplace_post(marketplace, structured_content[marketplace], source_channels)
                if marketplace_post:
                    post_parts.append(marketplace_post)
                    post_parts.append("")  # Пустая строка между маркетплейсами
        
        # Убираем последнюю пустую строку
        if post_parts and post_parts[-1] == "":
            post_parts.pop()
        
        # Источники
        if source_channels:
            source_names = [ch.replace('@', '').replace('https://t.me/', '') for ch in source_channels[:3]]
            post_parts.append(f"\n📡 **Источники:** {', '.join(source_names)}")
        
        # Статистика
        total_messages = sum(content.get('message_count', 0) for content in structured_content.values())
        if total_messages > 0:
            post_parts.append(f"📊 **Обработано сообщений:** {total_messages}")
        
        return '\n'.join(post_parts)
    
    def format_simple_post(self, main_content: List[str], source_channels: List[str]) -> str:
        """Простой формат поста (резервный)"""
        post_parts = ["📢 **СВЕЖИЕ НОВОСТИ**\n"]
        
        for i, content in enumerate(main_content[:3], 1):
            clean_content = content[:200] + '...' if len(content) > 200 else content
            post_parts.append(f"{i}. {clean_content}")
        
        if source_channels:
            source_names = [ch.replace('@', '').replace('https://t.me/', '') for ch in source_channels[:2]]
            post_parts.append(f"\n📡 **Источники:** {', '.join(source_names)}")
        
        return '\n'.join(post_parts)