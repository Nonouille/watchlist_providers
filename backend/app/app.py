from datetime import datetime
from flask import Flask, request, jsonify
from flasgger import Swagger
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

app = Flask(__name__)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all rules
            "model_filter": lambda tag: True,  # all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}
swagger = Swagger(app, config=swagger_config)


region_list = get_all_regions()


@app.route("/", methods=["GET"])
def get_home():
    """
    Status endpoint.
    ---
    tags:
      - Home
    responses:
      200:
        description: A simple status message
        schema:
          type: object
          properties:
            message:
              type: string
              example: Boum boum, server is running !
    """
    return jsonify({"message" : "Boum boum, server is running !"})

@app.route("/your_providers", methods=["GET"])
def get_your_providers():
    """
    Get the user's selected providers for a specific country.
    ---
    tags:
        - Providers
    parameters:
        - name: username
          in: query
          type: string
          required: true
          description: The username of the user
          example: "nonouille92"
        - name: country_code
          in: query
          type: string
          required: true
          description: The country code (ISO 3166-1 alpha-2)
          example: "FR"
    responses:
        200:
            description: A list of the user's selected providers
            schema:
                type: object
                properties:
                    providers:
                        type: array
                        items:
                            type: object
                        example: [{"provider_id": 8, "provider_name": "Netflix"}]
        400:
            description: Missing or invalid parameters
        500:
            description: Server error retrieving user data from the database
    """
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
    """
    Get all streaming providers available in a specific region.
    ---
    tags:
        - Providers
    parameters:
        - name: country_code
          in: query
          type: string
          required: true
          description: The country code (ISO 3166-1 alpha-2)
          example: "FR"
    responses:
        200:
            description: A list of all streaming providers available in the specified region
            schema:
                type: object
                properties:
                    country_code:
                        type: string
                        example: "FR"
                    providers:
                        type: array
                        items:
                            type: string
                        example: ["Netflix", "Amazon Prime Video", "Disney+"]
        400:
            description: Missing or invalid country_code parameter
    """
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
    """
    Get a list of all available regions/countries.
    ---
    tags:
        - Regions
    responses:
        200:
            description: A list of all available regions
            schema:
                type: object
                properties:
                    regions:
                        type: array
                        items:
                            type: string
                        example: ["US", "FR", "DE", "GB"]
    """
    regions = get_all_regions()
    return {"regions": regions}


@app.route("/results", methods=["POST"])
def results():
    """
    Get filtered results from a user's watchlist based on selected providers.
    ---
    tags:
        - Results
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              username:
                type: string
                description: The username of the user
                example: "nonouille92"
              country_code:
                type: string
                description: The country code (ISO 3166-1 alpha-2)
                example: "FR"
              providers:
                type: array
                description: List of selected provider IDs
                items:
                  type: integer
                example: [8, 119, 337]
              refresh:
                type: boolean
                description: Force refresh of watchlist data
                default: false
                example: true
            required:
              - username
              - country_code
    responses:
        200:
            description: Filtered watchlist results
            schema:
                type: array
                items:
                    type: object
                    properties:
                        id:
                            type: integer
                            example: 550
                        title:
                            type: string
                            example: "Fight Club"
                        providers:
                            type: array
                            items:
                                type: integer
                            example: [8, 119]
        400:
            description: Missing or invalid parameters
        500:
            description: Server error retrieving data
    """
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
