import slumber, settings as s


class Wrapper(object):
    def __init__(self):
        self.api = slumber.API(s.api_url, auth=(s.user, s.pwd))

    def fetch_backlog_cards(self):
        reply_data_backlog_lanes_list = self.api.boards("113683593").get()['ReplyData'][0]['Backlog']
        targets_list = []
        for lane in reply_data_backlog_lanes_list:
            if lane['Title'] == "J1":
                cards_list = lane['Cards']
                for card in cards_list:
                    d = {}
                    d['epic'] = card['TypeName']
                    d['priority'] = card['Index']
                    d['percent'] = card['DrillThroughCompletionPercent']
                    d['total'] = card['DrillThroughProgressSizeTotal']
                    d['title'] = card['Title']
                    targets_list.append(d)
        x = []
        for item in targets_list:
            if x['epic'] == item['epic']:
                y = {}
                y['priority'] = item['Index']
                y['percent'] = item['percent']
                y['total'] = item['total']
                y['title'] = item['title']
                x['cards'].append(y)
            else:
                z = {}
                z['epic'] = item['epic']
                z['cards'] = []

        x.append()





#                     if targets_list:
#                         if i['epic'] == card['TypeName']:
#                             x = {}
#                             x['title'] = card['Title']
#                             x['priority'] = card['Index']
#                             x['percent'] = card['DrillThroughCompletionPercent']
#                             x['total'] = card['DrillThroughProgressSizeTotal']
#                             lst = i['cards']
#                             lst.append(x)
#                         else:
#                             i['epic'] = card['TypeName']
#                             i['cards'] = []
#                             targets_list.append(i)
#                     else:
#                         d = {}
#                         d['epic'] = card['TypeName']
#                         d['cards'] = []
#                         targets_list.append(d)

        print









        #print reply_data_backlog

if __name__ == "__main__":
    wrapper = Wrapper()
    wrapper.fetch_backlog_cards()