import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)
# CORS(app)

@app.route("/")
def welcome():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start>/<end></br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    prcpresults = session.query(Measurement.prcp).all() 
    dateresults = session.query(Measurement.date).all()
    session.close()

    # Convert list of tuples into normal list
    precip = list(np.ravel(prcpresults))
    date = list(np.ravel(dateresults))

    measurement_dict = {}

    for x in range(len(date)):
        measurement_dict[date[x]] = precip[x]

    return jsonify(measurement_dict)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stationresults = session.query(Station.station).all()
    return jsonify(stationresults)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    measurement_dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(measurement_dates, '%Y-%m-%d')
    last_year = dt.date(last_date.year -1, last_date.month, last_date.day)
    tobs_dates = [Measurement.date, Measurement.tobs]
    query_results = session.query(*tobs_dates).filter(Measurement.date >= last_year).all()
    session.close()

    tobs_list = []

    for date, tobs in query_results:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)




@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    tobs_list = []

    for min, avg, max in start_query:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Avg"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


@app.route('/api/v1.0/<start>/<end>')
def get_dates(start,end):
    session = Session(engine)
    date_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    tobs_list = []

    for min, avg, max in date_query:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Avg"] = avg
        tobs_dict["Max"] = max
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)


if __name__ == '__main__':
    app.run(debug=True)
