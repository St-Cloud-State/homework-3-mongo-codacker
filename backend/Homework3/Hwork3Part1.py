from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

# Initialize Flask app
app = Flask(__name__)

# Set up MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client['loan_application_db']  # Database name
collection = db['applications']    # Collection name


# Define a route for the root URL
@app.route('/')
def home():
    return "Welcome to the MongoDB Loan Application System!"

# Handle favicon request (optional)
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content

# Create a loan application
@app.route('/apply', methods=['POST'])
def apply_loan():
    data = request.get_json()  # Get JSON data from the request

    # Ensure all required fields are present
    if 'name' not in data or 'amount' not in data:
        return jsonify({"message": "Missing required fields: 'name' or 'amount'"}), 400

    # Create a loan application document
    new_application = {
        "name": data['name'],
        "amount": data['amount'],
        "status": "Pending",  # Default status
        "notes": data.get('notes', [])
    }

    # Insert the document into MongoDB collection
    collection.insert_one(new_application)

    return jsonify({"message": "Application submitted successfully!"}), 201

# View application status
@app.route('/application/<application_id>', methods=['GET'])
def get_application(application_id):
    # Convert string ID to ObjectId
    try:
        app_id = ObjectId(application_id)
    except Exception as e:
        return jsonify({"message": "Invalid application ID format"}), 400

    application = collection.find_one({"_id": app_id})

    if application:
        # Remove _id before returning to client
        application['_id'] = str(application['_id'])
        return jsonify(application), 200
    else:
        return jsonify({"message": "Application not found"}), 404

# Update application status
@app.route('/application/<application_id>', methods=['PUT'])
def update_status(application_id):
    data = request.get_json()

    # Ensure the new status is valid
    if 'status' not in data:
        return jsonify({"message": "Missing status field"}), 400

    new_status = data['status']

    # Convert string ID to ObjectId
    try:
        app_id = ObjectId(application_id)
    except Exception as e:
        return jsonify({"message": "Invalid application ID format"}), 400

    result = collection.update_one(
        {"_id": app_id},
        {"$set": {"status": new_status}}
    )

    if result.matched_count > 0:
        return jsonify({"message": "Status updated successfully!"}), 200
    else:
        return jsonify({"message": "Application not found"}), 404

# Add notes to the application
@app.route('/application/<application_id>/notes', methods=['PATCH'])
def add_notes(application_id):
    data = request.get_json()

    # Ensure the note is provided
    if 'note' not in data:
        return jsonify({"message": "Missing note field"}), 400

    note = data['note']

    # Convert string ID to ObjectId
    try:
        app_id = ObjectId(application_id)
    except Exception as e:
        return jsonify({"message": "Invalid application ID format"}), 400

    # Update the application by adding the note
    result = collection.update_one(
        {"_id": app_id},
        {"$push": {"notes": note}}  # Adding note to the 'notes' field
    )

    if result.matched_count > 0:
        return jsonify({"message": "Note added successfully!"}), 200
    else:
        return jsonify({"message": "Application not found"}), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
