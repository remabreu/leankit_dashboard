import collections
from datetime import datetime as dt
import datetime
import requests
import settings as s

class LkStateMachine(object):
    backlog_list = ["Backlog", "BACKLOG", "Inbox", "Next"]
    doing_list = ["Analysis", "In Progress", "Validation", "Deploy"]
    waiting_list = ["Done", "To Prod"]
    teams = ["ESP 1", "ESP 2"]

    def __init__(self, history_data):
        self.backlog_times_list = []
        self.doing_times_list = []
        self.waiting_times_list = []
        #self.block_times_list = []

        self.build_events(history_data)
        self.execute_transitions()

        self.backlog_duration = self.count_times(self.backlog_times_list)
        self.doing_duration = self.count_times(self.doing_times_list)
        self.waiting_duration = self.count_times(self.waiting_times_list)
        self.cycle_time = self.doing_duration + self.waiting_duration
        self.block_duration = sum(self.block_card_events.keys(), datetime.timedelta(0))

    def append_to_time_lst(self, lane, lane_time):
        if lane in self.backlog_list:
            self.backlog_times_list.append(lane_time)
        elif lane in self.doing_list:
            self.doing_times_list.append(lane_time)
        elif lane in self.waiting_list:
            self.waiting_times_list.append(lane_time)

    def execute_transitions(self):
        create_date = self.create_card_event.keys()[0]
        for move_date, from_to in self.move_events.iteritems():
            from_lane, to_lane = from_to
            elapsed_time = move_date - create_date
            create_date = move_date
            self.append_to_time_lst(from_lane, elapsed_time)

        #self.print_stuff("Backlog", self.backlog_times_list)
        #self.print_stuff("Doing", self.doing_times_list)
        #self.print_stuff("Wait", self.waiting_times_list)
        #self.print_total()
    # def execute_block_events_transitions(self):
    #     start_block = end_block = datetime.timedelta(0)
    #     for block_time in self.block_events.keys():
    #         if self.block_events[block_time][0]:
    #             start_block = block_time
    #         else:
    #             end_block = block_time
    #
    #     self.block_times_list.append(end_block - start_block)
    #
    #     print self.block_times_list
    #
    #     return sum(self.block_times_list)

    def build_events(self, card_history_data):
        move_events_dict = {}
        create_card_event = {}
        self.block_card_events = {}
        x = y = 0
        block_comment = None
        for data in card_history_data:
            if data["Type"] == "CardCreationEventDTO":
                create_date = dt.strptime(data["DateTime"], "%m/%d/%Y at %I:%M:%S %p")
                create_card_event = {create_date: data["ToLaneTitle"]}
            elif data["Type"] == "CardMoveEventDTO":
                move_date = dt.strptime(data['DateTime'], '%m/%d/%Y at %I:%M:%S %p')
                move_events_dict.update({move_date: (data["FromLaneTitle"], data["ToLaneTitle"])})
            elif data["Type"] == "CardBlockedEventDTO":
                block_date = dt.strptime(data['DateTime'], '%m/%d/%Y at %I:%M:%S %p')
                if data["IsBlocked"]:
                    x = block_date
                    block_comment = data["Comment"]
                else:
                    y = block_date
                if x and y:
                    z = y - x
                    self.block_card_events.update({z: block_comment})
                    x = y = 0
                    block_comment = None

                #block_date = dt.strptime(data["DateTime"], "%m/%d/%Y at %I:%M:%S %p")
                #block_card_events.update({block_date: [data["IsBlocked"], data["Comment"]]})

        self.create_card_event = self.normalize_create_state(create_card_event)
        self.move_events = self.normalize_move_states(move_events_dict)
        #self.block_events = collections.OrderedDict(sorted(block_card_events.items(), key=lambda t: t[0]))

    def normalize_create_state(self, create_card_event):
        (create_date, init_state) = create_card_event.items()[0]
        if ":" in init_state:
            create_card_event.update({create_date: init_state.split(":")[1].strip().encode()})

        #self.print_states(create_card_event)
        return create_card_event

    def normalize_move_states(self, move_events_dict):
        x = {}

        for k,lane_tuple in move_events_dict.iteritems():
            l = []
            for lane in lane_tuple:
                if lane.split(":")[0] in self.teams:
                    l.append((lane.split(":")[1]).strip().encode())
                else:
                    l.append((lane.split(":")[0]).strip().encode())

            x[k] = l

        ordered_move_events_dict = collections.OrderedDict(sorted(x.items(), key=lambda t: t[0]))
        #self.print_states(ordered_move_events_dict)
        return ordered_move_events_dict

    def print_states(self, events_list):
        for event_date, states in events_list.iteritems():
            print event_date, states
        print "================"


    def count_times(self, states_list):
        count = datetime.timedelta(0)
        for i in states_list:
            count += i
        return count

    def print_stuff(self, state, lanes_list):
        print "========="
        print state
        count = datetime.timedelta(0)
        for i in lanes_list:
            count += i
            print i
        print "TOTAL COUNT:", count

    def print_total(self):
        print "======================"
        print "TOTAL SPENT: (CYCLE TIME):", sum(self.backlog_times_list + self.doing_times_list + self.waiting_times_list, datetime.timedelta(0))


