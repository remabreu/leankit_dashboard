# -*- coding: utf-8 -*-

import slumber
import settings as s
import requests
from datetime import datetime as dt
from isoweek import Week


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
            reply_answer = self.api.board(s.board_id).getcard(lk_card["Id"]).get()
            if reply_answer["ReplyCode"] == 200:
                cards_list.append(self.__create_card(reply_answer["ReplyData"][0]))

        return cards_list

    def __fetch_recent_archived_cards_list(self):
        lk_reply_data_archive = self.api.board(s.board_id).archive.get()["ReplyData"][0][0]["Lane"]["Cards"]
        return self.__fetch_cards_list(lk_reply_data_archive)

    def __fetch_old_archived_cards_list(self):
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resource_uri = "https://produtos-globocom.leankit.com/kanban/api/board/178068433/searchcards"
        old_archived_cards = requests.post(resource_uri,
                                           data=s.search_options_for_old_archive,
                                           headers=headers,
                                           auth=(s.user, s.pwd))
        old_arch_cards_list = old_archived_cards.json()
        return self.__fetch_cards_list(old_arch_cards_list["ReplyData"][0]["Results"])

    def __fetch_delivered_cards_list(self):
        lk_reply_data_delivered = self.api.boards(s.board_id).get()['ReplyData'][0]['Lanes']
        delivered_cards = []
        #print lk_reply_data_delivered
        for lane in lk_reply_data_delivered:
            if lane["Title"] == "BETA" or lane["Title"] == "PROD":
                delivered_cards += self.__fetch_cards_list(lane["Cards"])
        return delivered_cards

    def __fetch_backlog_cards_list(self, reply_data):
        for backlog_lane in reply_data['Backlog']:
            if backlog_lane['Title'] == 'Next':
                return backlog_lane['Cards']

    def __fetch_development_cards_list(self, reply_data):
        dev_card_list = []
        for lane in reply_data['Lanes']:
            if lane['Title'] in s.work_wip:
                dev_card_list += lane['Cards']

        return self.__fetch_cards_list(dev_card_list)

    def __fetch_deploy_cards_list(self, reply_data):
        cards_list = []
        for lane in reply_data['Lanes']:
            if lane['Title'] == 'TO PROD' or \
                            lane['Title'] == u'Validação' or \
                            lane['Title'] == 'Waiting for Deploy':
                print lane['Title'], len(lane['Cards'])
                cards_list += lane['Cards']

        return cards_list

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
                    value=lk_card["ClassOfServiceTitle"],
                    tags=lk_card["Tags"].split(","),
                    completed_tasks=lk_card["TaskBoardCompletedCardCount"],
                    total_tasks=lk_card["TaskBoardTotalCards"])

    def get_archived_cards(self):
        recent_archive = self.__fetch_recent_archived_cards_list()
        old_archive = self.__fetch_old_archived_cards_list()
        # for card in old_archive:
        #     print card.lane_title, card.title
        delivered_cards = self.__fetch_delivered_cards_list()
        print len(recent_archive), len(old_archive), len(delivered_cards)
        return list(set(recent_archive) | set(old_archive) | set(delivered_cards))

    def get_wip_cards(self):
        reply_data = self.api.boards(s.board_id).get()["ReplyData"][0]

        #backlog_cards_list = self.__fetch_backlog_cards_list(reply_data)
        #development_cards_list = self.__fetch_development_cards_list(reply_data)
        #deploy_cards_list = self.__fetch_deploy_cards_list(reply_data)

        #return [backlog_cards_list, development_cards_list, deploy_cards_list]
        return self.__fetch_development_cards_list(reply_data)
