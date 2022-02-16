from flask import Flask, request, jsonify, make_response
from markets import MARKETS
from listings import LISTING
from currencies import CURRENCIES

app = Flask(__name__)


# region error-handling


@app.errorhandler(400)
def handle_400_error(_error):
    return make_response(
        jsonify(
            {
                "Error400": "Bad request. The browser (or proxy) sent a request that this server could not understand."
            }
        ),
        400,
    )


@app.errorhandler(404)
def handle_404_error(_error):
    return make_response(jsonify({"Error404": "Page Cannnot Be Found"}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    return make_response(jsonify({"error500": "Internal Server Error"}), 500)


# endregion error-handling


@app.route("/test_flask", methods=["GET", "POST"])
def test_flask():
    """Example to show how to use Flask and extract information from the incoming request.
    It is not intended to be the only way to do things with Flask, rather more a way to help you not spend too much time on Flask.

    Ref: http://flask.palletsprojects.com/en/1.1.x/

    Try to make those requests:
    curl "http://localhost:5000/test_flask?first=beyond&last=pricing"
    curl "http://localhost:5000/test_flask" -H "Content-Type: application/json" -X POST -d '{"first":"beyond", "last":"pricing"}'

    """
    # This contains the method used to access the route, such as GET or POST, etc
    method = request.method

    # Query parameters
    # It is a dict like object
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=args#flask.Request.args
    query_params = request.args
    query_params_serialized = ", ".join(f"{k}: {v}" for k, v in query_params.items())

    # Get the data as JSON directly
    # If the mimetype does not indicate JSON (application/json, see is_json), this returns None.
    # Ref: https://flask.palletsprojects.com/en/1.1.x/api/?highlight=get_json#flask.Request.get_json
    data_json = request.get_json()

    return jsonify(
        {
            "method": method,
            "query_params": query_params_serialized,
            "data_json": data_json,
        }
    )


@app.route("/markets")
def markets():
    return jsonify([market.to_dict() for market in MARKETS.get_all()])


@app.route("/listings", methods=["GET", "POST"])
def listings():
    listings_list = [listing_item.to_dict() for listing_item in LISTING.get_all()]
    query_params = request.args
    query_params_serialized = ", ".join(f"{k}: {v}" for k, v in query_params.items())

    if request.method == "GET":

        # Comment out the 'for' loop to show calendar attribute
        for listing_item in listings_list:
            listing_item.pop("calendar")
        if not query_params:
            return jsonify(listings_list)

        else:
            # region filtering
            filtered_listings = []

            if "base_price." in query_params_serialized:
                for param, price in query_params.items():
                    if "base_price" in param.split("."):
                        comparison_type = param.split(".")[1]

                        filtered_listings = LISTING.comparison_function(
                            listings_list=listings_list,
                            comparison_type=comparison_type,
                            threshold_price=float(price),
                        )

                        if "currency" in query_params:
                            currency_filter = []
                            for listing_item in listings_list:
                                if listing_item["currency"] in query_params["currency"].upper():
                                    currency_filter.append(listing_item)

                            filtered_listings = [i for i in filtered_listings if i in currency_filter]

            # market filtering
            elif "market" in query_params:
                for market_code in query_params["market"].split(","):
                    try:
                        MARKETS.get_by_code(code=market_code)
                    except Exception as error:
                        return jsonify({"Error": str(error)})

                for listing_item in listings_list:
                    if listing_item["market"] in query_params["market"].split(","):
                        filtered_listings.append(listing_item)

            # currency filtering
            elif "currency" in query_params:
                try:
                    CURRENCIES.get_by_code(code=query_params["currency"].upper())
                except Exception as error:
                    return jsonify({"Error": str(error)})

                for listing_item in listings_list:
                    if listing_item["currency"] == query_params["currency"].upper():
                        filtered_listings.append(listing_item)

            # endregion filtering

            return jsonify({"filtered_listings": filtered_listings})

    if request.method == "POST":
        data_json = request.get_json()
        new_item = (
            {
                "id": len(
                    listings_list
                ),  # first item index on listings_list=0 (id = 0) -> new item id = id(len(listings_list))
                "title": data_json["title"],
                "base_price": data_json["base_price"],
                "currency": data_json["currency"],
                "market": data_json["market"],
            },
        )
        listings_list.append(new_item)
        return jsonify(new_item)


@app.route("/listings/<int:id>", methods=["GET", "PUT", "DELETE"])
def listing(id):
    listing_list = [listing_item.to_dict() for listing_item in LISTING.get_all()]
    for i in listing_list:
        i["id"] = listing_list.index(i)

    # Comment out the 'for' loop to show calendar attribute
    for listing_item in listing_list:
        listing_item.pop("calendar")

    if request.method == "GET":
        if request.args:
            return jsonify({"Error": "Unsupported query args. Please try again."})
        return jsonify({"listing_item": listing_list[id]})

    if request.method == "PUT":
        data_json = request.get_json()
        for key in data_json:
            listing_list[id][key] = data_json[key]

        return jsonify({"listing_item": listing_list[id]})

    if request.method == "DELETE":
        listing_list.pop(id)
        return jsonify({"listing_list": listing_list})


@app.route("/listings/<int:id>/calendar", methods=["GET"])
def listing_calendar(id):
    listing_list = [listing_item.to_dict() for listing_item in LISTING.get_all()]

    market = listing_list[id]["market"]
    base_price = listing_list[id]["base_price"]
    calendar = listing_list[id]["calendar"]
    currency = listing_list[id]["currency"]

    if request.method == "GET":
        query_params = request.args

        base_listings_calendar = []
        for calendar_date in calendar:
            temp = {
                "date": str(calendar_date),
                "price": LISTING.base_price_calc(
                    market=market, base_price=base_price, calendar_date=calendar_date,
                ),
                "currency": LISTING.currency_selector(market=market),
            }
            base_listings_calendar.append(temp)

        if not query_params:
            return jsonify({"base_listings_calendar": base_listings_calendar})

        elif "currency" in query_params:
            query_currency = query_params["currency"].upper()

            try:
                CURRENCIES.get_by_code(query_currency)
            except Exception as error:
                return jsonify({"Error": str(error)})

            if query_currency != currency:
                for listing_item in base_listings_calendar:
                    listing_item["currency"] = query_currency
                    listing_item["price"] = (
                        base_price
                        * CURRENCIES.exchange_coefficient(currency, query_currency)
                    )
                return jsonify(
                    {f"listing_calendar_{query_currency}": base_listings_calendar}
                )
            else:
                return jsonify({"base_listings_calendar": base_listings_calendar})
        else:
            return jsonify({"Error": "Unsupported query args. Please try again."})