r = requests.get("http://produtos-globocom.leankitkanban.com/Kanban/API/Card/History/" +\
                         str(s.board_id) + "/" + str("216731609"), auth=("rodrigo.abreu@corp.globo.com", "reminha"))
hist_data = r.json()['ReplyData'][0]
# #218098934
# #180261716
# #219916317

fsm = LkStateMachine(hist_data)
#fsm.print_stuff()



# move_events_dict = {}
# block_card_events = {}
# for data in hist_data:
#     if data["Type"] == "CardCreationEventDTO":
#         create_date = dt.strptime(data["DateTime"], "%m/%d/%Y at %I:%M:%S %p")
#         create_card_event = {create_date: data["ToLaneTitle"]}
#     elif data["Type"] == "CardMoveEventDTO":
#         move_date = dt.strptime(data['DateTime'], '%m/%d/%Y at %I:%M:%S %p')
#         move_events_dict.update({move_date: (data["FromLaneTitle"], data["ToLaneTitle"])})
#     elif data["Type"] == "CardBlockedEventDTO":
#         block_date = dt.strptime(data["DateTime"], "%m/%d/%Y at %I:%M:%S %p")
#         block_card_events.update({block_date: [data["IsBlocked"], data["Comment"]]})
#
# #ordered_move_events_dict = collections.OrderedDict(sorted(move_events_dict.items(), key=lambda t: t[0]))
# for k,v in move_events_dict.iteritems():
#     print k,v
#
# print "================================="
#
# x = {}
# team = ["ESP 1", "ESP 2"]
# (create_date, init_state) = create_card_event.items()[0]
# create_card_event.update({create_date: init_state.split(":")[1].strip().encode()})
#
# for k,lane_tuple in move_events_dict.iteritems():
#     l = []
#     for lane in lane_tuple:
#         if lane.split(":")[0] in team:
#             l.append((lane.split(":")[1]).strip().encode())
#         # elif lane.split(":")[0] == "ARCHIVE":
#         #     l.append(lane.split(":")[0])
#         else:
#             l.append((lane.split(":")[0]).strip().encode())
#
#     x[k] = l
#
# ordered_move_events_dict = collections.OrderedDict(sorted(x.items(), key=lambda t: t[0]))
# print create_card_event
# for k,v in ordered_move_events_dict.iteritems():
#     print k,v
#
# print block_card_events
# unblock_time = block_time = 0
# for block_event in block_card_events.keys():
#     if block_card_events[block_event][0]:
#         print "blocked time", block_event
#         print "Comment", block_card_events[block_event][1]
#         block_time = block_event
#     else:
#         print "unblocked time", block_event
#         print "Comment", block_card_events[block_event][1]
#         unblock_time = block_event
# print "Block Time: ", unblock_time - block_time
#
#
# fsm = LkStateMachine()
# fsm.execute_transitions(ordered_move_events_dict, create_card_event)