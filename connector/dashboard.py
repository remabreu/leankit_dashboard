from __future__ import division
from leftronic import Leftronic
from read_api import ApiWrapper
from controller import CardController
import pycurl
import simplejson as json
import datetime
from isoweek import Week

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

def build_archived_by_week_bar_chart(cards_dict, stream_name):
    points_list = []
    cards_sum = 0
    for arch_week_no in sorted(cards_dict.keys()):
        chart = {}
        chart["name"] = arch_week_no.monday().strftime("%d/%m") + "-" + \
                            arch_week_no.friday().strftime("%d/%m")
        chart["value"] = len(cards_dict[arch_week_no])
        if arch_week_no == Week.thisweek():
            chart["name"] = "Current"
            chart["color"] = "green"

        cards_sum += len(cards_dict[arch_week_no])
        points_list.append(chart)

    points_json = json.dumps(points_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
              '"streamName": "'+ stream_name +'", "point": ' +
              '{"chart": '+ points_json + '}}')
    c.perform()

    days = len(cards_dict.keys()) * 5
    print "DIAS", days
    print "SUM CARDS", cards_sum
    update.pushNumber("cards_per_day", cards_sum/days)

def build_average_lead_time(lead_time):
    update.pushNumber("lead_time", lead_time)

def build_lead_time_table_for_card_type(lt_by_type):
    header = ['Card Type', 'Lead Time']
    rows = [[k, v] for k, v in lt_by_type.iteritems()]
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

def build_backlog_wip_toprod_chart(wip_counts):
    update.pushNumber("line_wip", wip_counts['wip'])
    update.pushNumber("line_backlog", wip_counts['backlog'])
    update.pushNumber("line_to_prod", wip_counts['to_prod'])

#    import random, time
#     for i in range(30):
#         back_number = random.randrange(0, 101, 2)
#         wip_number = random.randrange(0, 101, 2)
#         update.pushNumber("line_wip", wip_number)
#         update.pushNumber("line_backlog", back_number)
#         time.sleep(3)

def build_tasks_line_chart(tasks):
    update.pushNumber("tasks_done", tasks['total_completed_tasks'])
    update.pushNumber("tasks_total", tasks['total_tasks'])

def build_leaderboard_old_wips(old_cards_list):
    leader_list = []
    leader = {}
    for card in old_cards_list:
        if card['days'] > datetime.timedelta(days=4) and card['lane_title'] == "Doing":
            leader['name'] = card['card_title'] + "(in Doing)"
            leader['value'] = card['days'].days
        elif card['days'] > datetime.timedelta(days=7):
            leader['name'] = card['card_title'] + "(in " + leader['lane_title'] + ")"
            leader['value'] = card['days'].days
        leader_list.append(leader)

    update.pushLeaderboard("old_wip", leader_list)


def build_table_wips(old_cards_list):
    header_list = ['Card', 'Epic', 'Column', 'Days']
    rows_list = []
    for card in old_cards_list:
        row = [card.title, card.epic, card.lane_title, card.wip_days.days]
        rows_list.append(row)

    update.pushTable("wip_days_table", header_list, rows_list)

if __name__ == "__main__":
    wrapper = ApiWrapper()
    archived_cards = wrapper.merge_archived_lists(wrapper.fetch_archived_cards(),
                                   wrapper.fetch_old_archived_cards())
    card_ctrl = CardController(archived_cards)
    cards_dict = card_ctrl.archived_cards_per_week_last_six_weeks()
    build_archived_by_week_bar_chart(cards_dict, "delivered_chart")
    cards_dict = card_ctrl.archived_cards_per_week_current_quarter()
#     build_last_week_list(cards_dict)

    build_archived_by_week_bar_chart(cards_dict, "bar_test")
#     build_average_lead_time(card_ctrl.average_lead_time())
#     build_lead_time_table_for_card_type(card_ctrl.card_type_average_lead_time())
#     build_pie_chart_effort_card_types(card_ctrl.card_types_effort())
#    build_pie_chart_effort_target(card_ctrl.tags_effort(),
#                                    ['meta_2014.q4', 'no_target.2014.q4'],
#                                   "pie_effort_targets")
#     build_pie_chart_effort_target(card_ctrl.tags_effort(),
#                                   ['mosaico', 'ego', 'opec_tags', 'feed'],
#                                   "important_tags_effort")
    wip_cards_list = wrapper.fetch_wip_cards()
    build_backlog_wip_toprod_chart(card_ctrl.wip_card_count(wip_cards_list))
    build_tasks_line_chart(card_ctrl.task_progression(wip_cards_list))
#    build_leaderboard_old_wips(card_ctrl.wip_days(wip_cards_list))
    build_table_wips(card_ctrl.wip_days(wip_cards_list))