from read_api import LeanKitWrapper
import datetime as dt
import settings as s
from isoweek import Week


class CardController(object):
    def __init__(self, cards_list):
        self.cards_list = cards_list

    def __get_week_range(self, start_week):
        this_week = Week.thisweek()
        week_numbers_list = []
        for i in range(start_week):
            week_numbers_list.append(this_week)
            this_week -= 1

        return week_numbers_list

    def set_cards(self, cards_dict, range_list, key_value, card):
        if key_value not in cards_dict.keys():
            cards_dict[key_value] = []
        if key_value in range_list:
            cards_dict[key_value].append(card)

        return cards_dict

    def archived_cards_per_week_last_six_weeks(self):
        archived_cards = {}
        week_numbers_range = self.__get_week_range(6)
        for card in self.cards_list:
            archived_cards.update(self.set_cards(archived_cards,
                                                 week_numbers_range,
                                                 card.archive_week, card))
            # if card.archive_week in week_numbers_range:
            #     archived_cards[card.archive_week].append(card)
            # else:
            #     archived_cards[card.archive_week] = [card]
            # if card.archive_week not in archived_cards.keys():
            #     archived_cards[card.archive_week] = []

        #         if card.archive_week in archived_cards.keys():
        #             lst = archived_cards[card.archive_week]
        #             lst.append(card)
        #             archived_cards[card.archive_week] = lst
        #         else:
        #             l = [card]
        #             archived_cards[card.archive_week] = l
        # #no card has been archived during this week
        # no_archived_weeks = list(set(week_numbers_range) -
        #                                 set(archived_cards.keys()))
        # for no_archive_week in no_archived_weeks:
        #     archived_cards[no_archive_week] = []

        return archived_cards

    def archived_cards_per_week_current_quarter(self):
        archived_cards = {}
        this_week = Week.thisweek()
        for start_quarter_week in s.quarter_week_numbers:
            if start_quarter_week < this_week < next(s.quarter_week_numbers):
                quarter_weeks = this_week.week - start_quarter_week.week
                #if quarter_weeks <= 13:
                break
            #if this_week > start_quarter_week and quarter_weeks <= 13:
        week_numbers_range = self.__get_week_range(quarter_weeks+1)
        for card in self.cards_list:
            archived_cards.update(self.set_cards(archived_cards,
                                                 week_numbers_range,
                                                 card.archive_week, card))
        # for card in self.cards_list:
        #     if card.archive_week in week_numbers_range:
        #         if card.archive_week in archived_cards.keys():
        #             lst = archived_cards[card.archive_week]
        #             lst.append(card)
        #             archived_cards[card.archive_week] = lst
        #         else:
        #             l = [card]
        #             archived_cards[card.archive_week] = l
        #
        # #no card has been archived during the week
        # no_archived_weeks = list(set(week_numbers_range) -
        #                                 set(archived_cards.keys()))
        # for no_archive_week in no_archived_weeks:
        #     archived_cards[no_archive_week] = []

        return archived_cards

    def archived_cards_by_quarter(self):
        archived_cards = {}
        for card in self.cards_list:
            for quarter, quarter_dates in s.quarter_date_ranges.items():
                if card.archive_date.date() >= quarter_dates[0] and card.archive_date.date() <= quarter_dates[1]:
                    if quarter in archived_cards.keys():
                       # print card.title, card.archive_date.date()
                        archived_cards[quarter].append(card)
                    else:
                       # print card.title, card.archive_date.date()
                        archived_cards[quarter] = [card]

        return archived_cards

    def archived_incidents_by_quarter(self, archived_cards_by_quarter):
        archived_cards = {}
        for quarter in archived_cards_by_quarter.keys():
            for card in archived_cards_by_quarter[quarter]:
                if card.card_type == "Incidente":
                    if quarter in archived_cards.keys():
                       # print card.title, card.archive_date.date()
                        archived_cards[quarter].append(card)
                    else:
                       # print card.title, card.archive_date.date()
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

        # for i,j in archived_incidents.items():
        #     for k in j:
        #         print i, k.epic, k.title, k.archive_date

        return archived_incidents

    def wip_card_count(self, wip_cards_list):
        """
        :param wip_cards_list: 0-backlog, 1-development, 2-to prod
        """
        return {'backlog': len(wip_cards_list[0]),
                'wip': len(wip_cards_list[1]),
                'to_prod': len(wip_cards_list[2])}

    def task_progression(self, wip_cards_list):
        return {'total_tasks': sum(wip_card.total_tasks
                                   for wip_card in wip_cards_list[1]),
                'total_completed_tasks': sum(wip_card.completed_tasks
                                             for wip_card in wip_cards_list[1])}

    def wip_days(self, wip_cards_list):
        old_cards_list = []

        today = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        for card in wip_cards_list[1]:
            card.wip_days = today - card.last_move_date
            old_cards_list.append(card)

        return old_cards_list

if __name__ == "__main__":
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()
    controller = CardController(archive)
    #print controller.archived_cards_per_week_last_six_weeks()
    print controller.archived_cards_per_week_current_quarter()

    #wip = wrapper.fetch_wip_cards()
    #print CardController(None).wip_card_count(wrapper.backlog_cards_list,
    #                                             wip)
    #print CardController(None).task_progression(wip)
    #print backlog_wip_card_count(wrapper.backlog_cards_list, wip)
    # cards_list = wrapper.merge_archived_lists(wrapper.fetch_recent_archived_cards_list(),
    #                                           wrapper.fetch_old_archived_cards_list())
    #CardController(cards_list).archived_cards_by_quarter()
    #CardController(cards_list).archived_cards_per_week_current_quarter()
    #CardController(cards_list).card_types_effort()
    #CardController(cards_list).tags_effort()
    #CardController(x).tags_effort()
