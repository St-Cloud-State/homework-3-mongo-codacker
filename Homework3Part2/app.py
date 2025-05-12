from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client["loan_applications"]
applications = db.applications

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/accept_application', methods=['POST'])
def accept_application():
    name = request.form.get('name')
    zipcode = request.form.get('zipcode')
    if not name or not zipcode:
        return jsonify({"error": "Name and zipcode are required."}), 400

    application = {
        "name": name,
        "zipcode": zipcode,
        "status": "received",
        "notes": [],
        "rejection_reason": None,
        "created_at": datetime.datetime.utcnow()
    }
    result = applications.insert_one(application)
    application_id = str(result.inserted_id)
    return jsonify({"message": "Application accepted.", "application_id": application_id}), 201

@app.route('/change_status', methods=['POST'])
def change_status():
    app_id = request.form.get('application_id')
    new_status = request.form.get('new_status')

    if not app_id or not new_status:
        return jsonify({"error": "Application ID and new status required."}), 400

    try:
        result = applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {"status": new_status}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Application not found."}), 404
        return jsonify({"message": "Status updated."}), 200
    except:
        return jsonify({"error": "Invalid application ID."}), 400

@app.route('/add_note', methods=['POST'])
def add_note():
    app_id = request.form.get('application_id')
    phase = request.form.get('phase')
    message = request.form.get('message')

    if not app_id or not phase or not message:
        return jsonify({"error": "All fields required."}), 400

    note = {
        "phase": phase,
        "timestamp": datetime.datetime.utcnow(),
        "message": message
    }

    try:
        result = applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$push": {"notes": note}}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Application not found."}), 404
        return jsonify({"message": "Note added."}), 200
    except:
        return jsonify({"error": "Invalid application ID."}), 400

@app.route('/reject_application', methods=['POST'])
def reject_application():
    app_id = request.form.get('application_id')
    reason = request.form.get('reason')

    if not app_id or not reason:
        return jsonify({"error": "Application ID and reason required."}), 400

    try:
        result = applications.update_one(
            {"_id": ObjectId(app_id)},
            {
                "$set": {
                    "status": "rejected",
                    "rejection_reason": reason
                }
            }
        )
        if result.matched_count == 0:
            return jsonify({"error": "Application not found."}), 404
        return jsonify({"message": "Application rejected."}), 200
    except:
        return jsonify({"error": "Invalid application ID."}), 400

@app.route('/view_notes/<application_id>', methods=['GET'])
def view_notes(application_id):
    try:
        app_data = applications.find_one({"_id": ObjectId(application_id)})
    except:
        return jsonify({"error": "Invalid application ID."}), 400

    if not app_data:
        return jsonify({"error": "Application not found."}), 404

    return jsonify({
        "notes": app_data.get("notes", []),
        "rejection_reason": app_data.get("rejection_reason", None),
        "status": app_data.get("status", "unknown")
    }), 200

if __name__ == '__main__':
    app.run(debug=True)