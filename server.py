import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flasgger import Swagger
from pymongo import MongoClient, errors
import datetime
import certifi
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "airline"

swagger = Swagger(app)
jwt = JWTManager(app)

MONGO_URI = os.getenv("MONGO_URI")
app.config["MONGO_URI"] = MONGO_URI

mongo_client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = mongo_client.get_database("airline")
flights_collection = db.get_collection("flights")
tickets_collection = db.get_collection("tickets")


@app.route("/")
def home():
    return "Welcome to the Airline API - SE 4458 Software Architecture & Design of Modern Large Scale Systems - Midterm 1"


@app.route("/api/v1/admin/login", methods=["POST"])
def admin_login():
    """
    Admin login to get JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: True
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      200:
        description: JWT token
      401:
        description: Invalid credentials
    """
    data = request.json
    if data["username"] == "admin" and data["password"] == "password":
        access_token = create_access_token(
            identity="admin", expires_delta=datetime.timedelta(hours=1)
        )
        return jsonify({"access_token": access_token}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/v1/admin/insert-flight", methods=["POST"])
@jwt_required()
def insert_flight():
    """
    Insert a new flight
    ---
    tags:
      - Admin
    parameters:
      - name: body
        in: body
        required: True
        schema:
          type: object
          properties:
            from:
              type: string
            to:
              type: string
            availableDates:
              type: array
              items:
                type: string
            days:
              type: array
              items:
                type: string
            capacity:
              type: integer
          required:
            - from
            - to
            - availableDates
            - days
            - capacity
    responses:
      201:
        description: Flight created successfully
      400:
        description: Missing or invalid fields
    """
    if db is None:
        return jsonify({"error": "Database connection not established"}), 500

    data = request.json
    required_fields = {"from", "to", "availableDates", "days", "capacity"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    flight_id = flights_collection.insert_one(data).inserted_id
    return jsonify({"status": "Successful", "flight_id": str(flight_id)}), 201


@app.route("/api/v1/admin/report-flights", methods=["GET"])
@jwt_required()
def report_flights():
    """
    Report flights with capacity
    ---
    tags:
      - Admin
    parameters:
      - name: from
        in: query
        type: string
      - name: to
        in: query
        type: string
    responses:
      200:
        description: List of flights with capacity
    """
    if db is None:
        return jsonify({"error": "Database connection not established"}), 500

    query_params = request.args
    from_city = query_params.get("from")
    to_city = query_params.get("to")

    filters = {}
    if from_city:
        filters["from"] = from_city
    if to_city:
        filters["to"] = to_city

    result = list(flights_collection.find(filters))
    for flight in result:
        flight["_id"] = str(flight["_id"])
    return jsonify({"flights": result}), 200


@app.route("/api/v1/client/query-flights", methods=["GET"])
def query_flights():
    """
    Query available flights
    ---
    tags:
      - Client
    parameters:
      - name: date
        in: query
        type: string
      - name: from
        in: query
        type: string
      - name: to
        in: query
        type: string
    responses:
      200:
        description: List of flights
    """
    if db is None:
        return jsonify({"error": "Database connection not established"}), 500

    query_params = request.args
    date = query_params.get("date")
    from_city = query_params.get("from")
    to_city = query_params.get("to")

    filters = {"availableDates": date, "from": from_city, "to": to_city}

    result = list(flights_collection.find(filters, {"_id": 0}))
    return jsonify({"flights": result}), 200


@app.route("/api/v1/client/buy-ticket", methods=["POST"])
def buy_ticket():
    """
    Buy a ticket for a flight
    ---
    tags:
      - Client
    parameters:
      - name: body
        in: body
        required: True
        schema:
          type: object
          properties:
            date:
              type: string
            from:
              type: string
            to:
              type: string
            passengerName:
              type: string
          required:
            - date
            - from
            - to
            - passengerName
    responses:
      201:
        description: Ticket created successfully
    """
    if db is None:
        return jsonify({"error": "Database connection not established"}), 500

    data = request.json
    required_fields = {"date", "from", "to", "passengerName"}
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    flight = flights_collection.find_one(
        {"from": data["from"], "to": data["to"], "availableDates": data["date"]}
    )

    if not flight or flight.get("capacity", 0) < 1:
        return jsonify({"status": "Error", "message": "No available seats"}), 400

    flights_collection.update_one({"_id": flight["_id"]}, {"$inc": {"capacity": -1}})
    ticket_id = tickets_collection.insert_one(
        {
            "flightId": str(flight["_id"]),
            "passengerName": data["passengerName"],
            "date": data["date"],
        }
    ).inserted_id

    return jsonify({"status": "Successful", "ticket_id": str(ticket_id)}), 201


@app.route("/api/v1/client/check-in", methods=["POST"])
def check_in():
    """
    Check-in to a flight
    ---
    tags:
      - Client
    parameters:
      - name: body
        in: body
        required: True
        schema:
          type: object
          properties:
            ticketId:
              type: string
          required:
            - ticketId
    responses:
      200:
        description: Check-in successful
    """
    if db is None:
        return jsonify({"error": "Database connection not established"}), 500

    data = request.json
    ticket_id = data.get("ticketId")

    if not ticket_id:
        return jsonify({"error": "Missing ticket ID"}), 400

    try:
        ticket_object_id = ObjectId(ticket_id)
    except Exception as e:
        return jsonify({"error": "Invalid ticket ID format", "details": str(e)}), 400

    ticket = tickets_collection.find_one({"_id": ticket_object_id})

    if not ticket:
        return jsonify({"status": "Error", "message": "Ticket not found"}), 404

    tickets_collection.update_one(
        {"_id": ticket_object_id}, {"$set": {"checkedIn": True}}
    )
    return jsonify({"status": "Successful"}), 200


if __name__ == "__main__":
    app.run()
