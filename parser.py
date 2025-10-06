import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)

@dataclass
class ParsedMessage:
    id: int
    channel: str
    text: str
    date: datetime
    media: Optional[str] = None

async def parse_channel_messages(client, channel_entity, since_date: datetime) -> List[ParsedMessage]:
    """
    Парсит сообщения из канала начиная с указанной даты
    """
    try:
        logger.info(f"🔍 Парсим канал: {channel_entity} с {since_date}")
        
        # Получаем entity канала
        if isinstance(channel_entity, str):
            channel = await client.get_entity(channel_entity)
        else:
            channel = channel_entity
        
        messages = []
        async for message in client.iter_messages(
            channel,
            offset_date=since_date,
            reverse=True  # Сначала старые сообщения
        ):
            if message.text:  # Только сообщения с текстом
                parsed_message = ParsedMessage(
                    id=message.id,
                    channel=channel_entity,
                    text=message.text,
                    date=message.date,
                    media=message.media if message.media else None
                )
                messages.append(parsed_message)
        
        logger.info(f"✅ Получено {len(messages)} сообщений из {channel_entity}")
        return messages
        
    except Exception as e:
        logger.error(f"❌ Ошибка парсинга канала {channel_entity}: {e}")
        return []

async def filter_messages_by_keywords(messages: List[ParsedMessage], keywords: List[str]) -> List[ParsedMessage]:
    """
    Фильтрует сообщения по ключевым словам
    """
    if not keywords:
        return messages
    
    filtered = []
    for message in messages:
        if any(keyword.lower() in message.text.lower() for keyword in keywords):
            filtered.append(message)
    
    logger.info(f"🔍 Фильтрация: {len(messages)} → {len(filtered)} сообщений")
    return filtered

async def format_message_for_publication(message: ParsedMessage) -> str:
    """
    Форматирует сообщение для публикации
    """
    # Обрезаем длинные сообщения
    text = message.text
    if len(text) > 4000:
        text = text[:4000] + "..."
    
    # Добавляем источник и дату
    formatted = f"{text}\n\n📅 {message.date.strftime('%d.%m.%Y %H:%M')}\n🔗 Источник: {message.channel}"
    
    return formatted