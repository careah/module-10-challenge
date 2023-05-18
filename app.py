from flask import Flask, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt
from sqlalchemy.ext.automap import automap_base

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create an instance of Flask
app = Flask(__name__)

# Define the routes

@app.route("/")
def home():
    
    return (
        f"Welcome to Hawaii Climate<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
        f"** start & end date format: yyyy-mm-dd<br/>"
        f"Ex.  2017-01-01/2017-02-01"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.date.fromisoformat(recent_date) - dt.timedelta(days=365)
    #The last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    session.close()

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    #A list of stations
    stations = session.query(Station.station).all()
    station_list = list(np.ravel(stations))
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #The previous year's temperature observations for the most active station
    recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.date.fromisoformat(recent_date) - dt.timedelta(days=365)

    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year).\
        filter(Measurement.station == "USC00519281").all()

    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
    session.close()
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    #Temperature statistics (TMIN, TAVG, TMAX) from a start date"""
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temp_stats_list = list(np.ravel(temp_stats))
    session.close()
    return jsonify(temp_stats_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    #Temperature statistics (TMIN, TAVG, TMAX) for a date range
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    print(start)
    print(end)
    temp_stats_list = list(np.ravel(temp_stats))
    session.close()
    return jsonify(temp_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
