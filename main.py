import vk
import requests
from datetime import datetime
from json import loads
from os import system, name

# Попытка импортировать config
try:
    from config import *
# Завершение скрипта, если config не найден
except ModuleNotFoundError:
    print('Файл config.py не найден')
    exit()
# Проверка наличия необходимых переменных в config
else:
    if TOKEN and API_VERSION and GROUP_ID:
        pass
    else:
        print('Файл config.py имеет неверную структуру')
        exit()


# Создаём сессию для api
api = vk.API(vk.AuthSession(access_token=TOKEN), v=API_VERSION)


# Функция для создания строки timestamp
def timestamp():
    return datetime.strftime(datetime.now(), '%d.%m.%Y %H:%M:%S')


# Функция очистки консоли
def clear():
    # Для windows
    if name == 'nt':
        _ = system('cls')

    # Для остальных
    else:
        _ = system('clear')


# Функция для получения ключа и ts LongPoll сервера
def getLongPoll():
    # Попытка обращения к api
    try:
        response = api.groups.getLongPollServer(group_id=GROUP_ID)

    # Вывод ошибки в случае неудачи
    except Exception as e:
        print(timestamp(), 'Произошла ошибка при получении LongPoll сервера:')
        print(e)
        return None

    # Возвращение сервера, ключа и ts в случае удачи
    else:
        return {'server': response['server'], 'key': response['key'], 'ts': response['ts']}


# Функция для получения списка сообщений
def get_messages(server, l_key, l_ts):
    url = server + '?act=a_check&key=' + l_key + '&ts=' + l_ts + '&wait=25'
    while True:
        # Попытка обращения к LongPoll серверу
        try:
            response = loads(requests.get(url).text)

        # Вывод ошибки и перезапуск цикла в случае неудачи
        except Exception as e:
            print(timestamp(), 'При подлкючении к LongPoll серверу произошла ошибка:')
            print(e)
            print('Повторяю попытку...')

        # Обработка ответа в случае удачи
        else:
            # Обработка ошибок в случае их наличия
            if 'failed' in response:
                # Установка нового ts в случае ошибки 1
                if response['failed'] == 1:
                    l_ts = response['ts']

                # Получение новых ts и ключа в случае ошибки 2 или 3
                elif response['failed'] == 2 or 3:
                    lp_data = getLongPoll()
                    l_ts, l_key = lp_data['ts'], lp_data['key']

                # Возврат пустого списка сообщений и новых ts и ключа
                return {'updates': [], 'key': l_key, 'ts': l_ts}

            # Форматирование и возврат новых сообщений
            else:
                msgs = []
                for upd in response['updates']:
                    msgs.append(upd['object']['message'])
                    l_ts = response['ts']
                return {'updates': msgs, 'key': l_key, 'ts': l_ts}


# Функция отправки сообщений
def send(uid, mess):
    # Попытка отправить сообщение через api
    try:
        api.messages.send(user_id=uid, message=mess, random_id=0)

    # Вывод ошибки в случае неудачи
    except Exception as e:
        print(timestamp(), 'При отправке сообщения произошла ошибка:')
        print(e)

    # Вывод сообщения об успехе в случае удачи
    else:
        print(timestamp(), 'Сообщение для', uid, 'отправлено')


if __name__ == '__main__':
    clear()
    print(timestamp(), 'Бот начал свою работу')
    data = getLongPoll()
    key, ts = data['key'], data['ts']

    while True:
        messages = get_messages(data['server'], key, ts)

        # Обработка сообщений
        for msg in messages['updates']:
            send(msg['from_id'], 'Я тебя услышал')
            ts, key = messages['ts'], messages['key']  # Установка ts и key, полученных из get_messages
