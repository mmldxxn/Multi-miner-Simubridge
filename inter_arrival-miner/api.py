# api_flask.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pm4py.objects.log.importer.xes import importer as xes_importer
from interarrival import find_inter_arrival_distribution
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/inter-arrival', methods=['POST'])
def upload_log():
    if 'file' not in request.files:
        return "No file part", 400

    file = request.files['file']

    if file.filename == '':
        return "No selected file", 400

    if file:
        filepath = "inter-arrival.xes"
        file.save(filepath)

        log = xes_importer.apply(filepath)
        arrival_distribution = find_inter_arrival_distribution(log)
        
        return app.response_class(
            response=json.dumps(arrival_distribution),
            mimetype='application/json'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)
