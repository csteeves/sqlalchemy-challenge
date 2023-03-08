# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session= Session(engine)
    # Query for last 12 months of data
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(most_recent_date,"%Y-%m-%d")-dt.timedelta(days=365)
    year_ago_date = year_ago.strftime("%Y-%m-%d")
    precipitation_scores = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=year_ago_date).order_by(Measurement.date.desc()).all()
    # Create empty list for dictionaries
    precipitation_list=[]
    # loop through query, covert to dictionary, append list
    for date,prcp in precipitation_scores:
        m_dict={}
        m_dict[date]= prcp
        precipitation_list.append(m_dict)
    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session= Session(engine)
    # Query for stations
    station_names = session.query(Station.name,Station.station, Station.latitude, Station.longitude, Station.elevation).all()
    station_list = []
    for station,name,latitude,longitude,elevation in station_names:
        station_dict={}
        station_dict["name"]=name
        station_dict["station"]=station
        station_dict["lattitude"]=latitude
        station_dict["longitutde"]=longitude
        station_dict["elevation"]=elevation
        station_list.append(station_dict)
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session= Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    year_ago = dt.datetime.strptime(most_recent_date,"%Y-%m-%d")-dt.timedelta(days=365)
    year_ago_date = year_ago.strftime("%Y-%m-%d")
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    most_active_station = 'USC00519281'
    sel=[Measurement.date,Measurement.tobs]
    station_temps = session.query(*sel).filter(Measurement.station == most_active_station).filter(Measurement.date>=year_ago_date).all()
    # loop through query, append list
    most_active_station_list=[]
    for date,tobs in station_temps:
        most_active_dict={}
        most_active_dict["Date"]= date
        most_active_dict["Temp"]= tobs
        most_active_station_list.append(most_active_dict)
    return jsonify(most_active_station_list)

@app.route("/api/v1.0/<start>")
def starting(start):
    # Create our session (link) from Python to the DB
    session= Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    sel = [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    search_query = session.query(*sel).filter(Measurement.date.between(start,most_recent_date))

    start_list = []
    for min,max,avg in search_query:
        start_dict={}
        start_dict['min']=min
        start_dict['max']=max
        start_dict['avg']=avg
        start_list.append(start_dict)
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def ending(start,end):
    # Create our session (link) from Python to the DB
    session= Session(engine)
    sel= [func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    search_query= session.query(*sel).filter(Measurement.date.between(start,end)).all()
    start_stop_list= []
    for min,max,avg in search_query:
        start_stop_dict={}
        start_stop_dict['Min']=min
        start_stop_dict['Max']=max
        start_stop_dict['Avg']=avg
        start_stop_list.append(start_stop_dict)
    return jsonify(start_stop_list)

if __name__ == '__main__':
    app.run(debug=True)