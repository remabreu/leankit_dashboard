from __future__ import division
from leftronic import Leftronic
from read_api import LeanKitWrapper
from controller import CardController
import pycurl
import simplejson as json
import datetime
from isoweek import Week
import settings as s

update = Leftronic("yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ")
c = pycurl.Curl()
c.setopt(c.VERBOSE, True)
c.setopt(c.URL, 'https://www.leftronic.com/customSend/')


def initialize():
    wrapper = LeanKitWrapper()
    return wrapper.merge_archived_lists(wrapper.fetch_recent_archived_cards_list(),
                                        wrapper.fetch_old_archived_cards_list())


def build_last_week_list(cards_dict):
    last_week_no = max(cards_dict.keys()) - 1
    list_array = []
    for cards in cards_dict[last_week_no]:
        list_array.append(cards.title)

    update.pushList("delivered_last_week", list_array)


def build_archived_by_week_bar_chart(cards_dict, stream_name, chart_color):
    points_list = []
    cards_sum = 0
    for arch_week_no in sorted(cards_dict.keys()):
        chart = {}
        chart["name"] = arch_week_no.monday().strftime("%d/%m") + "-" + \
                        arch_week_no.friday().strftime("%d/%m")
        chart["value"] = len(cards_dict[arch_week_no])
        chart["color"] = chart_color
        if arch_week_no == Week.thisweek():
            chart["name"] = "Current"
            chart["color"] = "green"

        cards_sum += len(cards_dict[arch_week_no])
        points_list.append(chart)

    points_json = json.dumps(points_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "' + stream_name + '", "point": ' +
             '{"chart": ' + points_json + '}}')
    c.perform()

    return cards_sum


def build_archived_by_week_multi_bar(cards_dict):
    # {"matrix":[["Years","Barcelona","Real Madrid","Atltico"],
    # ["2010",95,102,62],["2011",114,121,53],["2012",115,103,65],["2013",100,104,77]]}

    bar = [["Week", "Target", "No Target"]]
    for arch_week_no in sorted(cards_dict.keys()):
        points = []
        week_range_str = arch_week_no.monday().strftime("%d/%m") + "-" + \
                         arch_week_no.friday().strftime("%d/%m")
        cards = cards_dict[arch_week_no]
        points.append(week_range_str)
        target = 0
        no_target = 0
        incidents = 0
        for card in cards:
            if "target_q2.2015" in card.tags:
                target += 1
            elif "no_target_q2.2015" in card.tags:
                no_target += 1
            else:
                print "Card sem Tag: ", card.title
        points.extend([target, no_target, incidents])
        bar.append(points)

    bar_json = json.dumps(bar)
    update.clear('target-archive')

    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "target-archive", "point": {"matrix": ' + bar_json + '}}')
    c.perform()


def build_cpd_number(stream_name, cards_dict):
    days = len(cards_dict.keys()) * 5  #number of weeks multiplied by 5 days
    average = sum([len(cards_dict[x]) for x in cards_dict.keys()]) / days
    update.pushNumber(stream_name, average)

    #for arch_week in cards_dict.keys():
    #    print len(cards_dict[arch_week])
    # print "DIAS", days
    # print "SUM CARDS", cards_sum
    # update.pushNumber(stream_name, cards_sum / days)


def build_average_lead_time(lead_time):
    update.pushNumber("lead_time", lead_time)


def build_lead_time_table_for_card_type(lt_by_type):
    header = ['Card Type', 'Lead Time']
    rows = [[k, v] for k, v in lt_by_type.iteritems()]
    update.pushTable("type_lead_time", header, rows)


def build_pie_chart_effort_card_types(card_type_efforts):
    update.pushLeaderboard("pie_effort", [{"name": k, "value": v} for \
                                          k, v in card_type_efforts.iteritems()])
    print "building pie chart of efforts by card type"


def build_pie_chart_effort_target(card_tags_effort, filter_tags, stream):
    tags_efforts = [{"name": k, "value": v} for k, v in card_tags_effort.iteritems() \
                    if k in filter_tags]
    update.pushLeaderboard(stream, tags_efforts)
    print "building pie chart of efforts by target"


def build_backlog_wip_toprod_chart(wip_counts):
    update.pushNumber("line_dev", wip_counts['wip'])
    update.pushNumber("line_backlog", wip_counts['backlog'])
    update.pushNumber("line_to_prod", wip_counts['to_prod'])


# import random, time
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


def build_table_wips(cards_list):
    header_list = ['Card', 'Epic', 'Days In Process']
    rows_list = []
    for card in cards_list:
        if card.lane_title in s.wip_dev:
            duration = datetime.date.today() - card.last_move_date.date()
            row = [card.title, card.epic, str(duration.days)]
            rows_list.append(row)

    update.pushTable("wip_days_table", header_list, rows_list)


# def build_archived_count_vertical_bar(archived_cards_by_week_in_quarter):
#     update.pushNumber("archive_count",
#                       sum([len(x) for x in archived_cards_by_week_in_quarter.values()]))


def build_archived_by_quarter_bar_chart(quarters_dict):
    points_list = []
    for quarter in quarters_dict.keys():
        chart = {}
        chart['name'] = quarter
        chart['color'] = "yellow"
        chart['value'] = len(quarters_dict[quarter])
        points_list.append(chart)

    points_json = json.dumps(points_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "archived_by_quarter_bar_chart", "point": ' +
             '{"chart": ' + points_json + '}}')
    c.perform()


