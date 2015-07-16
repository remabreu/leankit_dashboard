# -*- coding: utf-8 -*-

import slumber
import settings as s
import requests
from datetime import datetime as dt
from isoweek import Week
import simplejson as json
from read_history import LkStateMachine


class Card(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

        if kwargs['archive_date']:
            self.archive_week = Week.withdate(kwargs['archive_date'])
            self.lead_time = kwargs['archive_date'] - kwargs['create_date']
        else:
            self.archive_date = kwargs['last_move_date']
            self.archive_week = Week.withdate(kwargs['last_move_date'])
            self.lead_time = kwargs['last_move_date'] - kwargs['create_date']

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

class LeanKitWrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))

    def __fetch_cards_list(self, lk_cards_list):
        cards_list = []
        for lk_card in lk_cards_list:
            if lk_card["Index"] is not "1000":
                reply_answer = self.api.board(s.board_id).getcard(lk_card["Id"]).get()
                if reply_answer["ReplyCode"] == 200:
                    card = self.__create_card(reply_answer["ReplyData"][0])
                    self.set_history_data(card)
                    cards_list.append(card)

        return cards_list

    def __fetch_recent_archived_cards_list(self, team):
        lk_reply_data_archive = self.api.board(s.board_id).archive.get()["ReplyData"][0][0]["ChildLanes"][team]['Lane']['Cards']
        #[0][0]["Lane"]["Cards"]
        return self.__fetch_cards_list(lk_reply_data_archive)

    def __build_search_options_for_old_archive(self, page):
        return json.dumps(json.JSONDecoder().decode('{"searchOptions":{"SearchTerm":"",\
        "SearchInOldArchive":true,\
        "Page":' + str(page) + ',"MaxResults":20,"OrderBy":"CreatedOn","SortOrder":0}}'))

    def __search_old_archives(self, page):
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resource_uri = "https://produtos-globocom.leankit.com/kanban/api/board/" + s.board_id + "/searchcards"
        old_archived_cards = requests.post(resource_uri,
                                           data=self.__build_search_options_for_old_archive(page),
                                           headers=headers,
                                           auth=(s.user, s.pwd))
        return old_archived_cards.json()

    def __fetch_old_archived_cards_list(self):
        old_arch_cards_list = self.__search_old_archives(1)

        total_results = int(old_arch_cards_list["ReplyData"][0]['TotalResults'])
        pages, remainder = divmod(total_results, 20)
        last_page = 1 if remainder > 0 else 0
        old_archive = self.__fetch_cards_list(old_arch_cards_list["ReplyData"][0]["Results"])

        for page in range(2, pages + last_page + 1):
            old_archive_pages = self.__search_old_archives(page)
            old_archive.extend(self.__fetch_cards_list(old_archive_pages["ReplyData"][0]["Results"]))

        return old_archive

    def __fetch_development_cards_list(self, reply_data):
        dev_card_list = []
        for lane in reply_data['Lanes']:
            if lane['Title'] in s.work_wip:
                dev_card_list += lane['Cards']

        return self.__fetch_cards_list(dev_card_list)

    def set_history_data(self, card):
        r = requests.get("http://produtos-globocom.leankitkanban.com/Kanban/API/Card/History/" +\
                         str(s.board_id) + "/" + str(card.id), auth=("rodrigo.abreu@corp.globo.com", "reminha"))
        hist_data = r.json()['ReplyData'][0]
        lk_state_machine = LkStateMachine(hist_data)
        card.backlog_duration = lk_state_machine.backlog_duration
        card.development_duration = lk_state_machine.doing_duration
        card.dev_queue_duration = lk_state_machine.waiting_duration
        card.cycle_time = lk_state_machine.cycle_time
        card.blocked_duration = lk_state_machine.block_duration
        card.blocked_reasons = lk_state_machine.block_card_events.values()

    def __create_card(self, lk_card):
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
                        tags=lk_card["Tags"].split(",") if lk_card["Tags"] else None,
                        completed_tasks=lk_card["TaskBoardCompletedCardCount"],
                        total_tasks=lk_card["TaskBoardTotalCards"],
                        #cycle_time=self.get_cycle_time(lk_card),
                        team=lk_card["ClassOfServiceTitle"])

    def get_archived_cards(self):
        recent_archive = self.__fetch_recent_archived_cards_list(1) #ESP1
        recent_archive.extend(self.__fetch_recent_archived_cards_list(2)) #ESP2
        old_archive = self.__fetch_old_archived_cards_list()
        #delivered_cards = self.__fetch_delivered_cards_list()
        #print len(recent_archive), len(old_archive)
        #return recent_archive
        return recent_archive + old_archive
        #return list(set(recent_archive) | set(old_archive))

    def get_wip_cards(self):
        reply_data = self.api.boards(s.board_id).get()["ReplyData"][0]

        return self.__fetch_development_cards_list(reply_data)

if __name__ == "__main__":
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()

    #wip = wrapper.get_wip_cards()

    for i, card in enumerate(archive):
        if card.blocked_duration:
            print i, card.id, card.team, card.title, card.blocked_duration, card.blocked_reasons
        # print i, card.id, card.title, card.backlog_duration, card.development_duration,\
        #         card.dev_queue_duration, card.cycle_time

