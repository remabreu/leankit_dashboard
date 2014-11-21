# -*- coding: utf-8 -*-
import simplejson as json
import datetime
from isoweek import Week

j1_board = "113658644"
api_url = "http://produtos-globocom.leankit.com/kanban/api/"
user = "rodrigo.abreu@corp.globo.com"
pwd = "reminha"
wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Waiting for Deploy',
       'Fixing Done', u'Validação', 'TO PROD', 'Validation']
work_wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Validation',
            'Validation Done', 'Fixing', 'Fixing Done']
development_lane = '127351620'

search_options_for_old_archive = json.dumps('{"searchOptions":{"SearchTerm":"",\
        "SearchInBacklog":false,\
        "SearchInBoard":false,\
        "SearchInRecentArchive":false,\
        "SearchInOldArchive":true,\
        "SearchAllBoards":false,\
        "IncludeComments":false,\
        "IncludeTags":false,\
        "IncludeExternalId":false,\
        "IncludeTaskboards":false,\
        "BoardId":"113658644",\
        "AssignedUserIds":null,"undefined":"Done","AddedAfter":"",\
        "AddedBefore":"",\
        "Page":1,"MaxResults":25,"OrderBy":"CreatedOn","SortOrder":0}}')


def week_no(y, m, d):
    quarter_start_date = datetime.date(y, m, d)
    return Week.withdate(quarter_start_date)

quarter_week_numbers = [week_no(2014, 9, 1), week_no(2014, 12, 1),
                        week_no(2015, 3, 1), week_no(2015, 6, 1),
                        week_no(2015, 9, 1)]

quarter_date_ranges = {'Q3.2014': (datetime.date(2014, 6, 1), datetime.date(2014, 8, 31)),
                       'Q4.2014': (datetime.date(2014, 9, 1), datetime.date(2014, 11, 30)),
                       'Q1.2015': (datetime.date(2014, 12, 1), datetime.date(2015, 2, 28)),
                       'Q3.2015': (datetime.date(2015, 3, 1), datetime.date(2014, 5, 31))}