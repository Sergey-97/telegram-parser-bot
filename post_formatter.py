import json
from datetime import datetime

class PostFormatter:
    def __init__(self):
        self.current_date = datetime.now().strftime("%d.%m.%Y")
    
    def format_structured_post(self, structured_content):
        """Форматирует структурированный контент в готовый пост"""
        try:
            # Если это строка, пытаемся распарсить
            if isinstance(structured_content, str):
                try:
                    structured_content = json.loads(structured_content)
                except json.JSONDecodeError:
                    return self._create_simple_post(structured_content)
            
            # Если это словарь
            if isinstance(structured_content, dict):
                return self._format_from_dict(structured_content)
            else:
                return self._create_simple_post(str(structured_content))
                
        except Exception as e:
            print(f"❌ Ошибка форматирования: {e}")
            return self._create_fallback_post()

    def _format_from_dict(self, data):
        """Форматирует пост из словаря"""
        lines = []
        
        # Заголовок
        title = data.get('title', f'📊 Аналитика маркетплейсов {self.current_date}')
        lines.append(f"**{title}**")
        lines.append("")
        
        # Резюме
        summary = data.get('summary', 'Ежедневный обзор ключевых изменений')
        lines.append(summary)
        lines.append("")
        
        # Секции
        sections = data.get('sections', {})
        
        for marketplace, content in sections.items():
            if marketplace == 'OTHER':
                continue
                
            lines.append(f"**{self._get_marketplace_emoji(marketplace)} {marketplace}**")
            
            # Ключевые моменты
            key_points = content.get('key_points', [])
            if key_points:
                if isinstance(key_points, list):
                    for point in key_points[:3]:
                        lines.append(f"• {point}")
                else:
                    lines.append(f"• {key_points}")
            
            # Важные изменения
            important = content.get('important', [])
            if important:
                lines.append("")
                lines.append("💡 **Важно:**")
                if isinstance(important, list):
                    for item in important[:2]:
                        lines.append(f"▪️ {item}")
                else:
                    lines.append(f"▪️ {important}")
            
            # Советы
            tips = content.get('tips', [])
            if tips:
                lines.append("")
                lines.append("👥 **Советы:**")
                if isinstance(tips, list):
                    for tip in tips[:2]:
                        lines.append(f"▫️ {tip}")
                else:
                    lines.append(f"▫️ {tips}")
            
            lines.append("")
        
        # Рекомендации
        recommendations = data.get('recommendations', '')
        if recommendations:
            lines.append("🎯 **Рекомендации:**")
            lines.append(recommendations)
            lines.append("")
        
        # Хештеги
        lines.append("#аналитика #маркетплейсы #OZON #WB #новости")
        
        return "\n".join(lines)

    def _get_marketplace_emoji(self, marketplace):
        """Возвращает эмодзи для маркетплейса"""
        emoji_map = {
            'OZON': '🟠',
            'WB': '🔵', 
            'YANDEX': '🟡',
            'OTHER': '⚪'
        }
        return emoji_map.get(marketplace, '🔹')

    def _create_simple_post(self, content):
        """Создает простой пост из строки"""
        return f"""📊 Аналитика маркетплейсов {self.current_date}

{content}

#аналитика #маркетплейсы #OZON #WB"""

    def _create_fallback_post(self):
        """Создает резервный пост"""
        return f"""📊 Аналитика маркетплейсов {self.current_date}

🟠 **OZON**
• Обновления платформы для продавцов
• Изменения в логистических процессах

🔵 **WB**
• Оптимизация процессов выкупа
• Обновления в работе с возвратами

🎯 **Рекомендации:** Следите за официальными объявлениями маркетплейсов

#аналитика #маркетплейсы #OZON #WB #новости"""