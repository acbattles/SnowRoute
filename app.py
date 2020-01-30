from flask import Flask, render_template, request
from mapbox import Geocoder, Directions
from shapely.geometry import Point, LineString
import pandas
import geopandas



app = Flask(__name__)



@app.route('/')
def input_data():
    return render_template('input.html')


@app.route('/output', methods=['GET','POST'])
def output():
    #get the lat/long of origin and destination
    geocoder = Geocoder()
    geocoder.session.params['access_token'] = 'pk.eyJ1IjoiYWNiYXR0bGVzIiwiYSI6ImNrNXptdWtnajA4ZGYzamxscmR5ZmV4ZGEifQ.e99budVtY2MsprEhvTNEtQ'
    directions = Directions()
    directions.session.params['access_token'] = 'pk.eyJ1IjoiYWNiYXR0bGVzIiwiYSI6ImNrNXptdWtnajA4ZGYzamxscmR5ZmV4ZGEifQ.e99budVtY2MsprEhvTNEtQ'

    starting_location = request.args.get('starting_location')
    ending_location = request.args.get('ending_location')
    #possibly code in auto-responses if nothing input to not break app

    start_geo = geocoder.forward(starting_location)
    end_geo = geocoder.forward(ending_location)
    
    origin = start_geo.geojson()['features'][0]
    destination = end_geo.geojson()['features'][0]

    route1 = directions.directions([origin,destination], 'mapbox/driving').geojson()

    
    return render_template("output.html", the_route = route1)


if __name__ == "__main__":
    app.run(debug=True)