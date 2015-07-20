from __future__ import division
from leftronic import Leftronic
from read_api import LeanKitWrapper
from archive_controller import CardArchiveController
import pycurl
import simplejson as json
import datetime
from isoweek import Week
import settings as s

_update = Leftronic("yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ")
c = pycurl.Curl()
c.setopt(c.VERBOSE, True)
c.setopt(c.URL, 'https://www.leftronic.com/customSend/')

def build_archived_by_week_multi_bar(archived_cards_dict):
    """

    :param archived_cards_dict:
    """
    bar = [["Week", "Target", "No Target", "Incidents"]]
    for arch_week_no in sorted(archived_cards_dict.keys()):
        points = []
        week_range_str = arch_week_no.monday().strftime("%d/%m") + "-" + \
                         arch_week_no.friday().strftime("%d/%m")
        cards = archived_cards_dict[arch_week_no]
        points.append(week_range_str)
        target = 0
        no_target = 0
        incidents = 0
        for card in cards:
            if card.card_type == "Incidente/Bug":
                incidents += 1
            else:
                for tag in card.tags:
                    if tag.startswith("target"):
                        target += 1
                        break
                    elif tag.startswith("no_target") and card.card_type is not "Incidente/Bug":
                        no_target += 1
                        break
            if target == 0 and no_target == 0:
                print "Card sem Tag: ", card.title, card.archive_week, card.archive_date
        points.extend([target, no_target, incidents])
        bar.append(points)

    bar_json = json.dumps(bar)
    _update.clear('target-archive')

    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "target-archive", "point": {"matrix": ' + bar_json + '}}')
    c.perform()


def build_archived_incindets_per_week_number(archived_incidents_per_week):
    weeks = len(archived_incidents_per_week.keys())
    average = sum([len(archived_incidents_per_week[k]) for k in archived_incidents_per_week.keys()])/weeks
    print "AVERAGE: ", average
    _update.pushNumber('incents_per_week_6_weeks', average)


def build_archived_cards_per_week_number(archived_cards_last_six_weeks):
    cards_count = 0
    weeks = len(archived_cards_last_six_weeks.keys())
    for week in archived_cards_last_six_weeks.keys():
        for card in archived_cards_last_six_weeks[week]:
            if card.card_type is not "Incidente/Bug":
                cards_count += 1

    average = cards_count / weeks
    # average = sum([len([card for card in archived_cards_last_six_weeks[x]
    #                     if card.card_type is not "Incidente/Bug"])
    #               for x in archived_cards_last_six_weeks.keys()]) / weeks
    print "AVERAGE: ", average
    _update.pushNumber("cpw_six_weeks", average)


def build_archived_cards_per_day_in_quarter(archived_cards_in_quarter_list):
    today = datetime.datetime.today()
    days_in_quarter = today - s.quarters["Q3.2015"][0]

    _update.pushNumber("cpd_quarter", len([card for card in archived_cards_in_quarter_list if
                                          card.card_type is not "Incidente/Bug"])/days_in_quarter.days)


def build_table_wips(wip_cards_list):
    header_list = ['Card', 'Epic', 'Days In Process']
    rows_list = []
    for card in wip_cards_list:
        if card.lane_title in "In Progress":
            duration = datetime.date.today() - card.last_move_date.date()
            row = [card.title, card.epic, str(duration.days)]
            rows_list.append(row)

    _update.pushTable("wip_days_table", header_list, rows_list)


def build_toprod_average_waiting_time_number(wip_cards_list):
    total_duration = card_count = 0
    for card in wip_cards_list:
        if card.lane_title in "To Prod":
            total_duration += (datetime.date.today() - card.last_move_date.date()).days
            card_count += 1

    average_waiting_time = total_duration/card_count if card_count > 0 else 0
    point_list = {"number": average_waiting_time, "suffix": " Days"}

    points_json = json.dumps(point_list)
    print points_json
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "toprod_waiting_average_number", "point": ' + points_json + '}')
    c.perform()

    #_update.pushNumber("toprod_waiting_average_number", total_duration/card_count if card_count > 0 else 0)



def build_archived_by_quarter_bar_chart(quarters_dict):
    points_list = []
    for quarter in quarters_dict.keys():
        chart = dict()
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


