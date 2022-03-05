#Dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Data/hawaii.sqlite")

# Reflect Database into classes
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

print(Base.classes.keys())



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    last_date = session.query(func.max(measurement.date)).scalar()
    max_date= dt.datetime.strptime(last_date, '%Y-%m-%d') 
    begin_date = max_date - dt.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).\
            filter(measurement.date >= begin_date).order_by(measurement.date).all()

    session.close() 

    precipitation_date = []
    for date, prcp in results:
        if prcp != None:
            precipitation_dict = {} 
            precipitation_dict = precipitation_date.append(precipitation_dict)

    return jsonify(precipitation_date)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of all station names"""
    # Query all station names
    results = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = session.query(func.max(measurement.date)).scalar()
    max_date= dt.datetime.strptime(last_date, '%Y-%m-%d') 
    begin_date = max_date - dt.timedelta(days=365)
   
    # Find the most active station.
    active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count().desc()).\
        first()
    # Get the station id of the most active station.
    (most_active_station_id, ) = active_station
    print(
        f"The station id of the most active station is {most_active_station_id}.")

    results = session.query(measurement.date, measurement.tobs).filter(
        measurement.station == most_active_station_id).filter(measurement.date >= begin_date).all()
    print (begin_date)
    session.close()  

      #create list of dictionaries (one for each observation)
    temp_list = []
    for result in results:
        temp_dict = {}
        temp_dict["date"] = result.date
        temp_dict["tobs"] = result.tobs
        temp_list.append(temp_dict)

    return jsonify(temp_list)

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def temps_dates(start, end):
     session = Session(engine)
    # If we have both a start date and an end date.
     if end != None:
        results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).all()
    # If we only have a start date.
     else:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
            
     session.close()


# Convert the query results to a list.
     temp_list = []
     no_data = False
     for min_temp, avg_temp, max_temp in results:
        if min_temp == None or avg_temp == None or max_temp == None:
             no_data = True
        temp_list.append(min_temp)
        temp_list.append(avg_temp)
        temp_list.append(max_temp)
    # Return the JSON representation of dictionary.
        return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)