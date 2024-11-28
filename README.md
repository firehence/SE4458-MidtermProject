# Airline API Project

Youtube video linki: https://www.youtube.com/watch?v=QgvTXzLimak


This is a simple API project for managing flights and ticketing for a fictitious airline company, developed using Python and Flask. The API allows admins to manage flights, and clients can book tickets and check-in for flights.

## Features
- **Admin Features**:
  - Insert new flights.
  - Report flights with available capacity.
  
- **Client Features**:
  - Query available flights.
  - Buy tickets for flights.
  - Check-in for flights.

## Technologies Used
- **Python 3**
- **Flask**: Web framework for building the API.
- **Flask-JWT-Extended**: For JSON Web Token (JWT) authentication.
- **Flasgger**: For Swagger UI documentation.
- **PyMongo**: For interacting with MongoDB.
- **MongoDB Atlas**: For cloud database hosting.
- **Dotenv**: For managing environment variables.

## Requirements
You need to have Python 3.6+ installed. To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Setting Up the Project

1. Clone the Repository

Run the following command to clone the project repository:

```bash
git clone https://github.com/yourusername/airline-api.git
cd airline-api
```

2. Install Dependencies

Run the following command to install the required packages:

```bash
pip install -r requirements.txt
```

3. Set Up MongoDB

Make sure you have an active MongoDB Atlas account and set up a cluster. Replace the MongoDB URI in the .env with your own URI.

```python
MONGO_URI = "your_mongo_atlas_uri"
```

4. Running the Application

To start the Flask application, run:

```bash
python app.py

```
The app will be accessible at http://127.0.0.1:5000.

5. Accessing the Swagger API Documentation

The Swagger API documentation is available at:

http://127.0.0.1:5000/apidocs

## API Endpoints

### Admin Endpoints

	1.	POST /api/v1/admin/insert-flight: Insert a new flight (Admin only).
	2.	GET /api/v1/admin/report-flights: Get a list of available flights with capacity (Admin only).

### Client Endpoints

	1.	GET /api/v1/client/query-flights: Query available flights.
	2.	POST /api/v1/client/buy-ticket: Buy a ticket for a flight.
	3.	POST /api/v1/client/check-in: Check-in for a flight.

### Authentication

To access the admin routes, you must log in first and get a JWT token. The token should be included in the Authorization header of the request.

### Example:

Authorization: Bearer your_jwt_token

## License

This project is open-source and available under the MIT License.

