__author__ = 'rodrigo.abreu'

import slumber
import settings as s
import pprint

api = slumber.API(s.api_url, auth=(s.user, s.pwd))
lk_reply_data_archive = api.board(s.j1_board).archive.get()["ReplyData"][0][0]["Lane"]["Cards"]

lk_history = api.card(.history.get()

pprint.pprint(lk_reply_data_archive)

#print lk_reply_data_archive

#166358181
