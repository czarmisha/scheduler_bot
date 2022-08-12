from telegram import InlineKeyboardButton

from utils.translation import messages

def get_date_keyboard(day, month, year):
    return [
            [InlineKeyboardButton(f"{messages['day']['ru']}\n{messages['day']['uz']}", callback_data=-1),],
            [
                InlineKeyboardButton('➖', callback_data='dec_day'),
                InlineKeyboardButton(f'{day}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_day'),
            ],
            [InlineKeyboardButton(f"{messages['month']['ru']}\n{messages['month']['uz']}", callback_data=-2),],
            [
                InlineKeyboardButton('➖', callback_data='dec_month'),
                InlineKeyboardButton(f'{month}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_month'),
            ],
            [InlineKeyboardButton(f"{messages['year']['ru']}\n{messages['year']['uz']}", callback_data=-3),],
            [
                InlineKeyboardButton('➖', callback_data='dec_year'),
                InlineKeyboardButton(f'{year}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_year'),
            ],
            [InlineKeyboardButton(f"✔️ {messages['confirm']['ru']} / {messages['confirm']['uz']}", callback_data=f'{day}.{month}.{year}')],
            [InlineKeyboardButton(f"✖️ {messages['cancel']['ru']} / {messages['cancel']['uz']}", callback_data='cancel')],
        ]

def get_time_keyboard(hour, minute, state):
    return [
            [InlineKeyboardButton(f"{messages['hours']['ru']}\n{messages['hours']['uz']}", callback_data=-1),],
            [
                InlineKeyboardButton('➖', callback_data=f'dec_hour{state}'),
                InlineKeyboardButton(f'{hour}', callback_data=2),
                InlineKeyboardButton('➕', callback_data=f'inc_hour{state}'),
            ],
            [InlineKeyboardButton(f"{messages['minutes']['ru']}\n{messages['minutes']['uz']}", callback_data=-2),],
            [
                InlineKeyboardButton('➖', callback_data=f'dec_minute{state}'),
                InlineKeyboardButton(f'{minute}', callback_data=2),
                InlineKeyboardButton('➕', callback_data=f'inc_minute{state}'),
            ],
            [InlineKeyboardButton(f"✔️ {messages['confirm']['ru']} / {messages['confirm']['uz']}", callback_data=f'{hour}:{minute}')],
            [InlineKeyboardButton(f"✖️ {messages['cancel']['ru']} / {messages['cancel']['uz']}", callback_data='cancel')],
        ]
