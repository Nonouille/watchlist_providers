from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from functions.db_functions import (
    get_userID,
    get_user_last_research_date,
    get_user_providers,
    modify_user_providers,
    get_user_results,
    modify_last_research_user,
    modify_film,
)
from functions.fetch_functions import (
    get_ids,
    get_providers,
    get_watchlist,
    get_all_regions,
    get_region_providers,
    sort_watchlist,
)
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

SWAGGER_URL = "/swagger/"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Watchlist API", "swaggerUiPrefix": "/api"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

region_list = get_all_regions()

@app.route("/", methods=["GET"])
def get_home():
    return jsonify({"message" : "Boum boum, server is running !"})

@app.route("/your_providers", methods=["GET"])
def get_your_providers():
    username = request.args.get("username")
    country_code = request.args.get("country_code")
    if not country_code:
        return "Error: country_code parameter is required", 400
    if not username:
        return "Error: username parameter is required", 400
    if country_code not in region_list:
        return "Error: invalid country_code", 400

    user_ID = get_userID(username)
    if user_ID == -1:
        return "Error: failed to retrieve user ID", 500

    providers = get_user_providers(user_ID, country_code)

    return {"providers": providers}

@app.route("/get_region_providers", methods=["GET"])
def get_get_region_providers():
    region_list = get_all_regions()
    country_code = request.args.get("country_code")
    if not country_code:
        return "Error: country_code parameter is required", 400
    if country_code not in region_list:
        return "Error: invalid country_code", 400

    return {
        "country_code": country_code,
        "providers": get_region_providers(country_code),
    }

@app.route("/regions", methods=["GET"])
def get_regions():
    regions = get_all_regions()
    return {"regions": regions}

@app.route("/results", methods=["POST"])
def results():
    data = request.json
    username = data.get("username")
    country_code = data.get("country_code")
    selected_providers = data.get("providers", [])
    refresh = data.get("refresh", False)
    if not country_code:
        return "Error: country_code parameter is required", 400
    if not username:
        return "Error: username parameter is required", 400
    if country_code not in region_list:
        return "Error: invalid country_code", 400

    user_ID = get_userID(username)
    if user_ID == -1:
        return "Error: failed to retrieve user ID", 500

    last_research_date = get_user_last_research_date(user_ID)
    if last_research_date == -1:
        return "Error: failed to retrieve the last research date", 500

    modify_user_providers(user_ID, country_code, selected_providers)

    watchlist = get_user_results(user_ID, country_code)
    if (
        not watchlist
        or not last_research_date
        or (datetime.now() - last_research_date).days > 7
        or refresh
    ):
        watchlist = get_watchlist(username)
        if not watchlist:
            return "Error: failed to retrieve the watchlist", 500
        watchlist = get_ids(watchlist)
        watchlist = get_providers(watchlist)
        watchlist = sort_watchlist(watchlist, selected_providers)
        modify_last_research_user(user_ID)
        modify_film(user_ID, country_code, watchlist)
    elif any(film["providers"] not in selected_providers for film in watchlist):
        watchlist = sort_watchlist(watchlist, selected_providers)

    return watchlist
