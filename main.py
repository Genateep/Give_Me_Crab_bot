import telebot
import func as f
from time import time
from datetime import datetime
from config import BOT_TOKEN
from telebot import types
from collections import defaultdict

bot = telebot.TeleBot(BOT_TOKEN)

START, CHOICE_1, SECOND, CHOICE_2, ANSWER, FINISH = range(6)  # состояния

USER_STATE = defaultdict(lambda: START)  # словарь состояний
REQ = defaultdict(lambda: {})  # словарь данных


def get_state(message):
    # возвращает состояние
    return USER_STATE[message.chat.id]


def update_state(message, state):
    # изменяет состояние
    USER_STATE[message.chat.id] = state


def get_req(user_id):
    # возвращает данные
    return REQ[user_id]


def update_req(user_id, key, value):
    # добавляет данные
    REQ[user_id][key] = value


@bot.message_handler(commands=['start'])
def cmd_greet(message):
    bot.send_message(message.chat.id,
                     "Введи ссылку на профиль или id первого аккаунта")
    update_state(message, START)


@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.reply_to(message, 'Суть работы бота - показать друзей целевого аккаунта у которых есть общие друзья, '
                          'например, с тобой. Для этого нужно сперва указать свой профиль, затем профиль цели. Бот '
                          'пробежится по списку твоих друзей и друзей цели, а затем и по спискам друзей у ваших '
                          'друзей. Таким образом бот произведет сотни запросов и получит десятки и даже сотни тысяч '
                          'идентификаторов пользователей, а затем сопоставит и отсортирует списки. Это дело может '
                          'занять от 20 секунд до 15 минут, так что будь добр, побудь ждуном. Перезапустить бота '
                          'всегда можно командой /start')


@bot.message_handler(func=lambda message: get_state(message) == START)
def handle_first(message):
    if message.chat.type == 'private':
        if f.id_check(f.get_id(message.text)):
            id1 = f.get_id(message.text)
            update_req(message.chat.id, 'first_id', id1)
            update_state(message, CHOICE_1)

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data='yes1')
            item2 = types.InlineKeyboardButton("Нет", callback_data='no1')
            markup.add(item1, item2)

            bot.send_photo(message.chat.id, f.get_photo(id1),
                           caption='Это аккаунт {}?'.format(' '.join(f.get_greet_name(id1, name_case='gen'))),
                           reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             'Не принимается. Need /help?')


@bot.message_handler(func=lambda message: get_state(message) == SECOND)
def handle_second(message):
    if message.chat.type == 'private':
        if f.id_check(f.get_id(message.text)):
            id2 = f.get_id(message.text)
            update_req(message.chat.id, 'second_id', id2)
            update_state(message, CHOICE_2)

            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Да", callback_data='yes2')
            item2 = types.InlineKeyboardButton("Нет", callback_data='no2')
            markup.add(item1, item2)

            bot.send_photo(message.chat.id, f.get_photo(id2),
                           caption='Это аккаунт {}?'.format(' '.join(f.get_greet_name(id2, name_case='gen'))),
                           reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             'Не принимается. Need /help?')


@bot.message_handler(func=lambda message: get_state(message) == ANSWER)
def handle_second(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, 'Погоди, я думаю...')


@bot.message_handler(func=lambda message: get_state(message) == FINISH)
def handle_second(message):
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, 'Нажми кнопочку!')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'yes1' and get_state(call.message) == CHOICE_1:
                bot.send_message(call.message.chat.id,
                                 'Введи ссылку на профиль или id второго аккаунта')
                update_state(call.message, SECOND)
                # remove inline buttons
                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         caption='{}\nвсего друзей: {}'.format(
                                             ' '.join(f.get_greet_name(REQ[call.message.chat.id]['first_id'])),
                                             len(f.get_data(REQ[call.message.chat.id]['first_id']))),
                                         reply_markup=None)
                # show alert
                bot.answer_callback_query(callback_query_id=call.id,
                                          text="на карандаше...")

            elif call.data == 'no1' and get_state(call.message) == CHOICE_1:
                bot.send_message(call.message.chat.id,
                                 'Давай по-новой')
                update_state(call.message, START)
                # remove inline buttons
                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         caption='отменено',
                                         reply_markup=None)

            elif call.data == 'yes2' and get_state(call.message) == CHOICE_2:
                if REQ[call.message.chat.id]['second_id'] == REQ[call.message.chat.id]['first_id']:
                    bot.send_message(call.message.chat.id,
                                     'Это два одинаковых профиля! Укажи другой')
                    update_state(call.message, SECOND)
                    # remove inline buttons
                    bot.edit_message_caption(chat_id=call.message.chat.id,
                                             message_id=call.message.message_id,
                                             caption='ошибка',
                                             reply_markup=None)
                else:
                    bot.send_message(call.message.chat.id,
                                     'Минуточку...')
                    update_state(call.message, ANSWER)
                    # remove inline buttons
                    bot.edit_message_caption(chat_id=call.message.chat.id,
                                             message_id=call.message.message_id,
                                             caption='{}\nвсего друзей: {}'.format(
                                                 ' '.join(f.get_greet_name(REQ[call.message.chat.id]['second_id'])),
                                                 len(f.get_data(REQ[call.message.chat.id]['second_id']))),
                                             reply_markup=None)
                    # show alert
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text="на карандаше...")
                    do_that_shit(call.message)

            elif call.data == 'no2' and get_state(call.message) == CHOICE_2:
                bot.send_message(call.message.chat.id,
                                 'Давай по-новой')
                update_state(call.message, SECOND)
                # remove inline buttons
                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         caption='отменено',
                                         reply_markup=None)
            else:
                bot.edit_message_caption(chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         caption='ошибка',
                                         reply_markup=None)

    except Exception as e:
        print(repr(e))


