@app.route('/run-fixed')
def run_fixed():
    """Запуск исправленной версии"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner_fixed import run_bot_fixed
        result = loop.run_until_complete(run_bot_fixed())
        loop.close()
        
        return result
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/force-session')
def force_session():
    """Принудительное создание сессии"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from force_user_session import force_create_session
        loop.run_until_complete(force_create_session())
        loop.close()
        
        return "✅ Сессия создана! Теперь используйте /run-fixed"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"