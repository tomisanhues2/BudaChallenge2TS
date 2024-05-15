import json
from flask_testing import TestCase
from app.spread import app


class TestFlaskApi(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_get_all_spreads_no_market_id(self):
        response = self.client.get('/markets/spreads')
        self.assertEqual(response.status_code, 200)

    def test_get_all_spreads_specific_market(self):
        response = self.client.get('/markets/spreads', query_string={'market_id': 'btc-clp'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('btc-clp', response.json)

    def test_set_alert_spread_valid(self):
        response = self.client.post('/markets/alert_spread', data=json.dumps({'market_id': 'btc-clp'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Alert spread set for market_id: btc-clp', response.json['message'])

    def test_poll_alert_spread(self):
        # Diferentes maneras de hacer esto, utilizar TestSuite para ordenar las pruebas dependientes
        # En este caso, manualmente se ejecutan las pruebas en el orden correcto

        response = self.client.post('/markets/alert_spread', data=json.dumps({'market_id': 'btc-clp'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Alert spread set for market_id: btc-clp', response.json['message'])

        response = self.client.get('/markets/alert_spread')
        self.assertEqual(response.status_code, 200)

# Añade más pruebas conforme sea necesario

if __name__ == '__main__':
    import unittest

    unittest.main()
