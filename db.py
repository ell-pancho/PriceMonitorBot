import os
import json

class Database():

    def __init__(self):
        self.monitorList = dict()
        self.path = os.path.abspath(r"./db.json")

    def chat_ids(self):
        return self.monitorList.keys()

    def name_list(self, chat_id):
        return self.monitorList[chat_id].keys()

    def register_chat_id(self, chat_id):
        if not chat_id in self.monitorList.keys():
            self.monitorList[chat_id] = dict()

    def save(func):
        def save_db(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            with open(self.path, 'w') as output:
                json.dump(self.monitorList, output, sort_keys=True, indent=2)
            return result
        return save_db

    def load(self):
        if not os.path.exists(self.path):
            return
        new_data = dict()
        with open(self.path, 'r') as output:
            data = json.load(output)
            for i in data.keys():
                new_data[int(i)] = dict()
                for j,k in data[i].items():
                    new_data[int(i)][str(j)] = k 
            self.monitorList = new_data

    @save
    def register_name(self, chat_id, name, url):
        if name in self.monitorList[chat_id].keys():
            return False
        params = {
            'url': url,
            'status': True,
            'last_best_price': 0,
            'last_check_time': 0,
            'time_step': 60
        }
        self.monitorList[chat_id][name] = params
        return True
    @save
    def set_last_best_price(self, chat_id, name, value):
        self.monitorList[chat_id][name]['last_best_price'] = value

    @save
    def set_last_check_time(self, chat_id, name, value):
        self.monitorList[chat_id][name]['last_check_time'] = value

    @save
    def set_status(self, chat_id, name, value):
        self.monitorList[chat_id][name]['status'] = value

    @save
    def set_time_step(self, chat_id, name, value):
        self.monitorList[chat_id][name]['time_step'] = value

    @save
    def delete_name(self, chat_id, name):
        self.monitorList[chat_id].pop(name)