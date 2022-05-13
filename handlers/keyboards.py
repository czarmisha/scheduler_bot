from telegram import InlineKeyboardButton

def get_data_keyboard(day, month, year):
    return [
            [
                InlineKeyboardButton('День', callback_data=-1),
                InlineKeyboardButton('➖', callback_data='dec_day'),
                InlineKeyboardButton(f'{day}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_day'),
            ],
            [
                InlineKeyboardButton('Месяц', callback_data=-2),
                InlineKeyboardButton('➖', callback_data='dec_month'),
                InlineKeyboardButton(f'{month}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_month'),
            ],
            [
                InlineKeyboardButton('Год', callback_data=-3),
                InlineKeyboardButton('➖', callback_data='dec_year'),
                InlineKeyboardButton(f'{year}', callback_data=2),
                InlineKeyboardButton('➕', callback_data='inc_year'),
            ],
            [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
            [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
        ]

def get_time_keyboard(hour, minute, state):
    return [
            [
                InlineKeyboardButton('Часы', callback_data=-1),
                InlineKeyboardButton('➖', callback_data=f'dec_hour{state}'),
                InlineKeyboardButton(f'{hour}', callback_data=2),
                InlineKeyboardButton('➕', callback_data=f'inc_hour{state}'),
            ],
            [
                InlineKeyboardButton('Минуты', callback_data=-2),
                InlineKeyboardButton('➖', callback_data=f'dec_minute{state}'),
                InlineKeyboardButton(f'{minute}', callback_data=2),
                InlineKeyboardButton('➕', callback_data=f'inc_minute{state}'),
            ],
            [InlineKeyboardButton('✔️ Подтвердить', callback_data='done')],
            [InlineKeyboardButton('✖️ Отменить', callback_data='cancel')],
        ]