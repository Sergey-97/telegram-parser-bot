import os
import json
import requests
import re
from config import HUGGINGFACE_TOKEN

class AIProcessor:
    def __init__(self):
        self.api_key = HUGGINGFACE_TOKEN
        
    def analyze_marketplace(self, text, channel_url=""):
        """Анализирует текст и определяет маркетплейс с улучшенной логикой"""
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
            
        # Улучшенные паттерны для определения маркетплейсов по тексту
        ozon_patterns = [
            r'\bozon\b', r'\bозон\b', r'\bozon\s*marketplace', r'\bозон\s*маркетплейс',
            r'\bozon\s*seller', r'\bозон\s*продавец', r'\bozon\s*adv', r'\bозон\s*реклама',
            r'\bozon\s*travel', r'\bозон\s*путешествия', r'\bozon\s*card', r'\bозон\s*карта',
            r'\bоzon\b', r'\bOZON\b', r'\bOzon\b'
        ]
        
        wb_patterns = [
            r'\bwb\b', r'\bвб\b', r'\bwildberries\b', r'\bвайлдберриз\b', r'\bвалдберриз\b',
            r'\bwildberry\b', r'\bвб\s*seller', r'\bвб\s*продавец', r'\bwb\s*seller',
            r'\bwildberries\s*official', r'\bвб\s*официальный', r'\bподборки\s*wb',
            r'\bwildberries\s*marketplace', r'\bвб\s*маркетплейс', r'\bWB\b', r'\bWb\b'
        ]
        
        yandex_patterns = [
            r'\byandex\b', r'\bяндекс\b', r'\bяндекс\s*market', r'\bяндекс\s*маркет',
            r'\byandex\s*market', r'\bяндекс\s*доставка', r'\byandex\s*delivery',
            r'\bmarket\s*place', r'\bмаркет\s*плейс', r'\bYandex\b', r'\bYANDEX\b'
        ]
        
        # Проверяем OZON
        ozon_score = sum(1 for pattern in ozon_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if ozon_score > 0:
            return 'OZON'
        
        # Проверяем Wildberries
        wb_score = sum(1 for pattern in wb_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if wb_score > 0:
            return 'WB'
        
        # Проверяем Yandex Market
        yandex_score = sum(1 for pattern in yandex_patterns if re.search(pattern, text_lower, re.IGNORECASE))
        if yandex_score > 0:
            return 'YANDEX'
        
        return 'OTHER'

    def structure_content(self, source_texts, discussion_texts):
        """Структурирует контент для поста на основе реального парсинга"""
        try:
            # Объединяем все тексты для анализа
            all_content = source_texts + discussion_texts
            
            if not all_content:
                return self._create_fallback_structure([])

            # Анализируем тексты для подсчета по маркетплейсам
            marketplace_stats = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
            
            # Собираем ключевые темы для каждого маркетплейса
            ozon_themes = set()
            wb_themes = set()
            yandex_themes = set()
            
            for text in all_content:
                marketplace = self.analyze_marketplace(text)
                marketplace_stats[marketplace] += 1
                
                # Анализируем темы сообщений
                themes = self._extract_themes(text, marketplace)
                if marketplace == 'OZON':
                    ozon_themes.update(themes)
                elif marketplace == 'WB':
                    wb_themes.update(themes)
                elif marketplace == 'YANDEX':
                    yandex_themes.update(themes)

            # Если нет данных по маркетплейсам, создаем более релевантные темы
            if not ozon_themes and marketplace_stats['OZON'] > 0:
                ozon_themes = {
                    'Обновления платформы OZON',
                    'Логистические улучшения', 
                    'Новые инструменты для продавцов'
                }
                
            if not wb_themes and marketplace_stats['WB'] > 0:
                wb_themes = {
                    'Обновления Wildberries',
                    'Изменения в работе с продавцами',
                    'Оптимизация процессов'
                }

            return {
                'title': '📊 Аналитика маркетплейсов',
                'summary': f'Проанализировано {len(all_content)} сообщений. OZON: {marketplace_stats["OZON"]}, WB: {marketplace_stats["WB"]}, Yandex: {marketplace_stats["YANDEX"]}',
                'sections': {
                    'OZON': {
                        'key_points': list(ozon_themes)[:3] if ozon_themes else ['Обновления платформы OZON', 'Логистические улучшения'],
                        'important': ['Следите за обновлениями в личном кабинете'],
                        'tips': ['Регулярно проверяйте изменения в правилах площадки']
                    },
                    'WB': {
                        'key_points': list(wb_themes)[:3] if wb_themes else ['Обновления Wildberries', 'Изменения в работе с продавцами'],
                        'important': ['Внимание к изменениям регламентов'],
                        'tips': ['Адаптируйтесь к изменениям логистики']
                    },
                    'YANDEX': {
                        'key_points': list(yandex_themes)[:3] if yandex_themes else ['Развитие Яндекс Маркета', 'Новые функции для продавцов'],
                        'important': ['Отслеживайте новые функции площадки'],
                        'tips': ['Используйте все возможности продвижения']
                    }
                },
                'recommendations': 'Рекомендуется активное участие в профессиональных сообществах для получения актуальной информации.'
            }
                
        except Exception as e:
            print(f"❌ Ошибка структурирования контента: {e}")
            return self._create_fallback_structure(source_texts + discussion_texts)

    def _extract_themes(self, text, marketplace):
        """Извлекает ключевые темы из текста"""
        themes = set()
        text_lower = text.lower()
        
        # Общие темы для всех маркетплейсов
        common_themes = {
            'доставк': 'Обновления доставки',
            'логистик': 'Изменения в логистике',
            'тариф': 'Корректировки тарифов',
            'реклам': 'Обновления рекламных инструментов',
            'продвижен': 'Изменения в продвижении',
            'возврат': 'Политика возвратов',
            'выкуп': 'Процессы выкупа товаров',
            'брак': 'Работа с бракованным товаром',
            'карточк': 'Требования к карточкам товаров',
            'отзыв': 'Система отзывов',
            'рейтинг': 'Изменения в рейтингах',
            'акци': 'Акции и скидки',
            'распродаж': 'Периоды распродаж',
            'склад': 'Складские процессы',
            'аналитик': 'Инструменты аналитики',
            'модерац': 'Процессы модерации',
            'каталог': 'Обновления каталога',
            'поиск': 'Алгоритмы поиска',
            'скидк': 'Система скидок',
            'бонус': 'Бонусные программы'
        }
        
        for keyword, theme in common_themes.items():
            if keyword in text_lower:
                themes.add(theme)
        
        return themes

    def _create_fallback_structure(self, texts):
        """Создает резервную структуру в случае ошибки"""
        # Анализируем тексты для статистики
        marketplace_stats = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
        for text in texts:
            marketplace = self.analyze_marketplace(text)
            marketplace_stats[marketplace] += 1
            
        return {
            'title': '📊 Аналитика маркетплейсов',
            'summary': f'Проанализировано {len(texts)} сообщений. OZON: {marketplace_stats["OZON"]}, WB: {marketplace_stats["WB"]}, Yandex: {marketplace_stats["YANDEX"]}' if texts else 'Ежедневный обзор ключевых трендов и изменений',
            'sections': {
                'OZON': {
                    'key_points': ['Обновления платформы для продавцов', 'Оптимизация логистических процессов'],
                    'important': ['Следите за изменениями в личном кабинете'],
                    'tips': ['Используйте все доступные инструменты аналитики']
                },
                'WB': {
                    'key_points': ['Изменения в работе с возвратами', 'Обновления алгоритмов выдачи'],
                    'important': ['Внимание к обновлениям регламентов'],
                    'tips': ['Регулярно мониторьте статистику продаж']
                },
                'YANDEX': {
                    'key_points': ['Развитие платформы Яндекс Маркет', 'Новые инструменты для продавцов'],
                    'important': ['Отслеживайте новые функции площадки'],
                    'tips': ['Используйте все возможности продвижения']
                }
            },
            'recommendations': 'Следите за официальными объявлениями маркетплейсов и участвуйте в профессиональных сообществах.'
        }