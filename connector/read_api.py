'''
Created on Jul 25, 2014

@author: rodrigoabreu
'''

import slumber, settings as s
from datetime import datetime as dt

class ApiWrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))


    def create_archived_cards(self):
        reply_data_archive = self.api.board(s.j1_board).archive.get()["ReplyData"][0][0]["Lane"]["Cards"]
        cards_list = []
        for i in reply_data_archive:
            #print i["Title"], i["ExternalCardID"]
            reply_answer = self.api.board(s.j1_board).getcard(i["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                lk_card = reply_answer["ReplyData"][0]
                #print lk_card["ReplyText"], lk_card["ReplyCode"]
                cards_list.append(Card(lk_card["Title"],
                                   lk_card["ExternalCardID"],
                                   dt.strptime(lk_card["CreateDate"], "%m/%d/%Y"),
                                   dt.strptime(lk_card["DateArchived"], "%m/%d/%Y"),
                                   lk_card["TypeName"],
                                   lk_card["ClassOfServiceTitle"],
                                   lk_card["Tags"]))
        return cards_list

class Card(object):
    #TODO: use kwargs to create a Card
    def __init__(self, title, epic, create_date, archive_date, card_type, value, tags):
        self.title = title
        self.epic = epic
        self.create_date = create_date
        self.archive_date = archive_date
        self.card_type = card_type
        self.value = value
        self.tags = tags

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

        print d


if __name__ == "__main__":
    x= ApiWrapper().create_archived_cards()
    CardController(x).archived_cards_per_week()
