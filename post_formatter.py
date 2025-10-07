# post_formatter.py
import logging
from datetime import datetime
from typing import List, Dict
import re

logger = logging.getLogger(__name__)

class PostFormatter:
    def __init__(self):
        self.emoji_map = {
            'позитивный': '😊',
            'нейтральный': '😐', 
            'негативный': '😟'
        }
    
    def escape_markdown(self, text: str) -> str:
        """Экранирует специальные символы Markdown"""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    
    def format_structured_post(self, structured_content: Dict, source_channels: List[str]) -> str:
        """Форматирует структурированный пост для публикации"""
        
        if not structured_content['has_ai_analysis']:
            return self.format_fallback_post(structured_content['main_content'], source_channels)
        
        # Основной заголовок (без Markdown для надежности)
        post_parts = [f"🎯 {structured_content['main_topic'].upper()}\n"]
        
        # Основной контент
        if structured_content['main_content']:
            post_parts.append("📋 ОСНОВНОЕ:")
            for i, content in enumerate(structured_content['main_content'][:2], 1):
                # Экранируем текст
                safe_content = self.escape_markdown(content)
                post_parts.append(f"{i}. {safe_content}")
        
        # Инсайты из дискуссий
        if structured_content['discussion_insights']:
            post_parts.append("\n💭 ЧТО ДУМАЮТ ДРУГИЕ:")
            for insight in structured_content['discussion_insights']:
                emoji = self.emoji_map.get(insight['sentiment'], '😐')
                safe_text = self.escape_markdown(insight['text'])
                post_parts.append(f"• {emoji} {safe_text}")
        
        # Источники и время
        source_names = [ch.replace('@', '').replace('https://t.me/', '') for ch in source_channels[:2]]
        post_parts.append(f"\n📡 Источники: {', '.join(source_names)}")
        post_parts.append(f"🕒 Анализ выполнен: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        return '\n'.join(post_parts)
    
    def format_fallback_post(self, main_content: List[str], source_channels: List[str]) -> str:
        """Форматирует пост без AI-анализа"""
        post_parts = ["📢 СВЕЖИЕ НОВОСТИ\n"]
        
        for i, content in enumerate(main_content[:3], 1):
            safe_content = self.escape_markdown(content[:200])
            post_parts.append(f"{i}. {safe_content}{'...' if len(content) > 200 else ''}")
        
        source_names = [ch.replace('@', '').replace('https://t.me/', '') for ch in source_channels[:2]]
        post_parts.append(f"\n📡 Источники: {', '.join(source_names)}")
        post_parts.append(f"🕒 Опубликовано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        return '\n'.join(post_parts)