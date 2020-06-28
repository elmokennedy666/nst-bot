Neural style transfer model - VGG 19, она поставлена не полностью, так как её полный размер не влезает на heroku и не используется в переносе стиля
Для переноса функционала в telegram используется библиотека telebot(pyTelegramBotAPI)
Deploy бота - на Heroku
Id бота в телеграмме - @neustyltransfer_bot
Команды, которые знает бот - /start, /help, /transform (подсказки выдаются после старта общения с ботом)
После вызова команды transform ожидается style image, а потом content image. Обработка занимает примерно 8-10 минут.
