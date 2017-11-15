import time
import json, os
import MonitorPriceBot as mPB

TOKEN_PATH = r"./token.json"

def get_token():
    token_path = os.path.abspath(TOKEN_PATH)
    if not os.path.exists(token_path): return False
    with open(token_path, 'r') as token:
        data = json.loads(token.read())
        token = data["token"]
    return token

def get_last_check_update():
    path = os.path.abspath(LAST_CHECK_UPDATE_PATH)
    if not os.path.exists(path): return False
    with open(path, 'r') as output:
        data = json.loads(output.read())
        last_check_update = data["last_check_update"]
    return last_check_update

def save_last_check_update(value):
    data = dict()
    with open(LAST_CHECK_UPDATE_PATH, 'w') as output:
        data["last_check_update"] = value
        json.dump(data, output, sort_keys=True, indent=2)

def main():
    
    token = get_token()
    if not token:
        print("Token-file not exists!")
        return
    bot = mPB.PriceMonitor_Bot(token)
    
    update_id = bot.last_update()['update_id']

    while True:
        last_update = bot.last_update()
        chat_id     = bot.get_chat_id(last_update)
        if not chat_id in bot.db.chat_ids(): bot.db.register_chat_id(chat_id)

        if update_id == last_update['update_id']:
            user_message = bot.get_message(last_update)

            #/help
            if user_message == "/help": bot.help(chat_id)

            #/settimestep
            if user_message.startswith("/settimestep"):
                if len(user_message.split()) == 2:
                    command, value = user_message.split()
                    bot.set_time_step(chat_id, value)
                else:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            #/monitor
            if user_message.startswith("/monitor"):
                if len(user_message.split()) == 3:
                    command, name, url = user_message.split()
                    bot.monitor(chat_id, name, url)
                else:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            #/listmonitor            
            if user_message == "/listmonitor": bot.list_monitor(chat_id)

            #/delete
            if user_message.startswith("/delete"):
                if len(user_message.split()) == 2:
                    command, name = user_message.split()
                    bot.delete(chat_id, name)
                else:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            #/startmonitor or /stopmonitor
            if user_message.startswith("/startmonitor") or user_message.startswith("/stopmonitor"):
                if len(user_message.split()) == 1:
                    bot.change_status(chat_id, True if user_message.startswith("/startmonitor") else False)
                elif len(user_message.split()) == 2:
                    command, name = user_message.split()
                    bot.change_status(chat_id, True if user_message.startswith("/startmonitor") else False, name)
                else:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            save_last_check_update(last_update['update_id'])
            update_id += 1
        time.sleep(1)

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()