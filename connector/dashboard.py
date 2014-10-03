'''
Created on Jul 29, 2014

@author: rodrigo.abreu
'''

from leftronic import Leftronic
from read_api import CardController, ApiWrapper
import pycurl, simplejson as json
import datetime

update = Leftronic("yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ")
c = pycurl.Curl()
c.setopt(c.VERBOSE, True)
c.setopt(c.URL, 'https://www.leftronic.com/customSend/')


def initialize():
    wrapper = ApiWrapper()
    return wrapper.merge_archived_lists(wrapper.fetch_archived_cards(),
                                  wrapper.fetch_old_archived_cards())

def build_last_week_list(cards_dict):
    last_week_no = max(cards_dict.keys()) - 1
    list_array = []
    for cards in cards_dict[last_week_no]:
        list_array.append(cards.title)

    update.pushList("delivered_last_week", list_array)

def build_archived_by_week_bar_chart(cards_dict):

    point_list = []
    #print cards_dict
    for i in sorted(cards_dict.keys()):
        chart = {}
        start, end = cards_dict[i][0].arch_date_range
        chart["name"] = start.strftime("%d/%m") + ' - ' + end.strftime("%d/%m")
        chart["value"] = len(cards_dict[i])
        today = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        if start <= today and end >= today:
            chart["name"] = "Current Week"
            chart["color"] = "green"
        point_list.append(chart)

    points_json = json.dumps(point_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",'+\
              '"streamName": "delivered_chart", "point": '+\
              '{"chart": '+ points_json + '}}')
    c.perform()

def build_average_lead_time(lead_time):
    update.pushNumber("lead_time", lead_time)

def build_lead_time_table_for_card_type(lt_by_type):
    header = ['Card Type', 'Lead Time']
    rows = [[k,v] for k,v in lt_by_type.iteritems()]
    update.pushTable("type_lead_time", header, rows)

def build_pie_chart_effort_card_types(card_type_efforts):
    update.pushLeaderboard("pie_effort", [{"name": k, "value": v} for \
                                          k,v in card_type_efforts.iteritems()])
    print "building pie chart of efforts by card type"

def build_pie_chart_effort_target(card_tags_effort, filter_tags, stream):
    tags_efforts = [{"name": k, "value": v} for k,v in card_tags_effort.iteritems()\
                     if k in filter_tags]
    update.pushLeaderboard(stream, tags_efforts)
    print "building pie chart of efforts by target"

if __name__ == "__main__":
    wrapper = ApiWrapper()
    archived_cards = wrapper.merge_archived_lists(wrapper.fetch_archived_cards(),
                                  wrapper.fetch_old_archived_cards())
    card_ctrl = CardController(archived_cards)
    cards_dict = card_ctrl.archived_cards_per_week()
    build_last_week_list(cards_dict)
    build_archived_by_week_bar_chart(cards_dict)
    build_average_lead_time(card_ctrl.average_lead_time())
    build_lead_time_table_for_card_type(card_ctrl.card_type_average_lead_time())
    build_pie_chart_effort_card_types(card_ctrl.card_types_effort())
    build_pie_chart_effort_target(card_ctrl.tags_effort(),
                                   ['meta_2014.q4', 'no_target.2014.q4'],
                                   "pie_effort_targets")
    build_pie_chart_effort_target(card_ctrl.tags_effort(),
                                  ['mosaico', 'ego', 'opec_tags', 'feed'],
                                  "important_tags_effort")
