import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

class PostFormatter:
    def __init__(self):
        self.emoji_map = {
            'позитивный': '😊',
            'нейтральный': '😐', 
            'негативный': '😟'
        }
    
    def format_structured_post(self, structured_content: Dict, source_channels: List[str]) -> str:
        """Форматирует структурированный пост для публикации"""
        
        if not structured_content['has_ai_analysis']:
            return self.format_fallback_post(structured_content['main_content'], source_channels)
        
        # Основной заголовок
        post_parts = [f"🎯 **{structured_content['main_topic'].upper()}**\n"]
        
        # Основной контент
        if structured_content['main_content']:
            post_parts.append("📋 **ОСНОВНОЕ:**")
            for i, content in enumerate(structured_content['main_content'][:2], 1):
                post_parts.append(f"{i}. {content}")
        
        # Инсайты из дискуссий
        if structured_content['discussion_insights']:
            post_parts.append("\n💭 **ЧТО ДУМАЮТ ДРУГИЕ:**")
            for insight in structured_content['discussion_insights']:
                emoji = self.emoji_map.get(insight['sentiment'], '😐')
                post_parts.append(f"• {emoji} {insight['text']}")
        
        # Источники и время
        post_parts.append(f"\n📡 _Источники: {', '.join([ch.split('/')[-1] for ch in source_channels[:2]])}_")
        post_parts.append(f"🕒 _Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}_")
        
        return '\n'.join(post_parts)
    
    def format_fallback_post(self, main_content: List[str], source_channels: List[str]) -> str:
        """Форматирует пост без AI-анализа"""
        post_parts = ["📢 **СВЕЖИЕ НОВОСТИ**\n"]
        
        for i, content in enumerate(main_content[:3], 1):
            post_parts.append(f"{i}. {content[:200]}{'...' if len(content) > 200 else ''}")
        
        post_parts.append(f"\n📡 _Источники: {', '.join([ch.split('/')[-1] for ch in source_channels[:2]])}_")
        post_parts.append(f"🕒 _Опубликовано: {datetime.now().strftime('%d.%m.%Y %H:%M')}_")
        
        return '\n'.join(post_parts)