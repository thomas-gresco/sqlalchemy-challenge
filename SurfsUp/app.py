# Design Your Climate App
# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
# Use SQLAlchemy create_engine to connect to your sqlite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
app=Flask(__name__)
#################################################

#################################################
# Flask Routes
#Start at the homepage (/)
#List all routes that are available.
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations<br/>"
        f"/api/v1.0/start<br/>"
        f"- List of the minimum temperature, the average temperature, and the max temperature for a given start date<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- List of the minimum temperature, the average temperature, and the max temperature for a given start-end range<br/>"
    )
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    '''Return a list of prior year rain totals from all stations'''
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').\
        order_by(Measurement.date).all()
    # Create a dictionary from the row data and append to a list of all_precipitation
    #Return the JSON representation of your dictionary.
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)

#################################################

@app.route("/api/v1.0/stations")
def stations():
    '''Return a list of Station numbers and names'''
        #Return a JSON list of stations from the dataset.
    session = Session(engine)
    stations=session.query(Station.name, Station.station).all()
    session.close()
    stations_list=list(np.ravel(stations))
    return jsonify(stations_list)

#################################################

@app.route("/api/v1.0/tobs")
def tobs():
    '''Return a list of prior year temperatures from all stations'''
        #Query the dates and temperature observations of the most active station for the last year of data.
        #Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    most_active=session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
    most_active=most_active[0]
    most_active_temps=session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.station==most_active).\
        order_by(Measurement.date).all()
    session.close()
    most_active_temps_list=list(np.ravel(most_active_temps))
    return jsonify(most_active_temps_list)


#################################################
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None, end=None):
    session=Session(engine)
    sel=[func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results=session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps=list(np.ravel(results))
        return jsonify(temps)
    results=session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    temps=list(np.ravel(results))
    return jsonify(temps)
#################################################

if __name__ == "__main__":
    app.run(debug=True)
