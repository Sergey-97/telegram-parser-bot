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
        
        # Определяем по URL канала (приоритет)
        if 'ozon' in channel_lower or 'prodaemozon' in channel_lower:
            return 'OZON'
        elif 'wb' in channel_lower or 'wildberr' in channel_lower or 'prodaemwb' in channel_lower:
            return 'WB'
        elif 'yandex' in channel_lower or 'market' in channel_lower:
            return 'YANDEX'
        elif 'ozon_adv' in channel_lower:
            return 'OZON'
            
        # Улучшенные паттерны для текста
        ozon_keywords = [
            'ozon', 'озон', 'oзон', 'o-zon', 'озон.', 'озон,', 'озон!',
            'озона', 'озоне', 'озону', 'озоном', 'озоны',
            'oзон.', 'oзон,', 'oзон!', 'oзона', 'oзоне', 'oзону', 'oзоном'
        ]
        
        wb_keywords = [
            'wb', 'вб', 'wildberries', 'вайлдберриз', 'валдберриз', 'wildberry',
            'вб.', 'вб,', 'вб!', 'вб?', 'wb.', 'wb,', 'wb!', 'wb?',
            'wildberries.', 'wildberries,', 'wildberries!'
        ]
        
        yandex_keywords = [
            'yandex', 'яндекс', 'yandex.', 'yandex,', 'yandex!',
            'яндекс.', 'яндекс,', 'яндекс!', 'яндекс?',
            'яндекс.market', 'yandex market', 'яндекс маркет'
        ]
        
        # Проверяем ключевые слова в тексте
        ozon_matches = sum(1 for keyword in ozon_keywords if keyword in text_lower)
        wb_matches = sum(1 for keyword in wb_keywords if keyword in text_lower)
        yandex_matches = sum(1 for keyword in yandex_keywords if keyword in text_lower)
        
        if ozon_matches > wb_matches and ozon_matches > yandex_matches:
            return 'OZON'
        elif wb_matches > ozon_matches and wb_matches > yandex_matches:
            return 'WB'
        elif yandex_matches > ozon_matches and yandex_matches > wb_matches:
            return 'YANDEX'
        
        # Если нет явных указаний, проверяем контекст
        if any(word in text_lower for word in ['маркетплейс', 'marketplace', 'продавец', 'seller']):
            if any(word in text_lower for word in ['озон', 'ozon']):
                return 'OZON'
            elif any(word in text_lower for word in ['вб', 'wb', 'wildberr']):
                return 'WB'
            elif any(word in text_lower for word in ['яндекс', 'yandex']):
                return 'YANDEX'
        
        return 'OTHER'

    def structure_content(self, source_texts, discussion_texts):
        """Структурирует контент с улучшенной логикой"""
        try:
            # Объединяем все тексты для анализа
            all_content = source_texts + discussion_texts
            
            if not all_content:
                print("⚠️ Нет контента для анализа, использую резервные данные")
                return self._create_fallback_structure([])

            print(f"📝 Анализирую {len(all_content)} сообщений...")
            
            # Анализируем тексты для подсчета по маркетплейсам
            marketplace_stats = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
            
            # Собираем конкретные темы и ключевые фразы
            ozon_themes = []
            wb_themes = []
            yandex_themes = []
            
            for text in all_content:
                marketplace = self.analyze_marketplace(text)
                marketplace_stats[marketplace] += 1
                
                # Извлекаем конкретные темы из текста
                themes = self._extract_specific_themes(text, marketplace)
                if marketplace == 'OZON':
                    ozon_themes.extend(themes)
                elif marketplace == 'WB':
                    wb_themes.extend(themes)
                elif marketplace == 'YANDEX':
                    yandex_themes.extend(themes)
            
            # Убираем дубликаты и оставляем самые частые темы
            ozon_top = self._get_top_themes(ozon_themes)
            wb_top = self._get_top_themes(wb_themes)
            yandex_top = self._get_top_themes(yandex_themes)
            
            # Если нет конкретных тем, создаем на основе статистики
            if not ozon_top and marketplace_stats['OZON'] > 0:
                ozon_top = self._generate_fallback_themes('OZON', marketplace_stats['OZON'])
            if not wb_top and marketplace_stats['WB'] > 0:
                wb_top = self._generate_fallback_themes('WB', marketplace_stats['WB'])
            if not yandex_top and marketplace_stats['YANDEX'] > 0:
                yandex_top = self._generate_fallback_themes('YANDEX', marketplace_stats['YANDEX'])
            
            return {
                'title': '📊 Еженедельный обзор маркетплейсов',
                'summary': f'На основе анализа {len(all_content)} сообщений. OZON: {marketplace_stats["OZON"]}, WB: {marketplace_stats["WB"]}, Яндекс: {marketplace_stats["YANDEX"]}',
                'sections': {
                    'OZON': {
                        'key_points': ozon_top or ['Обновления платформы OZON'],
                        'important': ['Следите за обновлениями в личном кабинете'],
                        'tips': ['Регулярно проверяйте изменения в правилах площадки']
                    },
                    'WB': {
                        'key_points': wb_top or ['Обновления Wildberries'],
                        'important': ['Внимание к изменениям регламентов'],
                        'tips': ['Адаптируйтесь к изменениям логистики']
                    },
                    'YANDEX': {
                        'key_points': yandex_top or ['Развитие Яндекс Маркета'],
                        'important': ['Отслеживайте новые функции площадки'],
                        'tips': ['Используйте все возможности продвижения']
                    }
                },
                'recommendations': 'Рекомендуется активное участие в профессиональных сообществах для получения актуальной информации.'
            }
                
        except Exception as e:
            print(f"❌ Ошибка структурирования контента: {e}")
            return self._create_fallback_structure(source_texts + discussion_texts)

    def _extract_specific_themes(self, text, marketplace):
        """Извлекает конкретные темы из текста"""
        themes = []
        text_lower = text.lower()
        
        # Ключевые фразы для поиска
        key_phrases = {
            'OZON': [
                'доставк', 'логистик', 'тариф', 'реклам', 'продвижен', 
                'возврат', 'выкуп', 'брак', 'карточк', 'отзыв', 'рейтинг',
                'акци', 'распродаж', 'склад', 'аналитик', 'модерац',
                'каталог', 'поиск', 'скидк', 'бонус', 'тревел', 'travel',
                'карт', 'card', 'фулфилмент', 'fulfillment', 'комисс'
            ],
            'WB': [
                'доставк', 'логистик', 'тариф', 'реклам', 'продвижен',
                'возврат', 'выкуп', 'брак', 'карточк', 'отзыв', 'рейтинг', 
                'акци', 'распродаж', 'склад', 'аналитик', 'модерац',
                'каталог', 'поиск', 'скидк', 'бонус', 'кешбек', 'cashback',
                'фулфилмент', 'fulfillment', 'комисс', 'выдач', 'рекомендац'
            ],
            'YANDEX': [
                'доставк', 'логистик', 'тариф', 'реклам', 'продвижен',
                'возврат', 'выкуп', 'брак', 'карточк', 'отзыв', 'рейтинг',
                'акци', 'распродаж', 'склад', 'аналитик', 'модерац', 
                'каталог', 'поиск', 'скидк', 'бонус', 'плюс', 'plus',
                'доставк', 'самовывоз', 'поиск', 'выдач', 'комисс'
            ]
        }
        
        theme_map = {
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
            'бонус': 'Бонусные программы',
            'тревел': 'OZON Travel',
            'карт': 'OZON Карта',
            'кешбек': 'Кешбэк программы',
            'фулфилмент': 'Fulfillment услуги',
            'плюс': 'Яндекс Плюс',
            'комисс': 'Изменения комиссий',
            'выдач': 'Алгоритмы выдачи товаров',
            'рекомендац': 'Система рекомендаций'
        }
        
        phrases = key_phrases.get(marketplace, [])
        for phrase in phrases:
            if phrase in text_lower:
                theme = theme_map.get(phrase, phrase)
                if theme not in themes:
                    themes.append(theme)
        
        return themes[:5]  # Ограничиваем количество тем

    def _get_top_themes(self, themes, top_n=3):
        """Возвращает самые частые темы"""
        from collections import Counter
        if not themes:
            return []
        
        counter = Counter(themes)
        return [theme for theme, count in counter.most_common(top_n)]

    def _generate_fallback_themes(self, marketplace, count):
        """Генерирует темы на основе статистики"""
        base_themes = {
            'OZON': [
                'Обновления платформы OZON',
                'Логистические улучшения',
                'Новые маркетинговые инструменты'
            ],
            'WB': [
                'Обновления Wildberries', 
                'Оптимизация процессов',
                'Изменения в работе с продавцами'
            ],
            'YANDEX': [
                'Развитие Яндекс Маркета',
                'Новые функции для продавцов',
                'Обновления платформы'
            ]
        }
        
        themes = base_themes.get(marketplace, ['Обновления платформы'])
        if count > 5:
            themes.append(f'Активных обсуждений: {count}')
        
        return themes

    def _create_fallback_structure(self, texts):
        """Создает резервную структуру"""
        marketplace_stats = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
        for text in texts:
            marketplace = self.analyze_marketplace(text)
            marketplace_stats[marketplace] += 1
            
        return {
            'title': '📊 Еженедельный обзор маркетплейсов',
            'summary': f'На основе анализа {len(texts)} сообщений. OZON: {marketplace_stats["OZON"]}, WB: {marketplace_stats["WB"]}, Яндекс: {marketplace_stats["YANDEX"]}' if texts else 'Анализ ключевых изменений и трендов',
            'sections': {
                'OZON': {
                    'key_points': ['Обновления платформы OZON', 'Логистические процессы', 'Маркетинговые инструменты'],
                    'important': ['Следите за обновлениями в личном кабинете'],
                    'tips': ['Используйте все доступные инструменты аналитики']
                },
                'WB': {
                    'key_points': ['Обновления Wildberries', 'Процессы выкупа', 'Работа с возвратами'],
                    'important': ['Внимание к изменениям регламентов'],
                    'tips': ['Регулярно мониторьте статистику продаж']
                }
            },
            'recommendations': 'Следите за официальными объявлениями маркетплейсов'
        }