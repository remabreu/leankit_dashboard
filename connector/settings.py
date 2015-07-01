# -*- coding: utf-8 -*-
import datetime
from isoweek import Week

board_id = "196166479"
api_url = "http://produtos-globocom.leankit.com/kanban/api/"
user = "rodrigo.abreu@corp.globo.com"
pwd = "reminha"
wip = ["Analise", "Doing", "Dev. Done", "Fixing", "Waiting for Deploy",
       "Fixing Done", u"Validação", "TO PROD", "Validation"]

wip_dev = ["In Process", "Dev.Done", "Team Validation"]
#work_wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Validation',
#            'Validation Done', 'Fixing', 'Fixing Done']
work_wip = ['Current Sprint Backlog', 'In Process', 'Dev. Done', 'Team Validation', 'TO PROD', 'Janela']
development_lane = '127351620'

#search_options_for_old_archive = json.dumps(json.JSONDecoder().decode('{"searchOptions":{"SearchTerm":"",\
#        "SearchInOldArchive":true,\
#        "Page":1, "MaxResults":20,"OrderBy":"CreatedOn","SortOrder":0}}'))

# '{"searchOptions":{"SearchTerm":"",\
#         "SearchInBacklog":false,\
#         "SearchInBoard":false,\
#         "SearchInRecentArchive":false,\
#         "SearchInOldArchive":true,\
#         "SearchAllBoards":false,\
#         "IncludeComments":false,\
#         "IncludeTags":false,\
#         "IncludeExternalId":false,\
#         "IncludeTaskboards":false,\
#         "BoardId":"178068433",\
#         "AssignedUserIds":null,"undefined":"Done","AddedAfter":"",\
#         "AddedBefore":"",\
#         "Page":1,"MaxResults":25,"OrderBy":"CreatedOn","SortOrder":0}}'

def week_no(y, m, d):
    quarter_start_date = datetime.date(y, m, d)
    return Week.withdate(quarter_start_date)

quarter_week_numbers = iter([week_no(2014, 9, 1), week_no(2014, 12, 1),
                            week_no(2015, 3, 1), week_no(2015, 6, 1),
                            week_no(2015, 9, 1)])

#quarters = [(3,1,"Q2.2015"), (6,1,"Q3.2015"), (9,1,"Q4.2015"), (12, 1, "Q1.2016")]

quarters = {"Q2.2015": (datetime.datetime(2015, 1, 3), datetime.datetime(2015, 5, 31)),
            "Q3.2015": (datetime.datetime(2015, 6, 1), datetime.datetime(2015, 8, 31)),
            "Q4.2015": (datetime.datetime(2015, 9, 1), datetime.datetime(2015, 8, 31)),
            "Q1.2016": (datetime.datetime(2015, 12, 1), datetime.datetime(2016, 2, 29))}
