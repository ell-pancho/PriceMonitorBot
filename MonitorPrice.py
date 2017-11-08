import requests
import time
import threading
import check_price as cPrice
import db
import copy
import json, os

class PriceMonitor_Bot():

    def __init__(self, token):
        self.token          = token
        self.api_url        = "https://api.telegram.org/bot{}/".format(token)
        self.db             = db.Database()
        self.db.load()
        threading.Thread(target=self.monitoring, args=()).start()

    def save_db(func):
        def save(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.db.save()
        return save

    def get_updates(self, offset=None, timeout=100):
        params = {'timeout': timeout, 'offset': offset}
        response = requests.get(self.api_url + 'getUpdates', data=params)
        result_json = response.json()['result']
        return result_json

    def last_update(self):
        data = self.get_updates()
        if len(data) > 0:
            last_update = data[-1]
        else:
            last_update = data[len(data)]
        return last_update

    def get_chat_id(self, update):
        chat_id = update['message']['chat']['id']
        return chat_id

    def get_message(self, data):
        try:
            message = data['message']['text']
        except:
            message = ""
        return message

    def send_message(self, chat, text, parse_mode="Markdown"):
        params = {'chat_id': chat, 'text': text, 'parse_mode': parse_mode}
        response = requests.post(self.api_url + 'sendMessage', data=params)
        return response

    def solo_check(self, chat_id, name, monitorList):
        message = ""
        url = monitorList[chat_id][name]['url']
        try:
            data = cPrice.get_price(url)
        except:
            return
        if data == None: return
        if int(data['isk']) != monitorList[chat_id][name]['last_best_price']:
            self.db.set_last_best_price(chat_id, name, int(data['isk']))
            message = "[{1}]({2}) \n*Security status:* {0[sec]}, *System:* {0[system_name]}, *Price:* {0[isk]}, *Quantity:* {0[remaining]}, *Update time:* {0[update_time]}".format(data, name, url)                
        if message: self.send_message(chat_id, message)
        message = ""
        print('check {}'.format(name))

    def monitoring(self):
        while True:
            monitorList = copy.deepcopy(self.db.monitorList)
            try:
                for chat_id in monitorList.keys():
                    for name in monitorList[chat_id].keys():
                        if not monitorList[chat_id][name]['status']: continue
                        current_time = round(time.time())
                        if abs(current_time-monitorList[chat_id][name]['last_check_time'])>int(monitorList[chat_id][name]['time_step']):
                            self.db.set_last_check_time(chat_id, name, current_time)
                            t = threading.Thread(target=self.solo_check, args=(copy.deepcopy(chat_id), copy.deepcopy(name), copy.deepcopy(monitorList)))
                            t.start()
            except:
                pass
            time.sleep(1)

    def monitor(self, chat_id, name, url):
        incorrect = "*{}* already added for monitoring!".format(name)
        correct = "*{}* added for monitoring!".format(name)
        message = self.db.register_name(chat_id, name, url)
        if message:
            self.send_message(chat_id, correct)
            self.db.save()
        else:
            self.send_message(chat_id, incorrect)

    @save_db
    def set_timestep(self, chat_id, value):
        for name in self.monitorList[chat_id].keys():
            self.db.set_time_step(chat_id, name, value)

    @save_db
    def change_status(self, chat_id, status, name=None):
        if name: self.db.set_status(chat_id, name, status)
        else:
            for name in self.db.monitorList[chat_id].keys():
                self.db.set_status(chat_id, name, status)

    def help(self, chat_id):
        message = "Help for PriceMonitorBot:\n/monitor [name] [url]\n/stop [name]\n/settimestep [value] | default value 60 seconds"
        self.send_message(chat_id, message, None)

def main():
    
    token_path = os.path.abspath(r"./token.json")
    if not os.path.exists(token_path):
        print("Token-file not exists!")
        return
    with open(token_path, 'r') as token:
        data = json.loads(token.read())
        token = data["token"]
    bot = PriceMonitor_Bot(token)
    
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
                try:
                    command, value = user_message.split()
                    bot.set_timestep(value)
                except:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            #/monitor
            if user_message.startswith("/monitor"):
                #try:
                command, name, url = user_message.split()
                bot.monitor(chat_id, name, url)
                #except:
                #    bot.send_message(chat_id, "Wrong format. See /help.")

            #/startmonitor or /stopmonitor
            if user_message.startswith("/startmonitor") or user_message.startswith("/stopmonitor"):
                if len(user_message.split()) == 1:
                    bot.change_status(chat_id, True if user_message.startswith("/startmonitor") else False)
                elif len(user_message.split()) == 2:
                    command, name = user_message.split()
                    bot.change_status(chat_id, True if user_message.startswith("/startmonitor") else False, name)
                else:
                    bot.send_message(chat_id, "Wrong format. See /help.")

            update_id += 1
        time.sleep(1)

if __name__ == '__main__':  
    try:
        main()
    except KeyboardInterrupt:
        exit()