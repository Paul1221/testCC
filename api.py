import flask
from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import http.client
import json
from webargs import fields, validate
from webargs.flaskparser import use_kwargs, parser
from time import time

app = Flask(__name__)
api = Api(app)


class Metrics(Resource):
    def get(self):
        f = open("Logs.txt", "r+")
        response = flask.jsonify(f.read())
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


class Forecast(Resource):
    args = {
        'city': fields.Str(
            required=True
        )
    }

    @use_kwargs(args, location="query")
    def get(self, city):
        f = open("Logs.txt", "a+")
        t1 = time()
        conn = http.client.HTTPSConnection("us1.locationiq.com")
        conn.request("GET", f"/v1/search.php?key=pk.331505d7975105bc642b581761934a18&q={city}&format=json&limit=1")
        t2 = time()
        r1 = conn.getresponse().read().decode()
        r1 = r1[1:]
        r1 = r1[:-1]
        coords = {'lat': json.loads(r1)["lat"], 'lon': json.loads(r1)["lon"]}
        f.write(f"Request: [GET] us1.locationiq.com"
                f"/v1/search.php?key=pk.331505d7975105bc642b581761934a18&q={city}&format=json&limit=1<br>"
                f"Response: {json.dumps(coords)}<br>"
                f"Latency: {t2 - t1}<br><br>")

        t1 = time()
        conn = http.client.HTTPSConnection("www.random.org")
        conn.request("GET", "/integers/?num=1&min=1&max=3&col=1&base=10&format=plain&rnd=new")
        t2 = time()
        r1 = conn.getresponse().read().decode()
        nr_of_days = int(r1)
        f.write(f"Request: [GET] www.random.org"
                f"/integers/?num=1&min=1&max=3&col=1&base=10&format=plain&rnd=new<br>"
                f"Response: {r1}<br>"
                f"Latency: {t2 - t1}<br><br>")

        t1 = time()
        conn = http.client.HTTPSConnection("api.weatherapi.com")
        conn.request("GET", f'/v1/forecast.json?key=16998a0ff0a14ffca37134802212502&'
                            f'q={coords["lat"]},{coords["lon"]}&days={nr_of_days}')
        t2 = time()

        r1 = conn.getresponse().read().decode()

        days = ["Azi", "Maine", "Poimaine"]
        forecast = {}

        for i in range(nr_of_days):
            forecast.update({days[i]: json.loads(r1)["forecast"]["forecastday"][i]["day"]["maxtemp_c"]})

        f.write(f"Request: [GET] api.weatherapi.com"
                f'/v1/forecast.json?key=16998a0ff0a14ffca37134802212502&'
                f'q={coords["lat"]},{coords["lon"]}&days={nr_of_days}<br>'
                f"Response: {json.dumps(forecast)}<br>"
                f"Latency: {t2 - t1}<br><br>")
        f.flush()
        f.close()

        response = flask.jsonify(forecast)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)


api.add_resource(Metrics, '/metrics/', endpoint='metrics')
api.add_resource(Forecast, '/forecast/', endpoint='forecast')

if __name__ == '__main__':
    app.run()