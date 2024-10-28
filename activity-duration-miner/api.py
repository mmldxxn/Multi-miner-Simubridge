from flask import Flask, request, jsonify
from flask_cors import CORS
import pm4py
import os
import tempfile
from activities_duration import find_execution_distributions
from pm4py.objects.log.importer.xes import importer as xes_importer
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

@app.route('/activity_duration', methods=['POST'])
def upload_xes():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.xes'):
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xes')
        file.save(temp_file.name)
        temp_file.close()

        try:
            # Read the XES file using pm4py
            log = xes_importer.apply(temp_file.name)
        finally:
            # Ensure the temporary file is removed
            os.remove(temp_file.name)

        # Process the log
        acd = find_execution_distributions(log)
        
        return app.response_class(
            response=json.dumps(acd),
            mimetype='application/json'
        )
    else:
        return jsonify({'error': 'Invalid file format. Please upload a .xes file'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)
