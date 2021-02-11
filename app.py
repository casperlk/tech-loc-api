import json, time
from flask import Flask, jsonify, request
import haversine as hs
# from flask.ext.login import (current_user, LoginManager, login_user, logout_user, login_required)

app = Flask(__name__)

maxTimeDiff = 0     # maximum permissible time difference for two location reports for techs to be considered colocated (in seconds, within a given payload)
reportIndex = 0     # Index of current technician location geojson
apiVersionNumber = '1'
farmID = '000001'   # unique identifier for the solar farm

# open the response data and load it as a dictionary
with open('api_techician_response_data.json') as f:
    techLocationData = json.load(f)

numberOfReports = len(techLocationData)     # Number of tech location reports in example file

@app.route('/api/v' + apiVersionNumber + '/solar_farms/' + farmID + '/colocated_technicians')
def query_colocated_techs():
    global reportIndex
    return jsonify(findColocatedTechs(techLocationData[reportIndex]))

@app.route('/api/v' + apiVersionNumber + '/solar_farms/' + farmID + '/technicians', methods=['GET'])
def query_tech_loc():
    global reportIndex
    payload = techLocationData[reportIndex]
    reportIndex = reportIndex + 1 if reportIndex < (numberOfReports - 1) else 0
    return jsonify(payload)


def findColocatedTechs(techReport):
    techPairs = []      # techPairs contains pairs of indices of colocated technicians
    global maxTimeDiff

    numberOfTechs = len(techReport['features'])
    for i in range(0, numberOfTechs - 1):
        for j in range(i + 1, numberOfTechs):
            time1 = techReport['features'][i]['properties']['tsecs']
            time2 = techReport['features'][j]['properties']['tsecs']
            diffTime = abs(time1 - time2)
            if diffTime <= maxTimeDiff:
                loc1 = techReport['features'][i]['geometry']['coordinates']
                loc2 = techReport['features'][j]['geometry']['coordinates']
                if hs.haversine(loc1,loc2) < 0.3048:
                    techPairs.append([i,j])
    return techPairs

if __name__ == "__main__":
    app.run(debug=True)


