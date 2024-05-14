import requests
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# Variable global para almacenar el valor de alerta
alert_spread = {'market_id': None, 'spread': None}
api = Api(app, version='1.0', title='Spread API',
          description='Challenge #2 Buda.com')

ns = api.namespace('markets', description='Market operations')

spread_response_model = api.model('MarketSpreads', {
    '*': fields.Float(description='The spread value between buy and sell orders for the market')
})

alert_model = api.model('AlertSpread', {
    'market_id': fields.String(required=True, description='Market identifier for setting alert'),
})

alert_status_model = api.model('AlertStatus', {
    'market_id': fields.String(required=True, description='Market identifier'),
    'current_spread': fields.Float(description='Current spread value'),
    'alert_spread': fields.Float(description='Alert spread value set earlier'),
    'status': fields.String(description='Status comparing current and alert spreads (within, higher, lower)')
})


def fetch_market_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


# Función para obtener el spread de los datos. Asume que los datos enviados por el endpoint estan siempre en
# El orden correcto.
def get_spread_from_data(data):
    if data is None:
        return None

    asks = data['order_book']['asks']
    bids = data['order_book']['bids']

    if not asks or not bids:
        return None

    # Segun la documentación de Buda.com, los datos siempre vienen ordenados en menor precio para asks y mayor precio
    # para bids.
    lowest_ask = float(asks[0][0])
    highest_bid = float(bids[0][0])

    spread = lowest_ask - highest_bid
    return spread


def get_spread(market_id):
    assert isinstance(market_id, str)
    url = f"https://buda.com/api/v2/markets/{market_id}/order_book"
    data = fetch_market_data(url)
    return get_spread_from_data(data)


def fetch_all_markets():
    url = "https://buda.com/api/v2/markets"
    data = fetch_market_data(url)
    if data is None:
        return None, "Error fetching markets"
    return data['markets'], None


@ns.route('/')
class MarketList(Resource):
    @api.response(200, 'Successful')
    @api.response(500, 'Failed to fetch data')
    def get(self):
        """
        Retrieves a list of all markets from the API.
        """
        markets, error = fetch_all_markets()
        if error:
            api.abort(500, error)
        return markets


@ns.route('/spreads')
class MarketSpread(Resource):
    @api.doc(params={'market_id': 'An optional market ID to fetch spread for a specific market'})
    @api.response(200, 'Successful', model=spread_response_model)
    @api.response(500, 'Failed to fetch data')
    def get(self):
        """
        Returns spread data for all markets or a specific market if market_id is provided.
        """
        market_id = request.args.get('market_id')
        if market_id:
            spread = get_spread(market_id)
            if spread is None:
                api.abort(500, "This market does not exist or has no data available.")
            return {market_id: spread}
        else:
            markets, error = fetch_all_markets()
            if error:
                api.abort(500, error)
            spreads = {market['id']: get_spread(market['id']) for market in markets if
                       get_spread(market['id']) is not None}
            return spreads


@ns.route('/alert_spread')
@api.response(400, 'Bad Request')
@api.response(500, 'Internal Server Error')
class MarketAlertSpread(Resource):

    @api.doc(description="Sets the alert spread for a specific market based on the current spread.")
    @api.expect(alert_model, validate=True)
    @api.response(200, 'Alert spread successfully set', model=alert_model)
    def post(self):
        """
        Sets the alert spread for a specific market.
        """
        data = request.json
        market_id = data.get('market_id')
        spread = get_spread(market_id)

        if spread is None:
            api.abort(500, "Could not fetch spread for this market")

        if not market_id or spread is None:
            api.abort(400, "Both market_id and spread are required")

        alert_spread['market_id'] = market_id
        alert_spread['spread'] = spread

        return {"message": "Alert spread set for market_id: {}".format(market_id)}

    @api.doc(description="Retrieves the alert spread status for the market.")
    @api.response(200, 'Alert spread status retrieved', model=alert_status_model)
    @api.response(404, 'No alert spread set for this market')
    def get(self):
        """
            Retrieves the alert spread status for the market.
            """
        market_id = alert_spread['market_id']

        if not market_id:
            api.abort(400, "There is no alert spread set for any market")

        if market_id != alert_spread['market_id']:
            api.abort(404, "No alert spread set for this market")

        current_spread = get_spread(market_id)
        if current_spread is None:
            api.abort(500, "Could not fetch current spread")

        alert_value = alert_spread['spread']
        status = "within" if current_spread == alert_value else ("higher" if current_spread > alert_value else "lower")

        return {
            "market_id": market_id,
            "current_spread": current_spread,
            "alert_spread": alert_value,
            "status": status
        }


if __name__ == '__main__':
    app.run(debug=True)
