import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async, run_js

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100


async def main():
    global chat_msgs

    put_markdown("## 🧊 Welcome to Angex chat!\n Тут ви можете поділитися своїми думками🤔😏 ")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Ввійти в чат", required=True, placeholder="Введіть  ваше ім'я",
                           validate=lambda n: "Ваш нік не є унікальним!" if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msgs.append(('📢', f'`{nickname}` приєднався до чату!'))
    msg_box.append(put_markdown(f'📢 `{nickname}` приєднався до чату'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 нове повідомлення", [
            input(placeholder="текст повідомлення ...", name="msg"),
            actions(name="cmd", buttons=["Надіслати", {'label': "Залишити чат", 'type': 'cancel'}])
        ], validate=lambda m: ('msg', "Введіть текст повідомлення!") if m["cmd"] == "Надіслати" and not m['msg'] else None)

        if data is None:
            break

        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    refresh_task.close()

    online_users.remove(nickname)
    toast("Ви залишили чат!")
    msg_box.append(put_markdown(f'📢 Користувач `{nickname}` залишив чат!'))
    chat_msgs.append(('📢', f'Користувач `{nickname}` залишив чат!'))

    put_buttons(['Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))


async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


if __name__ == "__main__":
    start_server(main, host = '0.0.0.0', debug=True, port=8081, cdn=False, remote_access=True)