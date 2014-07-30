'''
Created on Jul 29, 2014

@author: rodrigo.abreu
'''

from leftronic import Leftronic
from read_api import CardController, ApiWrapper
import pycurl, json

update = Leftronic("yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ")
c = pycurl.Curl()
c.setopt(c.VERBOSE, True)
c.setopt(c.URL, 'https://www.leftronic.com/customSend/')


def initialize():
    wrapper = ApiWrapper().create_archived_cards()
    return CardController(wrapper).archived_cards_per_week()

def build_last_week_list(cards_dict):
    last_week_no = max(cards_dict.keys()) - 1
    list_array = []
    for cards in cards_dict[last_week_no]:
        list_array.append(cards.title)

    update.pushList("delivered_last_week", list_array)

def build_archived_by_week_bar_chart(cards_dict):

    point_list = []
    #print cards_dict
    for i in cards_dict.keys():
        chart = {}
        start, end = cards_dict[i][0].arch_date_range
        chart["name"] = start.strftime("%d/%m") + ' - ' + end.strftime("%d/%m")
        print chart["name"]
        chart["value"] = len(cards_dict[i])
        #chart["color"] = "red"
        point_list.append(chart)

    points_json = json.dumps(point_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",'+\
              '"streamName": "delivered_chart", "point": '+\
              '{"chart": '+ points_json + '}}')
    c.perform()

if __name__ == "__main__":
    cards_dict = initialize()
    build_last_week_list(cards_dict)
    build_archived_by_week_bar_chart(cards_dict)
