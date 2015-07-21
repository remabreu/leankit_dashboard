# -*- coding: utf-8 -*-

from jinja2 import Environment, PackageLoader
import os
from read_api import LeanKitWrapper
from archive_controller import CardArchiveController

wrapper = LeanKitWrapper()
archive = wrapper.get_archived_cards()
wip = wrapper.get_wip_cards()

cac = CardArchiveController(archive, wip, "ESP2")
archived_cards_by_week = cac.group_cards_by_week()
archived_by_quarter_by_week = cac.group_cards_by_quarter_by_week(archived_cards_by_week)
archived_by_quarter = cac.group_cards_by_quarter()

#print archived_cards_by_week
env = Environment(loader=PackageLoader('connector', '../templates'))
template = env.get_template('template.html')
f = os.path.join(os.getcwd(), '../web/esp1/relatorio_semanal.html')
template.stream(archived_by_quarter_by_week=archived_by_quarter_by_week,
                archived_by_quarter=archived_by_quarter).dump(f, encoding="UTF-8")

template = env.get_template('template_by_tag.html')
f = os.path.join(os.getcwd(), '../web/esp1/targets_report.html')
template.stream(archived_cards_by_week=archived_cards_by_week).dump(f, encoding="UTF-8")