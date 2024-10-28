from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import BaseModel
from pm4py.objects.log.importer.xes import importer as xes_importer
from resource_calendars import structured_resource_calendar
from role_resource import get_activity_resources
import json

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

class LogFile(BaseModel):
    path: str

@app.route("/resource-calendars/", methods=["POST"])
def resource_calendars():
    try:
        file = request.files['file']
        filepath = "log.xes"
        file.save(filepath)
        log = xes_importer.apply(filepath)
        calendars = structured_resource_calendar(log)
        return app.response_class(
            response=json.dumps(calendars),
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error": str(e)}),
            mimetype='application/json'
        ), 500

@app.route("/role-resources/", methods=["POST"])
def role_resources():
    try:
        file = request.files['file']
        filepath = "log.xes"
        file.save(filepath)
        log = xes_importer.apply(filepath)
        resources = get_activity_resources(log)
        return app.response_class(
            response=json.dumps(resources),
            mimetype='application/json'
        )
    except Exception as e:
        return app.response_class(
            response=json.dumps({"error": str(e)}),
            mimetype='application/json'
        ), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8001)
