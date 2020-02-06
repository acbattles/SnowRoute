#! /usr/bin/env python

from flask import Flask, render_template, request
from mapbox import Geocoder, Directions
from shapely.geometry import Point, LineString
import pandas as pd
import numpy as np
import geopandas
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
from geoalchemy2 import Geometry



app = Flask(__name__)
app.config.from_object(__name__)

#def get_point():


def geodb_query(list_x):
    
    #change to the NEW DB (and make sure it's alligned in the app online)
    con = psycopg2.connect(database = 'intersections', user = 'postgres', password = 'andrew17')
    inters_sql_df = pd.DataFrame()
    for i in list_x:
        sql_query = """
        SELECT * FROM intersections_class_table
        WHERE ST_Within(geometry, ST_Buffer(ST_MakePoint{x},0.0001));
        """.format(x=i)
    
        inters_sql_df = inters_sql_df.append(pd.read_sql_query(sql_query,con))

    return inters_sql_df

def risk_calc(inters_df):
    sml_avg = 0.00139
    med_avg = 0.00205
    wde_avg = 0.00042
    
    sml_rel=0
    med_rel=0
    wde_rel=0

    x1 = inters_df.groupby('Road_Width')['Prediction'].sum()
    x2 = list(inters_df['Road_Width'])
    
    if 'Small' in x2:
        sml_rel=x1['Small']/sml_avg
        
    if 'Medium' in x2:
        med_rel=x1['Medium']/med_avg
    
    if 'Wide' in x2:
        wde_rel=x1['Wide']/wde_avg
    
    sum_risk = sum([sml_rel,med_rel,wde_rel])

    return sum_risk

#def safe_route(x1,x2):


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

    route = directions.directions([origin,destination], 'mapbox/driving', alternatives=True, exclude = 'motorway')
    route1 = route.geojson()['features'][0]
    route2 = route.geojson()['features'][1]

    #makes a list of the start/end coordinates on each line segment of the route
    coord_points_alt1 = route1['geometry']['coordinates']
    coord_points_alt2 = route2['geometry']['coordinates']

    #get the coordinates for TURNS (at this point)
    intersections_df1 = geodb_query(coord_points_alt1)
    intersections_df2 = geodb_query(coord_points_alt2)

    #get the relative risk at each turn.
    total_risk1 = intersections_df1['Pred_Prob'].max()
    total_risk2 = intersections_df2['Pred_Prob'].max()

    if total_risk1 < total_risk2:
        best_route = route1
        next_route = route2
        risk_out_low = round(total_risk1,1)
        risk_out_high = round(total_risk2,1)
    else:
        best_route = route2
        next_route = route1
        risk_out_low = round(total_risk2,1)
        risk_out_high = round(total_risk1,1)
    
    return render_template("output.html", routeA = best_route, routeB = next_route, origin = origin, destination = destination,
    risk1 = risk_out_low, risk2 = risk_out_high)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)