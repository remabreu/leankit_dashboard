# -*- coding: utf-8 -*-

'''
Created on Jul 25, 2014

@author: rodrigoabreu
'''
from __future__ import division
import slumber, settings as s
from datetime import datetime as dt
from datetime import timedelta
import simplejson as json
import codecs

class ApiWrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))


    def fetch_archived_cards(self):
        reply_data_archive = self.api.board(s.j1_board).archive.get()["ReplyData"][0][0]["Lane"]["Cards"]
        cards_list = []
        for i in reply_data_archive:
            #print i["Title"], i["ExternalCardID"]
            reply_answer = self.api.board(s.j1_board).getcard(i["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                lk_card = reply_answer["ReplyData"][0]
                #print lk_card["ReplyText"], lk_card["ReplyCode"]
                cards_list.append(Card(lk_card["Id"],
                                   lk_card["Title"],
                                   lk_card["ExternalCardID"],
                                   dt.strptime(lk_card["CreateDate"], "%m/%d/%Y"),
                                   dt.strptime(lk_card["DateArchived"], "%m/%d/%Y"),
                                   lk_card["TypeName"],
                                   lk_card["ClassOfServiceTitle"],
                                   lk_card["Tags"]))
#         c = 0
#         for i in cards_list:
#             c += 1
#             print c, i.title
        return cards_list

    def fetch_old_archived_cards(self):
        search_options = json.dumps('{"searchOptions":{"SearchTerm":"","SearchInBacklog":false,\
        "SearchInBoard":false,"SearchInRecentArchive":false,"SearchInOldArchive":true,\
        "SearchAllBoards":false,"IncludeComments":false,"IncludeTags":false,\
        "IncludeExternalId":false,"IncludeTaskboards":false,"BoardId":"113658644",\
        "AssignedUserIds":null,"undefined":"Done","AddedAfter":"","AddedBefore":"",\
        "Page":1,"MaxResults":25,"OrderBy":"CreatedOn","SortOrder":0}}')
        reply_data = self.api.board("113658644").searchcards.post(search_options)["ReplyData"][0]['Results']
        cards_list = []
        #print reply_data
        for i in reply_data:
            reply_answer = self.api.board(s.j1_board).getcard(i["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                lk_card = reply_answer["ReplyData"][0]
                #print lk_card["ReplyText"], lk_card["ReplyCode"]
                cards_list.append(Card(lk_card["Id"],
                                       lk_card["Title"],
                                       lk_card["ExternalCardID"],
                                       dt.strptime(lk_card["CreateDate"], "%m/%d/%Y"),
                                       dt.strptime(lk_card["DateArchived"], "%m/%d/%Y"),
                                       lk_card["TypeName"],
                                       lk_card["ClassOfServiceTitle"],
                                       lk_card["Tags"]))

#         c = 0
#         for i in cards_list:
#             c += 1
#             print c, i.title
        return cards_list

    def merge_archived_lists(self, recent_archive, old_archive):
        complete_archive = []
        for i in recent_archive:
            for j in old_archive:
                if i == j and i not in complete_archive:
                    complete_archive.append(i)
                elif i!= j:
                    if i not in complete_archive:
                        complete_archive.append(i)
                    elif j  not in complete_archive:
                        complete_archive.append(j)
        return complete_archive

    def amount_of_cards(self):
        reply_data = self.api.boards("113658644").get()["ReplyData"][0]
        cards_count = {}

        for backlog_lane in reply_data['Backlog']:
            if backlog_lane['Title'] == 'Next':
                cards_count['backlog'] = len(backlog_lane['Cards'])

        wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Waiting for Deploy', 'Fixing Done', u'Validação', 'TO PROD', 'Validation', 'CHG']
        wip_card_count = 0
        for lane in reply_data['Lanes']:
            if lane['Title'] in wip:
                wip_card_count += len(lane['Cards'])

        cards_count['wip'] = wip_card_count

        return cards_count

class Card(object):
    #TODO: use kwargs to create a Card
    def __init__(self, card_id, title, epic, create_date, archive_date, card_type, value, tags):
        self.card_id = card_id
        self.title = title
        self.epic = epic
        self.create_date = create_date
        self.archive_date = archive_date
        self.card_type = card_type
        self.value = value
        self.tags = tags
        self.arch_date_range = self.week_range(archive_date)
        self.lead_time = archive_date - create_date

    def __str__(self):
        return str(self.card_id, self.epic, self.title)

#     def __repr__(self, *args, **kwargs):
#
#         return unicode(self.title, 'utf-8')

    def __eq__(self, other):
        return self.card_id == other.card_id

    def __ne__(self, other):
        return self.card_id != other.card_id


    def week_range(self, archive_date):
        """Find the first/last day of the week for the given day.
        Assuming weeks start on Sunday and end on Saturday.

        Returns a tuple of ``(start_date, end_date)``.

        """
        # isocalendar calculates the year, week of the year, and day of the week.
        # dow is Mon = 1, Sat = 6, Sun = 7
        year, week, dow = archive_date.isocalendar()

        # Find the first day of the week.
        if dow == 7:
            # Since we want to start with Sunday, let's test for that condition.
            start_date = archive_date
        else:
            # Otherwise, subtract `dow` number days to get the first day
            start_date = archive_date - timedelta(dow)

        # Now, add 6 for the last day of the week (i.e., count up to Saturday)
        end_date = start_date + timedelta(6)

        return (start_date, end_date)


class CardController(object):
    def __init__(self, cards_list):
        self.cards_list = cards_list

    def archived_cards_per_week(self):
        d = {}
        for i in self.cards_list:
            arch_week_no = i.archive_date.date().isocalendar()[1]
            if arch_week_no in d.keys():
                lst = d[arch_week_no]
                lst.append(i)
                d[arch_week_no] = lst
            else:
                l = [i]
                d[arch_week_no] = l

        return d

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

        #print d
        return d

    def card_types_effort(self):
        effort_per_card_type_dict = {}
        for card in self.cards_list:
            if card.card_type in effort_per_card_type_dict.keys():
                effort_per_card_type_dict[card.card_type] += card.lead_time.days
            else:
                effort_per_card_type_dict[card.card_type] = card.lead_time.days

        #print effort_per_card_type_dict
        return effort_per_card_type_dict



if __name__ == "__main__":
    wrapper = ApiWrapper()
    print wrapper.amount_of_cards()
    #cards_list = wrapper.merge_archived_lists(wrapper.fetch_archived_cards(),
    #                              wrapper.fetch_old_archived_cards())
    #CardController(cards_list).card_types_effort()
    #CardController(cards_list).tags_effort()
    #CardController(x).tags_effort()
