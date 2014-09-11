import slumber, settings as s


class Wrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))

    def fetch_backlog_cards(self):
        reply_data_backlog_lanes_list = self.api.boards("113683593").get()['ReplyData'][0]['Backlog']
        for i in reply_data_backlog_lanes_list:
            if i['Title'] == "J1":
                cards_list = i['Cards']
                for j in cards_list:
                    print j['TypeName']
                    print j['Title']
                    print j['DrillThroughCompletionPercent']
                    print

        #print reply_data_backlog

if __name__ == "__main__":
    wrapper = Wrapper()
    wrapper.fetch_backlog_cards()