import random
from translate import translator
import os
from config import Config, message_types
from telebot import types


config = Config()
fact_ending = os.environ.get(config.env_fact_end, None)


def _is_translate_time(message):
    if all([
        config.period.translate_count > config.period.translate_period,
        message.date - config.period.last_message_data > config.offset,
        len(message.text) > config.message_length,
        not message.text.startswith('http'),
    ]):
        return True
    return False


def _is_punch_time(message):
    if all([
        config.period.punch_count > config.period.punch_period,
        message.date - config.period.last_punch_data > config.offset,
    ]):
        return True
    return False


def _is_fact_time(message):
    return message.date - config.period.last_fact_data > config.long_offset


def _is_pubg_time(message):
    ''' It is black magick, but if this return `True` we need to play pubg!!! '''
    return int(message.data) % random.randint(10, 100) == random.randint(0, 5)


def spot_answer_type(message):
    text = message.text.lower()
    if text in config.skip_triger:
        return message_types.skip

    elif _is_pubg_time(message):
        return message_types.pubg

    # logic only for special users
    elif message.from_user.username in config.users:
        if any([word in text for word in config.fact_triger]) and _is_fact_time(message):
            return message_types.fact

        return message_types.translate if _is_translate_time(message) else None

    return message_types.punch if _is_punch_time(message) else None


def translate(text):
    try:
        translate_message = translator(config.lang_from, config.lang_to, text)
        return translate_message[0]
    except Exception:
        return


def get_fact():
    fact = random.choice(config.facts)
    return f"{fact.capitalize()} (c) {fact_ending}"


def reset_period(date):
    config.period.punch_count = config.period.translate_count = 0
    config.period.last_message_data = config.period.last_punch_data = date


def get_markup_pubg():
    markup = types.InlineKeyboardMarkup()

    row = [
        types.InlineKeyboardButton('Да', callback_data='yes'),
        types.InlineKeyboardButton('Нет', callback_data='no'),
    ]

    markup.row(*row)
    return markup


def update_text(call):
    text = call.message.text + '\n\n'
    user = call.from_user.first_name or "@" + call.from_user.username
    because = random.choice(config.because_i_am[call.data])

    return text + f"{user}: Я {'пас' if call.data == 'no' else 'за'} потому что я {because}"
