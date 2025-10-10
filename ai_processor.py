import logging

logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self):
        pass
        
    def analyze_marketplace(self, text, channel_url=""):
        """Анализирует текст и определяет маркетплейс"""
        if not text:
            return 'OTHER'
            
        text_lower = text.lower()
        channel_lower = channel_url.lower()
        
        # Определяем по URL канала
        if 'ozon' in channel_lower:
            return 'OZON'
        elif 'wb' in channel_lower or 'wildberr' in channel_lower:
            return 'WB'
        elif 'yandex' in channel_lower or 'market' in channel_lower:
            return 'YANDEX'
            
        # Определяем по тексту
        if 'ozon' in text_lower or 'озон' in text_lower:
            return 'OZON'
        elif 'wb' in text_lower or 'вб' in text_lower or 'wildberr' in text_lower:
            return 'WB'
        elif 'yandex' in text_lower or 'яндекс' in text_lower:
            return 'YANDEX'
        
        return 'OTHER'

    def structure_content(self, source_texts, discussion_texts):
        """Структурирует контент для поста"""
        try:
            # Объединяем все тексты
            all_content = source_texts + discussion_texts
            
            if not all_content:
                return self._create_fallback_structure([])

            # Анализируем тексты
            marketplace_stats = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
            
            for text in all_content:
                marketplace = self.analyze_marketplace(text)
                marketplace_stats[marketplace] += 1
            
            return {
                'title': '📊 Аналитика маркетплейсов',
                'summary': f'Проанализировано {len(all_content)} сообщений. OZON: {marketplace_stats["OZON"]}, WB: {marketplace_stats["WB"]}',
                'sections': {
                    'OZON': {
                        'key_points': ['Обновления платформы', 'Логистические улучшения'],
                        'important': ['Следите за обновлениями'],
                        'tips': ['Используйте инструменты аналитики']
                    },
                    'WB': {
                        'key_points': ['Оптимизация процессов', 'Обновления возвратов'],
                        'important': ['Внимание к регламентам'],
                        'tips': ['Мониторьте статистику']
                    }
                },
                'recommendations': 'Следите за официальными объявлениями'
            }
                
        except Exception as e:
            logger.error(f"❌ Ошибка структурирования: {e}")
            return self._create_fallback_structure(source_texts + discussion_texts)

    def _create_fallback_structure(self, texts):
        """Создает резервную структуру"""
        return {
            'title': '📊 Аналитика маркетплейсов',
            'summary': f'Ежедневный обзор на основе {len(texts)} сообщений' if texts else 'Обзор ключевых изменений',
            'sections': {
                'OZON': {
                    'key_points': ['Обновления платформы', 'Логистические процессы'],
                    'important': ['Проверьте настройки ЛК'],
                    'tips': ['Используйте аналитику']
                },
                'WB': {
                    'key_points': ['Процессы выкупа', 'Работа с возвратами'],
                    'important': ['Следите за регламентами'],
                    'tips': ['Анализируйте статистику']
                }
            },
            'recommendations': 'Участвуйте в профессиональных сообществах'
        }