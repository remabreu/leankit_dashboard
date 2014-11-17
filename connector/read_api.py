# -*- coding: utf-8 -*-

from __future__ import division
import slumber, settings as s
from datetime import datetime as dt
# from datetime import timedelta
from isoweek import Week


class ApiWrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))

    def fetch_archived_cards(self):
        reply_data_archive = self.api.board(s.j1_board).archive.get()["ReplyData"][0][0]["Lane"]["Cards"]
        cards_list = []
        for i in reply_data_archive:
            reply_answer = self.api.board(s.j1_board).getcard(i["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                cards_list.append(self.get_lk_card(reply_answer["ReplyData"][0]))

        return cards_list

    def fetch_old_archived_cards(self):
        reply_data = self.api.board("113658644").searchcards. \
            post(s.search_options_for_old_archive)["ReplyData"][0]['Results']
        cards_list = []
        # print reply_data
        for i in reply_data:
            reply_answer = self.api.board(s.j1_board).getcard(i["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                cards_list.append(self.get_lk_card(reply_answer["ReplyData"][0]))

        return cards_list

    def merge_archived_lists(self, recent_archive, old_archive):
        complete_archive = []
        for i in recent_archive:
            for j in old_archive:
                if i == j and i not in complete_archive:
                    complete_archive.append(i)
                elif i != j:
                    if i not in complete_archive:
                        complete_archive.append(i)
                    elif j not in complete_archive:
                        complete_archive.append(j)
        return complete_archive

    def __fetch_backlog_cards_list(self, reply_data):
        for backlog_lane in reply_data['Backlog']:
            if backlog_lane['Title'] == 'Next':
                return backlog_lane['Cards']

    def __fetch_development_cards_list(self, reply_data):
        wip_card_list = []
        for lane in reply_data['Lanes']:
            if lane['Title'] in s.work_wip and \
                    str(lane['ParentLaneId']) != s.development_lane and \
                    len(lane['Cards']) > 0:
                cards = lane['Cards']
                for card in cards:
                    reply_answer = self.api.board(s.j1_board).getcard(card["Id"]).get()
                    if reply_answer["ReplyCode"] == 200:
                        wip_card_list.append(self.get_lk_card(reply_answer["ReplyData"][0]))

        return wip_card_list

    def __fetch_to_prod_cards_list(self, reply_data):
        for lane in reply_data['Lanes']:
            if lane['Title'] == 'TO PROD':
                return lane['Cards']

    def fetch_wip_cards(self):
        reply_data = self.api.boards(s.j1_board).get()["ReplyData"][0]

        backlog_cards_list = self.__fetch_backlog_cards_list(reply_data)
        development_cards_list = self.__fetch_development_cards_list(reply_data)
        to_prod_cards_list = self.__fetch_to_prod_cards_list(reply_data)

        return [backlog_cards_list, development_cards_list, to_prod_cards_list]

    def get_lk_card(self, lk_card):
        return Card(id=lk_card["Id"],
                    title=lk_card["Title"],
                    lane_title=lk_card["LaneTitle"],
                    epic=lk_card["ExternalCardID"],
                    create_date=dt.strptime(lk_card["CreateDate"], "%m/%d/%Y"),
                    archive_date=dt.strptime(lk_card["DateArchived"], "%m/%d/%Y")
                    if lk_card["DateArchived"] else None,
                    last_move_date=dt.strptime(lk_card["LastMove"].split(" ")[0],
                                               "%m/%d/%Y"),
                    card_type=lk_card["TypeName"],
                    value=lk_card["ClassOfServiceTitle"],
                    tags=lk_card["Tags"],
                    completed_tasks=lk_card["TaskBoardCompletedCardCount"],
                    total_tasks=lk_card["TaskBoardTotalCards"])


class Card(object):
    def __init__(self, **kwargs):
        """

        :rtype :
        """
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

        if kwargs['archive_date']:
            self.archive_week = Week.withdate(kwargs['archive_date'])
            # self.arch_date_range = self.week_range(kwargs['archive_date'])
            self.lead_time = kwargs['archive_date'] - kwargs['create_date']

# def __str__(self):
#         return str(self.id, self.epic, self.title)
#
# #     def __repr__(self, *args, **kwargs):
# #
# #         return unicode(self.title, 'utf-8')
#
#     def __eq__(self, other):
#         return self.id == other.id
#
#     def __ne__(self, other):
#         return self.id != other.id


#     def week_range(self, archive_date):
#         """Find the first/last day of the week for the given day.
#         Assuming weeks start on Sunday and end on Saturday.
#
#         Returns a tuple of ``(start_date, end_date)``.
#
#         """
#         # isocalendar calculates the year, week of the year, and day of the week.
#         # dow is Mon = 1, Sat = 6, Sun = 7
#         #year, week_no,
#         dow = archive_date.isocalendar()[2]
#
#         # Find the first day of the week.
#         if dow == 7:
#             # Since we want to start with Sunday, let's test for that condition.
#             start_date = archive_date
#         else:
#             # Otherwise, subtract `dow` number days to get the first day
#             start_date = archive_date - timedelta(dow)
#
#         # Now, add 6 for the last day of the week (i.e., count up to Saturday)
#         end_date = start_date + timedelta(6)
#
#         return (start_date, end_date)
