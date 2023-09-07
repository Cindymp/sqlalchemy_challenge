# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """Homepage - List all available routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert precipitation analysis results to a dictionary and return as JSON."""
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent_date)
    one_year_ago = most_recent_date - pd.DateOffset(years=1)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert data to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    session = Session(engine)
    station_list = session.query(Station.station).all()
    session.close()
    
    # Convert the station list to a JSON list
    stations_json = [station[0] for station in station_list]
    
    return jsonify(stations_json)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query temperature observations for the most active station for the previous year and return as JSON."""
    session = Session(engine)
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = pd.to_datetime(most_recent_date)
    one_year_ago = most_recent_date - pd.DateOffset(years=1)
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    # Convert temperature data to a JSON list
    temperature_json = [{"date": date, "temperature": tobs} for date, tobs in temperature_data]
    
    return jsonify(temperature_json)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return JSON list of TMIN, TAVG, and TMAX for dates greater than or equal to the start date."""
    session = Session(engine)
    start_date = pd.to_datetime(start)
    
    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()

    # Create JSON response
    temp_json = {
        "TMIN": temperature_data[0][0],
        "TAVG": temperature_data[0][1],
        "TMAX": temperature_data[0][2]
    }

    return jsonify(temp_json)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return JSON list of TMIN, TAVG, and TMAX for dates between start and end dates."""
    session = Session(engine)
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)

    temperature_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    # Create JSON response
    temp_json = {
        "TMIN": temperature_data[0][0],
        "TAVG": temperature_data[0][1],
        "TMAX": temperature_data[0][2]
    }

    return jsonify(temp_json)

if __name__ == "__main__":
    app.run(debug=True)
    
