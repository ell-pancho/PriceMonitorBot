from html.parser import HTMLParser
import requests
from lxml import html

def parser_html(rawHTML):
    data            = dict()
    tree            = html.fromstring(rawHTML)
    sec             = tree.xpath('//tr[@class = "r1"]/td/span[@class="sec_high" or @class="sec_null" or @class="sec_low"]/text()')
    name            = tree.xpath('//tr[@class = "r1"]/td/text()')
    quantity        = tree.xpath('//tr[@class = "r1"]/td[@class="qty"]/text()')
    isk             = [int(i.replace('\n','').replace(' ','').replace(',','')) for i in tree.xpath('//tr[@class = "r1"]/td[@class = "isk"]/text()') if i.replace('\n','').replace(' ','')]
    update_time     = tree.xpath('//tr[@class = "r1"]/td[@class="update_time"]/span/text()')
    names           = list()

    for item in name:
        clear = item.replace('\n','').replace(' ','').replace(',','')
        if not clear: continue
        try:
            a = int(clear)
        except:
            names.append(clear)

    for count, item in enumerate(isk):
        info = dict()
        info['isk'] = int(item)
        info['system_name'] = names[count]
        info['sec'] = float(sec[count])
        info['quantity'] = int(quantity[count])
        info['update_time'] = update_time[count]
        data[count] = info
    return data

def get_best_price(url):
    try:
        request = requests.get(url)
    except requests.exceptions.HTTPError as e:
        print(e)
        return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None
    text = request.text
    data = parser_html(text)
    return data[0]