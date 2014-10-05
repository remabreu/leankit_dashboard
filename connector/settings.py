import simplejson as json

j1_board = "113658644"
api_url = "http://produtos-globocom.leankit.com/kanban/api/"
user = "rodrigo.abreu@corp.globo.com"
pwd = "reminha"
wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Waiting for Deploy',
       'Fixing Done', u'Validação', 'TO PROD', 'Validation', 'CHG']
work_wip = ['Analise', 'Doing', 'Dev. Done', 'Fixing', 'Validation',
            'Validation Done', 'Fixing', 'Fixing Done']

serach_options_for_old_archive = json.dumps('{"searchOptions":{"SearchTerm":"",\
        "SearchInBacklog":false,\
        "SearchInBoard":false,"SearchInRecentArchive":false,\
        "SearchInOldArchive":true,\
        "SearchAllBoards":false,"IncludeComments":false,"IncludeTags":false,\
        "IncludeExternalId":false,"IncludeTaskboards":false,\
        "BoardId":"113658644",\
        "AssignedUserIds":null,"undefined":"Done","AddedAfter":"",\
        "AddedBefore":"",\
        "Page":1,"MaxResults":25,"OrderBy":"CreatedOn","SortOrder":0}}')
