# -*- coding: utf-8 -*-
from read_api import LeanKitWrapper
import datetime as dt
import settings as s
import collections
from isoweek import Week
from bisect import bisect


class CardArchiveController(object):

    def __init__(self, cards_list):
        self.cards_archive_list = cards_list


    def filter_cards_by_team(self, team): #ESP1 or ESP2
        archived_cards_by_team = []
        for card in self.cards_archive_list:
            if card.team == team:
                archived_cards_by_team.append(card)

        return {team: archived_cards_by_team}

    def group_cards_by_week(self):
        cards_by_week_ditc = {}
        for card in self.cards_archive_list:
            if card.archive_week in cards_by_week_ditc:
                cards_by_week_ditc[card.archive_week].append(card)
            else:
                cards_by_week_ditc[card.archive_week] = []

        return collections.OrderedDict(cards_by_week_ditc)

    def filter_incidents_by_week(self, cards_by_week_ditc):
        incidents_by_week = {}
        for week, archived_cards_list_in_week in cards_by_week_ditc.iteritems():
            incidents_by_week.update(week,
                                      [card for card in archived_cards_list_in_week
                                       if card.card_type == "Incidente/Bug"])

        return incidents_by_week

    def group_cards_by_quarter(self):
        for card in self.cards_archive_list:


    def filter_cards_by_current_quarter(self):
        pass

    def filter_cards_by_last_6_weeks(self):
        pass






    def __get_week_range(self, start_week):
        this_week = Week.thisweek()
        week_numbers_list = []
        for i in range(start_week):
            week_numbers_list.append(this_week)
            this_week -= 1

        return week_numbers_list

    def __get_current_quarter(self, month, day):
        return s.quarters[bisect(s.quarters,(month,day)) - 1][2]

    def __set_cards(self, cards_dict, range_list, key_value, card):
        if key_value not in cards_dict.keys():
            cards_dict[key_value] = []
        if key_value in range_list:
            cards_dict[key_value].append(card)

        return cards_dict

    def archived_cards_per_week_last_six_weeks(self):
        archived_cards = {}
        week_numbers_range = self.__get_week_range(6)
        for card in self.cards_archive_list:
            archived_cards.update(self.__set_cards(archived_cards,
                                                 week_numbers_range,
                                                 card.archive_week, card))

        return archived_cards

    def archived_cards_per_week_current_quarter(self):
        archived_cards = {}
        this_week = Week.thisweek()
        for start_quarter_week in s.quarter_week_numbers:
            if start_quarter_week < this_week < next(s.quarter_week_numbers):
                quarter_weeks = this_week.week - start_quarter_week.week
                break
        week_numbers_range = self.__get_week_range(quarter_weeks+1)
        for card in self.cards_archive_list:
            if card.archive_week in week_numbers_range:
                cards_in_week = archived_cards.get(card.archive_week, [])
                cards_in_week.append(card)
                archived_cards.update({card.archive_week: cards_in_week})

        return archived_cards


    def archived_cards_by_quarter(self):
        archived_cards = {}
        for card in self.cards_archive_list:
            quarter = self.__get_current_quarter(card.archive_date.month, card.archive_date.day)
            cards_in_quarter = archived_cards.get(quarter, [])
            cards_in_quarter.append(card)
            archived_cards.update({quarter: cards_in_quarter})

        return archived_cards

    def archived_incidents_by_quarter(self, archived_cards_by_quarter):
        archived_cards = {}
        for quarter in archived_cards_by_quarter.keys():
            for card in archived_cards_by_quarter[quarter]:
                if card.card_type == "Incidente":
                    if quarter in archived_cards.keys():
                        archived_cards[quarter].append(card)
                    else:
                        archived_cards[quarter] = [card]
                if quarter not in archived_cards.keys():
                    archived_cards[quarter] = []

        return archived_cards


    def archived_incidents_by_week(self, archived_cards_by_week):
        archived_incidents = {}
        for week_number in archived_cards_by_week.keys():
            if len(archived_cards_by_week[week_number]) > 0:
                for card in archived_cards_by_week[week_number]:
                    if card.card_type == "Incidente":
                        if week_number in archived_incidents.keys():
                            archived_incidents[week_number].append(card)
                        else:
                            archived_incidents[week_number] = [card]
                if week_number not in archived_incidents.keys():
                    archived_incidents[week_number] = []
            else:
                archived_incidents[week_number] = []

        return archived_incidents

    def targets_effort(self, archived_cards):
        no_target_effort = target_effort = 0
        for card in archived_cards:
            if "target_q2.2015" in card.tags:
                target_effort += card.cycle_time
            elif "no_target_q2.2015" in card.tags:
                no_target_effort += card.cycle_time

        print "EFFORTS", no_target_effort, target_effort
        return no_target_effort, target_effort

    def card_types_effort(self,archived_cards):
        card_types_cycle_time = {}
        for card in archived_cards:
            cycle_time = 0
            if "tag_manager" in card.tags:
                #print card.title, card.cycle_time
                cycle_time = card_types_cycle_time.get(card.card_type, 0) + card.cycle_time
                card_types_cycle_time.update({card.card_type: cycle_time})

        print card_types_cycle_time

    def no_target_card_types_effort(self,archived_cards):
        card_types_cycle_time = {}
        for card in archived_cards:
            cycle_time = 0
            if "no_target_q2.2015" in card.tags:
                #print card.title, card.cycle_time
                cycle_time = card_types_cycle_time.get(card.card_type, 0) + card.cycle_time
                card_types_cycle_time.update({card.card_type: cycle_time})

        print card_types_cycle_time

    def average_cycle_time(self, archived_cards):
        print sum([card.cycle_time for card in archived_cards])/len(archived_cards)
        return sum([card.cycle_time for card in archived_cards])/len(archived_cards)

    def print_archived_from_date(self, archived_cards):
        last_archive_date = dt.datetime(2015, 5, 6)
        for card in archived_cards:
            if card.archive_date > last_archive_date:
                s0 = (card.epic).encode('utf-8', 'replace')
                s1 = (card.card_type).encode('utf-8', 'replace')
                s2 = (card.title).encode('utf-8', 'replace')
                print "{0},{1},{2}".format(s0,s1,s2)
                #print card.epic, card.title, card.card_type, card.archive_date

if __name__ == "__main__":
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()

    cc = CardArchiveController(archive)
    #cc.print_archived_from_date(archive)
    # print "Card types efforts"
    cc.card_types_effort(archive)
    print
    print "No Target Card Types Effort"
    cc.no_target_card_types_effort(archive)