def build_archived_incidents_by_week_bar_chart(archived_incidents):
    points_list = []
    for arch_week_no in sorted(archived_incidents.keys()):
        chart = {'name': arch_week_no.monday().strftime("%d/%m") + "-" + \
                         arch_week_no.friday().strftime("%d/%m"),
                 'color': "red",
                 'value': len(archived_incidents[arch_week_no])}
        points_list.append(chart)
        #print chart['name'], chart['value']

    points_json = json.dumps(points_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "weekly_incidents_by_chart", "point": ' +
             '{"chart": ' + points_json + '}}')
    c.perform()

    #update.pushLeaderboard("archived_by_quarter_bar_chart", chart)


def build_archived_incidents_by_quarter_bar_chart(quarter_incidents):
    points_list = []
    for quarter in sorted(quarter_incidents.keys()):
        chart = {}
        chart['name'] = quarter
        chart['color'] = "red"
        chart['value'] = len(quarter_incidents[quarter])
        points_list.append(chart)
        print chart['name'], chart['value']

    points_json = json.dumps(points_list)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "quarter_incidents_bar_chart", "point": ' +
             '{"chart": ' + points_json + '}}')
    c.perform()


def build_wip_dial(wip_cards):

    #total_wip = wip_counts['wip'] + wip_counts['backlog'] + wip_counts['to_prod']
    update.pushNumber("current_wip_dial", len(wip_cards))

def build_queue_sizes_bar_chart(wip_cards):
    queues = {}
    for card in wip_cards:
        if card.lane_title == "Current Sprint Backlog":
            queues.update({"Sprint Backlog": queues.get("Sprint Backlog", 0) + 1})
        elif card.lane_title == "Dev. Done" or card.lane_title == "TO PROD":
            queues.update({card.lane_title: queues.get(card.lane_title, 0) + 1})
    chart = []
    for key in queues.keys():
        chart.append({"name": key, "value": queues[key], "color": "purple"})
    print "Submitting a JSON"
    print chart
    points_json = json.dumps(chart)
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "queue_sizes_bar", "point": ' +
             '{"chart": ' + points_json + '}}')
    c.perform()

def build_target_effort_pie_chart(no_tagert, target):
    efforts = [{"name": "No Target", "value": no_tagert},
               {"name": "Target", "value": target}]
    update.pushLeaderboard("effort_pie", efforts)

def build_average_cycle_time_number(cycle_time):
    update.pushNumber("average_cycle_time", cycle_time)

def build_instant_tp_number(wip, cycle_time):
    update.pushNumber("instant_tp", wip/cycle_time)


if __name__ == "__main__":
    # wrapper = LeanKitWrapper()
    # archived_cards = wrapper.get_archived_cards(wrapper.fetch_recent_archived_cards_list(),
    #                                wrapper.fetch_old_archived_cards_list())
    # card_ctrl = CardController(archived_cards)
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()
    card_ctrl = CardController(archive)

    no_target, target = card_ctrl.targets_effort(archive)
    build_target_effort_pie_chart(no_target, target)
    avg_cycle_time = card_ctrl.average_cycle_time(archive)
    build_average_cycle_time_number(avg_cycle_time)

    wip_cards_list = wrapper.get_wip_cards()
    #print wip_cards_list
    build_wip_dial(wip_cards_list)
    build_table_wips(wip_cards_list)
    build_queue_sizes_bar_chart(wip_cards_list)
    build_instant_tp_number(len(wip_cards_list),avg_cycle_time)



    cards_dict = card_ctrl.archived_cards_per_week_last_six_weeks()
    #cards_count = build_archived_by_week_bar_chart(cards_dict, "delivered_chart", "purple")
    build_archived_by_week_multi_bar(cards_dict)
    build_cpd_number("cpd_six_weeks", cards_dict)

    #cards_dict = card_ctrl.archived_cards_per_week_current_quarter()
    #cards_count = build_archived_by_week_bar_chart(cards_dict,
    #                                               "quarter_throughput_bar_chart", "blue")
    #    cards_per_day("cpd_quarter", cards_count)
    #build_archived_count_vertical_bar(cards_dict)
    archived_incidents = card_ctrl.archived_incidents_by_week(cards_dict)
    build_archived_incidents_by_week_bar_chart(archived_incidents)

    quarter_cards_dict = card_ctrl.archived_cards_by_quarter()
    build_archived_by_quarter_bar_chart(quarter_cards_dict)

    quarter_weeks_cards_dict = card_ctrl.archived_cards_per_week_current_quarter()
    build_cpd_number("cpd_quarter", quarter_weeks_cards_dict)
    #build_archived_by_quarter_bar_chart(quarter_cards_dict)

    #quarter_incidents = card_ctrl.archived_incidents_by_quarter(quarter_cards_dict)
    #build_archived_incidents_by_quarter_bar_chart(quarter_incidents)





#     build_average_lead_time(card_ctrl.average_lead_time())
#     build_lead_time_table_for_card_type(card_ctrl.card_type_average_lead_time())
#     build_pie_chart_effort_card_types(card_ctrl.card_types_effort())
#    build_pie_chart_effort_target(card_ctrl.tags_effort(),
#                                    ['meta_2014.q4', 'no_target.2014.q4'],
#                                   "pie_effort_targets")
#     build_pie_chart_effort_target(card_ctrl.tags_effort(),
#                                   ['mosaico', 'ego', 'opec_tags', 'feed'],
#                                   "important_tags_effort")

#     build_backlog_wip_toprod_chart(card_ctrl.wip_card_count(wip_cards_list))
    #build_wip_dial(card_ctrl.wip_card_count(wip_cards_list))
#     build_tasks_line_chart(card_ctrl.task_progression(wip_cards_list))
# #    build_leaderboard_old_wips(card_ctrl.wip_days(wip_cards_list))
#     build_table_wips(card_ctrl.wip_days(wip_cards_list))
