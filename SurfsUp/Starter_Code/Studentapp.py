# Import the dependencies.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.types import Date
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import func
from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.metadata.create_all(engine)

# reflect an existing database into a new model
# reflect the tables

class Measurement(Base):
    __tablename__ = "measurement"
    id = Column(Integer, primary_key=True)
    station = Column(String(255))
    date = Column(Date)
    prcp = Column(Float)
    tobs = Column(Integer)

# Save references to each table
class Station(Base):
    __tablename__ = "station"
    id = Column(Integer, primary_key=True)
    station = Column(String(255))
    name = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)



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
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>" 
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"Please enter dates in the format YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")

def precipitation():
    """Return a list of all precipitation data"""
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of precipitation
    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")

def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")

def tobs():
    """Return a list of all temperature observations for the previous year"""
    # Query all temperature observations for the previous year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]
    last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
    year_ago = last_date - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(results))

    return jsonify(tobs)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start_end(start=None, end=None):
    """Return a list of all temperature observations for the previous year"""
    # Query all temperature observations for the previous year
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
