# В database.py добавляем функцию
def post_exists(post_content):
    """Проверяет, был ли уже отправлен такой пост"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM posts 
        WHERE post_content = ? AND created_at > datetime('now', '-1 day')
    ''', (post_content,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

# В bot_runner.py добавляем проверку перед отправкой
async def publish_post(client, post_content):
    """Публикует пост в целевой канал"""
    try:
        # Проверяем, не отправляли ли уже такой пост сегодня
        from database import post_exists
        if post_exists(post_content):
            logger.info("⚠️ Похожий пост уже был отправлен сегодня, пропускаем")
            return
        
        # Ограничиваем длину поста
        max_length = 4096
        if len(post_content) > max_length:
            post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
        
        await client.send_message(TARGET_CHANNEL, post_content)
        logger.info(f"✅ Пост успешно опубликован в канале {TARGET_CHANNEL}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка публикации поста: {e}")
        raise