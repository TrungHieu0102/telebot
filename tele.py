import os
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Thiết lập thông tin bot Telegram
TELEGRAM_TOKEN = '6937689169:AAHdY6k9puw4YdGCXT8VEvZ99qxBANlnEPo'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Thiết lập thông tin Google Sheets
GOOGLE_SHEET_NAME = 'htshop256'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_FILE = 'D:/Telegram/pythonProject/htshop256-e48514344ccd.json'  # Đường dẫn đến file JSON của Google Sheets
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1  # Mở sheet đầu tiên

# Thiết lập các trạng thái cho người dùng
users = {}


# Xử lý lệnh /start từ người dùng
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    users[user_id] = {}
    bot.send_message(user_id, "Chào mừng bạn đến với Bot Doanh Thu!")


# Xử lý lệnh /input
@bot.message_handler(commands=['input'])
def handle_input(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Nhập tên sản phẩm:")
    bot.register_next_step_handler(message, input_product_name)


def input_product_name(message):
    user_id = message.from_user.id
    product_name = message.text
    users[user_id]['product_name'] = product_name
    bot.send_message(user_id, "Nhập giá bán:")
    bot.register_next_step_handler(message, input_price)


def input_price(message):
    user_id = message.from_user.id
    try:
        price = float(message.text)
        users[user_id]['price'] = price

        # Ghi thông tin vào Google Sheets
        sheet.append_row([users[user_id]['product_name'], users[user_id]['price']])

        bot.send_message(user_id, "Đã nhập thông tin thành công!")
    except ValueError:
        bot.send_message(user_id, "Giá bán phải là một số. Vui lòng thử lại.")


# Xử lý lệnh /stats
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    user_id = message.from_user.id
    data = sheet.get_all_values()
    if len(data) > 1:
        stats_message = "Danh sách sản phẩm và giá bán:\n"
        for row in data[1:]:
            stats_message += f"{row[0]} - {row[1]}\n"
        bot.send_message(user_id, stats_message)
    else:
        bot.send_message(user_id, "Không có dữ liệu thống kê.")

@bot.message_handler(commands=['total'])
def handle_total(message):
    user_id = message.from_user.id
    # Lấy giá trị từ ô D1
    total_value = sheet.acell('A1').value
    bot.send_message(user_id, f"{total_value}")

# Chạy bot
bot.polling()
