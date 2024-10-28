from flask import Flask, request, send_file
from flask_cors import CORS
import pm4py
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
import os
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/process_log', methods=['POST'])
def process_log():
    log_path = None
    output_path = None
    
    try:
        if 'file' not in request.files:
            return "No file part in the request", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if file:
            log_path = os.path.join("/tmp", file.filename)
            file.save(log_path)
            
            log = pm4py.read_xes(log_path)
            bpmn_graph = pm4py.discover_bpmn_inductive(log)
            
            # Apply layout to avoid overlapping elements
            pm4py.objects.bpmn.layout.variants.graphviz.apply(bpmn_graph)
            
            output_path = os.path.join("/tmp", "output.bpmn")
            bpmn_exporter.apply(bpmn_graph, output_path)
            
            return send_file(output_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return f"An error occurred: {str(e)}", 500
    finally:
        if log_path and os.path.exists(log_path):
            os.remove(log_path)
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)








# from flask import Flask, request, send_file
# from flask_cors import CORS
# import pm4py
# from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
# import os
# import logging

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})  # 启用CORS

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# @app.route('/process_log', methods=['POST'])
# def process_log():
#     try:
#         if 'file' not in request.files:
#             return "No file part in the request", 400

#         file = request.files['file']
#         if file.filename == '':
#             return "No selected file", 400

#         if file:
#             log_path = os.path.join("/tmp", file.filename)
#             file.save(log_path)
            
#             log = pm4py.read_xes(log_path)
#             bpmn_graph = pm4py.discover_bpmn_inductive(log)
            
#             output_path = os.path.join("/tmp", "output.bpmn")
#             bpmn_exporter.apply(bpmn_graph, output_path)
            
#             return send_file(output_path, as_attachment=True)
#     except Exception as e:
#         logging.error(f"Error processing file: {e}")
#         return f"An error occurred: {str(e)}", 500
#     finally:
#         if os.path.exists(log_path):
#             os.remove(log_path)
#         if os.path.exists(output_path):
#             os.remove(output_path)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=8000)
