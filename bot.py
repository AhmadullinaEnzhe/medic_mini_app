from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import json
import html
import logging

# Включите логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

user_results = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Посмотреть результаты")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Привет! Нажмите кнопку ниже, чтобы посмотреть результаты.",
        reply_markup=reply_markup
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем данные из Mini App
        data = json.loads(update.message.web_app_data.data)
        user_id = update.message.from_user.id
        user_results[user_id] = data
        # Форматируем сообщение для отправки
        message_text = f"🧪 <b>{data['type']}</b>:\n\n"
        
        # Добавляем результаты
        for result in data.get('results', []):
            status_icon = "✅" if result.get('status') == 'normal' else "⚠️" if result.get('status') == 'warning' else "❌"
            message_text += f"{status_icon} <b>{html.escape(result.get('parameter', ''))}:</b> {html.escape(result.get('value', ''))}\n"
            message_text += f"{html.escape(result.get('explanation', ''))}\n\n"
        
        # Отправляем сообщение
        await update.message.reply_text(message_text, parse_mode='HTML')
        
    except Exception as e:
        logging.error(f"Ошибка обработки данных: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке результатов")

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if user_id in user_results:
        data = user_results[user_id]
        message_text = f"🧪 <b>{data['type']}</b>:\n\n"
        
        for result in data.get('results', []):
            status_icon = "✅" if result.get('status') == 'normal' else "⚠️" if result.get('status') == 'warning' else "❌"
            message_text += f"{status_icon} <b>{html.escape(result.get('parameter', ''))}:</b> {html.escape(result.get('value', ''))}\n"
            message_text += f"{html.escape(result.get('explanation', ''))}\n\n"
        
        await update.message.reply_text(message_text, parse_mode='HTML')
    else:
        await update.message.reply_text("❌ У вас нет сохраненных результатов.")

def main():
    # Создаем Application
    application = Application.builder().token("YOUR_BOT_TOKEN").build()
    
    # Добавляем обработчик данных из Web App
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_results))
    # Запускаем бота
    application.run_polling()
if __name__ == '__main__':
    main()