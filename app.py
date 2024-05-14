import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Use a single dictionary to store the alert configuration
alert_spread = {'market_id': None, 'spread': None}


# Helper function to fetch market data from API
def fetch_market_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Función para obtener el spread de un mercado
def get_spread(market_id):
    assert isinstance(market_id, str)
    url = f"https://buda.com/api/v2/markets/{market_id}/order_book"
    data = fetch_market_data(url)
    if data is None:
        return None

    asks = data['order_book']['asks']
    bids = data['order_book']['bids']

    if not asks or not bids:
        return None

    lowest_ask = float(asks[0][0])
    highest_bid = float(bids[0][0])

    spread = lowest_ask - highest_bid

    return spread


# Function to fetch all markets from the API
def fetch_all_markets():
    url = "https://buda.com/api/v2/markets"
    data = fetch_market_data(url)
    if data is None:
        return None, "Error fetching markets"
    return data['markets'], None


# Endpoint para obtener el spread de todos los mercados o un mercado específico
@app.route('/spreads', methods=['GET'])
def get_all_spreads():
    market_id = request.args.get('market_id')

    if market_id:
        spread = get_spread(market_id)
        if spread is None:
            return jsonify({"message": "Error fetching spread for market"}), 500
        return jsonify({market_id: spread})

    markets, error = fetch_all_markets()
    if error:
        return jsonify({"message": error}), 500

    spreads = {}
    for market in markets:
        market_id = market['id']
        spread = get_spread(market_id)
        if spread is not None:
            spreads[market_id] = spread

    return jsonify(spreads)


@app.route('/set_alert_spread', methods=['POST'])
def set_alert_spread():
    data = request.json
    market_id = data.get('market_id')
    spread = get_spread(market_id)

    # Validate that both market_id and spread are provided
    if not market_id or spread is None:
        return jsonify({"message": "Both market_id and spread are required"}), 400

    # Set the alert
    alert_spread['market_id'] = market_id
    alert_spread['spread'] = spread

    return jsonify({"message": "Alert spread set for market_id: {}".format(market_id)})


@app.route('/poll_alert_spread', methods=['GET'])
def poll_alert_spread():
    market_id = alert_spread['market_id']

    # Validate that a market_id is provided
    if not market_id:
        return jsonify({"error": "Market ID not provided"}), 400

    # Check if the requested market is the one with the alert set
    if market_id != alert_spread['market_id']:
        return jsonify({"error": "No alert spread set for this market"}), 404

    # Fetch the current spread for the market
    current_spread = get_spread(market_id)
    if current_spread is None:
        return jsonify({"error": "Could not fetch current spread"}), 500

    # Compare the current spread with the alert spread
    alert_value = alert_spread['spread']
    status = "within" if current_spread == alert_value else ("higher" if current_spread > alert_value else "lower")

    return jsonify({
        "market_id": market_id,
        "current_spread": current_spread,
        "alert_spread": alert_value,
        "status": status
    })


if __name__ == '__main__':
    app.run(debug=True)