def build_target_effort_pie_chart(archived_cards_list_in_quarter):
    no_target_effort = target_effort = incident_effort = datetime.timedelta(0)

    for card in archived_cards_list_in_quarter:
        if card.card_type == "Incidente/Bug":
            incident_effort += card.cycle_time
        else:
            for tag in card.tags:
                if tag.startswith("target"):
                    target_effort += card.cycle_time
                    break
                elif tag.startswith("no_target") and card.card_type is not "Incidente/Bug":
                    no_target_effort += card.cycle_time
                    break
            if target_effort == 0 and no_target_effort == 0:
                print "Card sem Tag: ", card.title, card.archive_week, card.archive_date

    print "EFFORTS", no_target_effort, target_effort, incident_effort
    efforts = [{"name": "No Target", "value": no_target_effort.total_seconds()},
               {"name": "Target", "value": target_effort.total_seconds()},
               {"name": "Incidents", "value": incident_effort.total_seconds()}]
    _update.pushLeaderboard("effort_pie", efforts)


def build_incidents_per_day_in_quarter(archived_cards_list_in_quarter):
    inc_count = 0
    today = datetime.datetime.today()
    days_in_quarter = today - s.quarters["Q3.2015"][0]

    # for card in archived_cards_list_in_quarter:
    #     if card.card_type == "Incidente/Bug":
    #         inc_count += 1
    inc_count = len([card for card in archived_cards_list_in_quarter if card.card_type == "Incidente/Bug"])

    # point_list = {"number": inc_count/days_in_quarter.days, "suffix": "ipd"}
    #
    # points_json = json.dumps(point_list)
    # print points_json
    # c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
    #          '"streamName": "incidents_per_day_in_quarter", "point": ' + points_json + '}')
    # c.perform()
    _update.pushNumber("incidents_per_day_in_quarter", inc_count/days_in_quarter.days)


def build_average_cycle_time_number(archived_cards_list_in_quarter):
    total_cycle_time = datetime.timedelta(0)
    for card in archived_cards_list_in_quarter:
        total_cycle_time += card.cycle_time

    average_cycle_time = total_cycle_time.days / len(archived_cards_list_in_quarter)
    point_list = {"number": average_cycle_time, "suffix": "Days"}

    points_json = json.dumps(point_list)
    print points_json
    c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
             '"streamName": "average_cycle_time", "point": ' + points_json + '}')
    c.perform()
    #cycle_time = sum([card.cycle_time for card in archived_cards_list_in_quarter])/\
    #             len(archived_cards_list_in_quarter)
    #_update.pushNumber("average_cycle_time", average_cycle_time, "prefix", )


def build_wip_sparkline(wip_cards_list):
    #_update.clear("wip_spark")
    # point_list = {"number": len(wip_cards_list), "suffix": "Cards"}
    #
    # points_json = json.dumps(point_list)
    # print points_json
    # c.setopt(c.POSTFIELDS, '{"accessKey": "yRtMi1VBjechqkFIpdTiEOzoGhkSu2lZ",' +
    #          '"streamName": "wip_spark", "point": ' + points_json + '}')
    # c.perform()

    _update.pushNumber("wip_spark", len(wip_cards_list))

if __name__ == "__main__":
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()
    wip = wrapper.get_wip_cards()
    cac = CardArchiveController(archive, wip, "ESP1")

    archived_cards_by_week = cac.group_cards_by_week()
    archived_in_six_weeks = cac.filter_cards_by_last_6_weeks(archived_cards_by_week)
    build_archived_by_week_multi_bar(archived_in_six_weeks)
    build_archived_cards_per_week_number(archived_in_six_weeks)

    archived_incidents = cac.filter_incidents_by_week(archived_cards_by_week)

    archived_incs_six_weeks = cac.filter_cards_by_last_6_weeks(archived_incidents)
    build_archived_incidents_by_week_bar_chart(archived_incs_six_weeks)
    build_archived_incindets_per_week_number(archived_incs_six_weeks)

    archived_cards_by_quarter = cac.group_cards_by_quarter()
    build_archived_by_quarter_bar_chart(archived_cards_by_quarter)
    build_target_effort_pie_chart(archived_cards_by_quarter["Q3.2015"])
    build_average_cycle_time_number(archived_cards_by_quarter["Q3.2015"])
    build_archived_cards_per_day_in_quarter(archived_cards_by_quarter["Q3.2015"])
    build_incidents_per_day_in_quarter(archived_cards_by_quarter["Q3.2015"])

    build_wip_sparkline(cac.wip_cards_by_team)
    build_table_wips(cac.wip_cards_by_team)
    build_toprod_average_waiting_time_number(cac.wip_cards_by_team)