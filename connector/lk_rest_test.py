import pycurl
import cStringIO
import simplejson as json
import datetime
import pprint

class CardHistory(object):
    def __init__(self):
        #self.card_creation = card_creation
        self.card_move_events = []

class CardCreation(object):
    def __init__(self, creation_lane, creation_date):
        self.cretion_lane = creation_lane
        self.creation_date = datetime.datetime.strptime(creation_date, '%m/%d/%Y at %H:%M:%S %p')

class CardMoveEvent(object):
    def __init__(self, from_lane, current_lane, move_date):
        self.from_lane = from_lane
        self.current_lane = current_lane
        self.move_date = datetime.datetime.strptime(move_date, '%m/%d/%Y at %I:%M:%S %p')

    def __gt__(self, other):
        return self.move_date > other.move_date

    def __lt__(self, other):
        return self.move_date < other.move_date


if __name__ == "__main__":

    buf = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.VERBOSE, True)
    c.setopt(c.URL, "http://produtos-globocom.leankit.com/kanban/api/Card/History/113658644/154480049/") #129396151
    c.setopt(pycurl.USERPWD, "rodrigo.abreu@corp.globo.com:reminha")
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
    string_buffer = buf.getvalue()
    history = json.loads(string_buffer)

    card_hist_lst = history['ReplyData'][0]

    card_history = CardHistory()

    for card_hist in card_hist_lst:
        if card_hist['Type'] == "CardCreationEventDTO":
            card_history.card_creation = CardCreation(card_hist['ToLaneTitle'], card_hist['DateTime'])
        if card_hist['Type'] == "CardMoveEventDTO":
            card_move = CardMoveEvent(card_hist['FromLaneTitle'], card_hist['ToLaneTitle'], card_hist['DateTime'])
            card_history.card_move_events.append(card_move)



    print card_history.card_creation.cretion_lane
    print card_history.card_creation.creation_date.strftime('%Y-%m-%d %H:%M')
    print
    for i in sorted(card_history.card_move_events):
        print i.from_lane
        print i.current_lane
        print i.move_date.strftime('%Y-%m-%d %H:%M')
    #pp = pprint.PrettyPrinter(indent=2)
    #pp.pprint(card_hist_dict)

    lst = sorted(card_history.card_move_events)
    x = [j.move_date-i.move_date for i, j in zip(lst[:-1], lst[1:])]
    print [str(i) for i in x]
    print len(x)
    print len(card_history.card_move_events)

    print card_history.card_creation.creation_date
    print sorted(card_history.card_move_events)[0].move_date
    d = sorted(card_history.card_move_events)[0].move_date - card_history.card_creation.creation_date
    print d
    x.insert(0, d)
    print [str(i) for i in x]
    for idx, obj in enumerate(sorted(card_history.card_move_events)):
        obj.lane_duration = x[idx]

    for i in sorted(card_history.card_move_events):
        print i.from_lane
        print i.current_lane
        print i.move_date.strftime('%Y-%m-%d %H:%M')
        print i.lane_duration

    print sum(x, datetime.timedelta())

    backlog_duration = datetime.timedelta()
    dev_duration = datetime.timedelta()
    for i in sorted(card_history.card_move_events):
        if i.from_lane.startswith("Backlog"):
            backlog_duration += i.lane_duration
        if i.from_lane.startswith("Backlog") and i.current_lane.startswith("DEVELOPMENT"):
            dev_duration += i.lane_duration
        if i.from_lane.startswith("DEVELOPMENT") and i.current_lane.startswith("DEVELOPMENT"):
            dev_duration += i.lane_duration
        if i.from_lane.startswith("DEVELOPMENT") and i.current_lane == "Archive":
            dev_duration += i.lane_duration

    print backlog_duration
    print dev_duration
   # lanes = {"Backlog": ["Icebox", "10%", "Inbox", "Next"],
   #          "DEVELOPMENT": ["Analise", "Doing", "VALIDATION"]}

    states = ['Backlobg', 'DEVELOPMENT', "VALIDATION", "TO PROD", "JANELA", "Archive"]
    transitions = [ #Backlog Transitions
                   {"source": "Backlog",
                    "dest": "Backlog"},
                   {"source": "Backlog",
                    "dest": "DEVELOPMENT"},
                    #DEV Transitions
                   {"source": "DEVELOPMENT",
                    "dest" : "DEVELOPMENT"},
                   {"source": "DEVELOPMENT",
                    "dest": "VALIDATION"},
                   {"source": "DEVELOPMENT",
                    "dest": "TO PROD"},
                   {"source": "DEVELOPMENT",
                    "dest": "JANELA"},
                   {"source": "DEVELOPMENT",
                    "dest": "Archive"},
                   #VALIDATION Transitions
                   {"source": "VALIDATION",
                    "dest": "VALIDATION"},
                    {"source": "VALIDATION",
                     "dest": "TO PROD"},
                    {"source": "VALIDATION",
                     "dest": "JANELA"},
                    {"source": "VALIDATION",
                     "dest": "Archive"},
                    {"source": "TO PROD",
                     "dest": "TO PROD"},
                    {"source": "TO PROD",
                     "dest": "Archive"},
                    {"source": "TO PROD",
                     "dest": "JANELA"},
                    {"source": ""
                    }

                   ]