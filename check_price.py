from html.parser import HTMLParser
import requests
from lxml import html

def parser_html(rawHTML):
    data            = dict()
    tree            = html.fromstring(rawHTML)
    list_lxml       = tree.xpath('//tr[@class = "r1"]')
    list_lxml       = list_lxml[0]
    sec             = list_lxml.xpath('//td/span[@class="sec_high" or @class="sec_null" or @class="sec_low"]/text()')
    name            = tree.xpath('//tr[@class = "r1"]/td/text()')
    remaining       = list_lxml.xpath('//td[@class="qty"]/text()')
    isk             = [int(i.replace('\n','').replace(' ','').replace(',','')) for i in list_lxml.xpath('//td[@class = "isk"]/text()') if i.replace('\n','').replace(' ','')]
    update_time     = list_lxml.xpath('//td[@class="update_time"]/span/text()')
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
        info['isk'] = item
        info['system_name'] = names[count]
        info['sec'] = sec[count]
        info['remaining'] = remaining[count]
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