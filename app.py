from flask import Flask, request, jsonify, render_template  
from pymongo import MongoClient
import os
import datetime
import hashlib


app = Flask(__name__)

# MongoDB Config
# mongo_uri = "mongodb://localhost:27017"
mongo_uri = "mongodb://host.docker.internal:27017/"

client = MongoClient(mongo_uri)
db = client["github_actions"]  
collection = db["Tstax-A"]  

# Webhook Endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()  

    try:
        if 'commits' in data:
            process_push(data)
        elif 'pull_request' in data:
            if 'action' not in data:  
                print("Warning: 'action' key not found in pull request payload")
                return jsonify({"error": "Invalid pull request payload: missing 'action' key"}), 400
            
            if data['action'] == 'opened' or data['action'] == 'reopened' or data['action'] == 'synchronize':
                process_pull_request(data)
            elif data['action'] == 'closed' and data['pull_request']['merged']:
                process_merge(data)
            else:
                print(f"Warning: Unhandled pull request action: {data['action']}")
                return jsonify({"error": f"Unhandled pull request action: {data['action']}"}), 400
        else:
            print("Warning: Unknown webhook event type")
            return jsonify({"error": "Unknown webhook event type"}), 400

        return jsonify({"message": "Webhook received and processed"}), 200

    except Exception as e:  
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

def process_push(data):
    for commit in data['commits']:
        event = {
            "request_id": commit['id'],
            "author": commit['author']['name'],
            "action": "PUSH",
            "from_branch": None,  
            "to_branch": data['ref'].split('/')[-1],  
            "timestamp": commit['timestamp']
        }
        collection.insert_one(event)

def process_pull_request(data):
    event = {
        "request_id": str(data['number']),
        "author": data['pull_request']['user']['login'],
        "action": "PULL_REQUEST",
        "from_branch": data['pull_request']['head']['ref'],
        "to_branch": data['pull_request']['base']['ref'],
        "timestamp": data['pull_request']['created_at']
    }
    collection.insert_one(event)

def process_merge(data):
    event = {
        "request_id": hashlib.sha256((str(data['number']) + data['pull_request']['merged_at']).encode()).hexdigest(),
        "author": data['pull_request']['merged_by']['login'],
        "action": "MERGE",
        "from_branch": data['pull_request']['head']['ref'],
        "to_branch": data['pull_request']['base']['ref'],
        "timestamp": data['pull_request']['merged_at']
    }
    collection.insert_one(event)

# Endpoint to fetch data for UI
@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))  # Fetch all events, exclude _id field, sort by timestamp descending
    return jsonify(events)


# Serving the index.html
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)