def logger(user_id, result, used_time=0):
    # логирование словаря данных сессии
    REQ[user_id]['result'] = result
    REQ[user_id]['used_time'] = used_time
    REQ[user_id]['date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open('log.txt', 'a', encoding='utf-8') as log:
        log.write(str(dict(REQ)) + '\n')


def split(arr, size):
    # разделение списка на вложенные списки по размеру
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
        arrs.append(arr)
        return arrs


def do_that_shit(message):

    # делаем списки друзей двух указанных профилей
    s1 = f.get_data(REQ[message.chat.id]['first_id'])
    s2 = f.get_data(REQ[message.chat.id]['second_id'])

    if REQ[message.chat.id]['second_id'] in s1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        item1 = types.KeyboardButton("/start")
        item2 = types.KeyboardButton("/help")
        markup.add(item1, item2)

        mut_friends = set(s1).intersection(set(s2))

        if len(mut_friends) > 0:
            bot.send_message(message.chat.id,
                             'Эти двое уже в друзьях!\n\nОбщие друзья:\n{}'.format(
                                 ', '.join(' '.join(f.get_greet_name(i)) for i in mut_friends)),
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             'Эти двое уже в друзьях!\n\nОбщих друзей нет.',
                             reply_markup=markup)

        update_state(message, FINISH)

        logger(message.chat.id, 'they are friends!')

    elif len(set(s1).intersection(set(s2))) > 0:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        item1 = types.KeyboardButton("/start")
        item2 = types.KeyboardButton("/help")
        markup.add(item1, item2)

        bot.send_message(message.chat.id,
                         'У них есть общие друзья:\n\n{}'.format(
                             ', '.join(' '.join(f.get_greet_name(i)) for i in set(s1).intersection(set(s2)))),
                         reply_markup=markup)
        update_state(message, FINISH)

        logger(message.chat.id, 'have mutual: {}'.format(len(set(s1).intersection(set(s2)))))

    else:
        start_time = time()

        bot.send_message(message.chat.id,
                         'Общих друзей нет, но у друзей тоже есть друзья...')

        d1 = f.get_id_dict(REQ[message.chat.id]['first_id'])
        bot.send_message(message.chat.id,
                         'Друзей с открытым профилем у {}: {}...'.format(
                             ' '.join(f.get_greet_name(REQ[message.chat.id]['first_id'], name_case='gen')), len(d1)))
        d2 = f.get_id_dict(REQ[message.chat.id]['second_id'])
        bot.send_message(message.chat.id,
                         'У {}: {}...'.format(
                             ' '.join(f.get_greet_name(REQ[message.chat.id]['second_id'], name_case='gen')), len(d2)))

        # делаем пересечение списков, чтоб найти общих друзей друзей
        for i in list(d2):
            d2[i].intersection_update(set(d1))
            if len(d2[i]) == 0:
                del d2[i]
        # считаем сколько всего у них есть общих друзей
        f_count = set()
        for i in d2:
            f_count |= d2[i]
        # bot.send_message(message.chat.id,
        #                  '...и их как минимум {}!'.format(len(f_count)))
        if len(f_count) == 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            item1 = types.KeyboardButton("/start")
            item2 = types.KeyboardButton("/help")
            markup.add(item1, item2)

            bot.send_message(message.chat.id,
                             'Этих персон разделяет более трех рукопожатий.\n'
                             'Дальнейший поиск доступен в платной версии бота,\n'
                             'которого, к сожалению, пока не существует.',
                             reply_markup=markup)

            logger(message.chat.id, 'not found!', int(time() - start_time))

        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            item1 = types.KeyboardButton("/start")
            item2 = types.KeyboardButton("/help")
            markup.add(item1, item2)

            # сортировка друзей второго профиля по количеству общих друзей с первым профилем
            crab_list = sorted(d2, key=lambda x: len(d2[x]), reverse=True)

            # подготовка строки вывода
            crab_message = []
            for i in crab_list:
                crab_message.append('<a href="http://vk.com/id{}">{}  >={}</a>'.format(
                    i, ' '.join(f.get_greet_name(i)), len(d2[i])))

            bot.send_message(message.chat.id,
                             'Список друзей {} по убыванию количества общих друзей c {}:'.format(
                                 ' '.join(f.get_greet_name(REQ[message.chat.id]['second_id'], name_case='gen')),
                                 ' '.join(f.get_greet_name(REQ[message.chat.id]['first_id'], name_case='ins'))))

            # выводим список с максимально допустимым количеством ссылок(100):
            if len(crab_message) <= 100:
                bot.send_message(message.chat.id,
                                 '\n'.join(crab_message),
                                 disable_web_page_preview=True,
                                 parse_mode='HTML')
            else:
                for i in split(crab_message, 100):
                    bot.send_message(message.chat.id,
                                     '\n'.join(i),
                                     disable_web_page_preview=True,
                                     parse_mode='HTML')

            update_state(message, FINISH)

            logger(message.chat.id, len(d2), int(time() - start_time))

            bot.send_photo(message.chat.id, open('vse.jpg', 'rb'), reply_markup=markup)


if __name__ == '__main__':
    try:
        bot.infinity_polling()
    except Exception:
        pass
