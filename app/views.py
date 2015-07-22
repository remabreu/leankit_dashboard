__author__ = 'rodrigo.abreu'
from flask import render_template,request
from app import app
from flask.ext.wtf import Form
from wtforms import SelectField
from connector.read_api import LeanKitWrapper
from connector.archive_controller import CardArchiveController


class SelectTeam(Form):
    teams = SelectField("Times", choices=[("ESP1", "Esportes 1"), ("ESP2", "Esportes 2")])



@app.route('/')
@app.route('/index', methods=['POST'])
def index():
    form = SelectTeam()
    return render_template("index.html",
                           form=form)

@app.route('/relatorio_semanal.html')
def handle_weekly_report():
    wrapper = LeanKitWrapper()
    archive = wrapper.get_archived_cards()
    wip = wrapper.get_wip_cards()

    cac = CardArchiveController(archive, wip, request.form["Times"])
    archived_cards_by_week = cac.group_cards_by_week()
    archived_by_quarter_by_week = cac.group_cards_by_quarter_by_week(archived_cards_by_week)
    archived_by_quarter = cac.group_cards_by_quarter()

    return render_template("relatorio_semanal.html",
                           archived_by_quarter_by_week=archived_by_quarter_by_week,
                           archived_by_quarter=archived_by_quarter)

