from read_api import ApiWrapper
import datetime, settings as s
from isoweek import Week


class CardController(object):
    def __init__(self, cards_list):
        self.cards_list = cards_list

    def get_week_range(self, start_week):
        this_week = Week.thisweek()
        week_numbers_list = []
        for i in range(start_week):
            week_numbers_list.append(this_week)
            this_week -= 1

        return week_numbers_list

    def archived_cards_per_week_last_six_weeks(self):
        archived_cards = {}
        week_numbers_range = self.get_week_range(6)
        for card in self.cards_list:
            if card.archive_week in week_numbers_range:
                if card.archive_week in archived_cards.keys():
                    lst = archived_cards[card.archive_week]
                    lst.append(card)
                    archived_cards[card.archive_week] = lst
                else:
                    l = [card]
                    archived_cards[card.archive_week] = l
        #no card has been archived during this week
        no_archived_weeks = list(set(week_numbers_range) - \
                                        set(archived_cards.keys()))
        for no_archive_week in no_archived_weeks:
            archived_cards[no_archive_week] = []

        return archived_cards

    def archived_cards_per_week_current_quarter(self):
        archived_cards = {}
        this_week = Week.thisweek()
        for start_quarter_week in s.quarter_week_numbers:
            quarter_weeks = this_week.week - start_quarter_week.week

            if this_week > start_quarter_week and quarter_weeks <= 13:
                week_numbers_range = self.get_week_range(quarter_weeks+1)
                for card in self.cards_list:
                    if card.archive_week in week_numbers_range:
                        if card.archive_week in archived_cards.keys():
                            lst = archived_cards[card.archive_week]
                            lst.append(card)
                            archived_cards[card.archive_week] = lst
                        else:
                            l = [card]
                            archived_cards[card.archive_week] = l
                #no card has been archived during this week
                no_archived_weeks = list(set(week_numbers_range) - \
                                                set(archived_cards.keys()))
                for no_archive_week in no_archived_weeks:
                    archived_cards[no_archive_week] = []

        return archived_cards





        for card in self.cards_list:
            if card.archive_week in week_numbers_range:
                if card.archive_week in archived_cards.keys():
                    lst = archived_cards[card.archive_week]
                    lst.append(card)
                    archived_cards[card.archive_week] = lst
                else:
                    l = [card]
                    archived_cards[card.archive_week] = l
        #no card has been archived during this week
        no_archived_weeks = list(set(week_numbers_range) - \
                                        set(archived_cards.keys()))
        for no_archive_week in no_archived_weeks:
            archived_cards[no_archive_week] = []

        return archived_cards


    def average_lead_time(self):
        lt = 0
        for card in self.cards_list:
            lt = lt + card.lead_time.days

        return lt/len(self.cards_list)

    def card_type_average_lead_time(self):
        d = {}
        for card in self.cards_list:
            if card.card_type in d.keys():
                lt = d[card.card_type][0] + card.lead_time.days
                count = d[card.card_type][1] + 1
                d[card.card_type] = (lt, count)
            else:
                d[card.card_type] = (card.lead_time.days, 1)

        return dict([(k,v[0]/v[1]) for k,v in d.iteritems()])

    def tags_effort(self):
        d = {}
        for card in self.cards_list:
            if card.tags:
                tags_lst = card.tags.split(',')
                for tag in tags_lst:
                    if tag in d.keys():
                        d[tag] += card.lead_time.days
                    else:
                        d[tag] = card.lead_time.days

        return d

    def card_types_effort(self):
        effort_per_card_type_dict = {}
        for card in self.cards_list:
            if card.card_type in effort_per_card_type_dict.keys():
                effort_per_card_type_dict[card.card_type] += card.lead_time.days
            else:
                effort_per_card_type_dict[card.card_type] = card.lead_time.days

        return effort_per_card_type_dict

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
        old_cards_dict = {}
        today = datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
        for card in wip_cards_list[1]:
            date_diff = today - card.last_move_date
            if date_diff >= datetime.timedelta(days=1):
                card.wip_days = date_diff
            else:
                card.days = 0

            old_cards_list.append(card)

        return old_cards_list

if __name__ == "__main__":
    wrapper = ApiWrapper()
    #wip = wrapper.fetch_wip_cards()
    #print CardController(None).wip_card_count(wrapper.backlog_cards_list,
    #                                             wip)
    #print CardController(None).task_progression(wip)
    #print backlog_wip_card_count(wrapper.backlog_cards_list, wip)
    cards_list = wrapper.merge_archived_lists(wrapper.fetch_archived_cards(),
                                              wrapper.fetch_old_archived_cards())
    CardController(cards_list).archived_cards_per_week_current_quarter()
    #CardController(cards_list).card_types_effort()
    #CardController(cards_list).tags_effort()
    #CardController(x).tags_effort()
