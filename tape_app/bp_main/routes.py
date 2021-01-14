from flask import Blueprint
from tape_app.utils import render_page
from flask import current_app as app

bp_main = Blueprint("bp_main", __name__)

@bp_main.route("/",methods=['GET',"POST"])
@bp_main.route("/home",methods=['GET',"POST"])
def home():
    """
        The home page of TapeFlip.app
    """
    demos = [
        {
            'type': 'Original Recording',
            'color': '3f5dca',
            'id': '874891348'
        },
        {
            'type': 'Tape Recording',
            'color': '9e2b25',
            'id': '874891534'
        },
        {
            'type': 'Original Recording',
            'color': '3f5dca',
            'id': '875472067'
        },
        {
            'type': 'Tape Recording',
            'color': '9e2b25',
            'id': '875472226'
        }
    ]
    return render_page("public/landing_page.html", demos=demos)

@bp_main.route("/pricing",methods=['GET',"POST"])
def pricing():
    """
        The pricing page where users can choose which
        credit package to purchase.
    """
    pricing_options = app.config["PRICING_OPTIONS"]
    return render_page("public/pricing.html", title='Pricing', options=pricing_options)

@bp_main.route("/faq",methods=['GET',"POST"])
def faq():
    """
        The FAQ page.
    """
    return render_page("public/faq.html", title='FAQ')

@bp_main.route("/tos",methods=['GET',"POST"])
def tos():
    """
        The TOS page.
    """
    return render_page("public/tos.html", title='Terms')

@bp_main.route("/privacy",methods=['GET',"POST"])
def privacy():
    """
        The privacy policy page.
    """
    return render_page("public/privacy.html", title='Privacy')

@bp_main.route("/roster",methods=['GET',"POST"])
def roster():
    """
        This page shows all the available tape machines.
    """
    return render_page("public/roster.html", title='Roster')
