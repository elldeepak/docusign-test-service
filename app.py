#!/usr/bin/env python3
"""
Test HTTP service with Basic Authentication & Sample Data
For testing DocuSign Workflow Builder's "Make a Web Request" step
Includes Car database with CRUD operations
"""

from flask import Flask, request, jsonify
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)

# Test credentials
VALID_USERNAME = "docusign_test"
VALID_PASSWORD = "test_password_123"

# In-memory car database (simulates a database)
cars_db = {
    "CAR001": {
        "id": "CAR001",
        "model": "Tesla Model S",
        "name": "Model S",
        "description": "Electric sedan with advanced autopilot features",
        "year": 2024,
        "price": 89990,
        "color": "Pearl White",
        "created_at": "2024-01-15T10:30:00Z"
    },
    "CAR002": {
        "id": "CAR002",
        "model": "BMW i8",
        "name": "i8",
        "description": "Plug-in hybrid sports car with iconic design",
        "year": 2023,
        "price": 156500,
        "color": "Metallic Blue",
        "created_at": "2024-02-20T14:45:00Z"
    },
    "CAR003": {
        "id": "CAR003",
        "model": "Audi e-tron GT",
        "name": "e-tron GT",
        "description": "High-performance electric grand tourer",
        "year": 2024,
        "price": 114000,
        "color": "Dynamite Black",
        "created_at": "2024-03-10T09:15:00Z"
    },
    "CAR004": {
        "id": "CAR004",
        "model": "Porsche 911",
        "name": "911",
        "description": "Iconic sports car with turbocharged engine",
        "year": 2024,
        "price": 120000,
        "color": "Racing Yellow",
        "created_at": "2024-01-25T11:20:00Z"
    },
    "CAR005": {
        "id": "CAR005",
        "model": "Mercedes-Benz EQE",
        "name": "EQE",
        "description": "Luxury electric sedan with cutting-edge technology",
        "year": 2024,
        "price": 104150,
        "color": "Diamond Silver",
        "created_at": "2024-02-05T16:00:00Z"
    }
}

def check_auth(username, password):
    """Check if username and password are valid."""
    return username == VALID_USERNAME and password == VALID_PASSWORD

def authenticate(f):
    """Decorator for routes requiring Basic Auth."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization

        if not auth:
            return jsonify({
                "error": "Missing Authorization header",
                "message": "Please provide Basic Authentication credentials"
            }), 401

        if not check_auth(auth.username, auth.password):
            return jsonify({
                "error": "Invalid credentials",
                "message": f"Authentication failed for username: {auth.username}"
            }), 401

        return f(*args, **kwargs)

    return decorated_function

# ============= PUBLIC ENDPOINTS (No Auth) =============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no auth required)."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DocuSign Workflow Test Service with Car Database"
    }), 200

@app.route('/api/credentials', methods=['GET'])
def get_credentials():
    """Get test credentials (no auth required - informational only)."""
    return jsonify({
        "credentials": {
            "username": VALID_USERNAME,
            "password": VALID_PASSWORD
        },
        "note": "Use these credentials for Basic Auth in DocuSign Workflow Builder",
        "endpoints": {
            "health_check": "GET /health",
            "info": "GET /api/info",
            "cars_all": "GET /api/cars (requires auth)",
            "car_by_model": "GET /api/cars/{model} (requires auth)",
            "create_car": "POST /api/cars (requires auth)",
            "update_car": "PUT /api/cars/{model} (requires auth)",
            "delete_car": "DELETE /api/cars/{model} (requires auth)"
        }
    }), 200

@app.route('/api/info', methods=['GET'])
def get_info():
    """Get API information."""
    return jsonify({
        "service": "DocuSign Workflow Test Service",
        "version": "2.0",
        "description": "HTTP service with Basic Auth for testing Workflow Builder",
        "features": [
            "Basic Authentication",
            "Car database with CRUD operations",
            "Sample data included",
            "JSON request/response"
        ],
        "auth_required": "Most endpoints require Basic Auth (docusign_test / test_password_123)",
        "base_url": request.base_url.rstrip('/'),
        "database": {
            "type": "In-memory",
            "table": "cars",
            "total_records": len(cars_db),
            "fields": ["id", "model", "name", "description", "year", "price", "color", "created_at"]
        }
    }), 200

# ============= CAR ENDPOINTS (With Auth) =============

@app.route('/api/cars', methods=['GET'])
@authenticate
def get_all_cars():
    """Get all cars from database (requires auth)."""
    cars_list = list(cars_db.values())

    return jsonify({
        "status": "success",
        "message": f"Retrieved {len(cars_list)} cars",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "count": len(cars_list),
        "data": cars_list
    }), 200

@app.route('/api/cars/<string:model>', methods=['GET'])
@authenticate
def get_car_by_model(model):
    """Get specific car by model (requires auth)."""
    car_id = model.upper()

    if car_id not in cars_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Car with model ID '{model}' not found",
            "timestamp": datetime.utcnow().isoformat(),
            "authenticated_user": request.authorization.username,
            "available_models": list(cars_db.keys())
        }), 404

    car = cars_db[car_id]
    return jsonify({
        "status": "success",
        "message": "Car retrieved successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": car
    }), 200

@app.route('/api/cars', methods=['POST'])
@authenticate
def create_car():
    """Create a new car (requires auth)."""
    if not request.is_json:
        return jsonify({
            "status": "error",
            "error": "Invalid Content-Type",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()

    # Validate required fields
    required_fields = ['model', 'name', 'description']
    missing_fields = [f for f in required_fields if f not in data or not data[f]]

    if missing_fields:
        return jsonify({
            "status": "error",
            "error": "Missing Fields",
            "message": f"Required fields missing: {', '.join(missing_fields)}",
            "required_fields": required_fields,
            "optional_fields": ["year", "price", "color"]
        }), 400

    # Generate ID from model
    car_id = data['model'].upper().replace(" ", "")

    if car_id in cars_db:
        return jsonify({
            "status": "error",
            "error": "Conflict",
            "message": f"Car with model '{data['model']}' already exists (ID: {car_id})"
        }), 409

    # Create new car record
    new_car = {
        "id": car_id,
        "model": data['model'],
        "name": data['name'],
        "description": data['description'],
        "year": data.get('year', 2024),
        "price": data.get('price', 0),
        "color": data.get('color', 'Unknown'),
        "created_at": datetime.utcnow().isoformat()
    }

    cars_db[car_id] = new_car

    return jsonify({
        "status": "success",
        "message": "Car created successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": new_car
    }), 201

@app.route('/api/cars/<string:model>', methods=['PUT'])
@authenticate
def update_car(model):
    """Update an existing car (requires auth)."""
    car_id = model.upper()

    if car_id not in cars_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Car with model ID '{model}' not found",
            "available_models": list(cars_db.keys())
        }), 404

    if not request.is_json:
        return jsonify({
            "status": "error",
            "error": "Invalid Content-Type",
            "message": "Content-Type must be application/json"
        }), 400

    data = request.get_json()
    car = cars_db[car_id]

    # Update allowed fields
    updatable_fields = ['name', 'description', 'year', 'price', 'color']
    for field in updatable_fields:
        if field in data and data[field] is not None:
            car[field] = data[field]

    # Always update timestamp
    car['updated_at'] = datetime.utcnow().isoformat()

    return jsonify({
        "status": "success",
        "message": "Car updated successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "data": car
    }), 200

@app.route('/api/cars/<string:model>', methods=['DELETE'])
@authenticate
def delete_car(model):
    """Delete a car (requires auth)."""
    car_id = model.upper()

    if car_id not in cars_db:
        return jsonify({
            "status": "error",
            "error": "Not Found",
            "message": f"Car with model ID '{model}' not found",
            "available_models": list(cars_db.keys())
        }), 404

    car = cars_db[car_id]
    del cars_db[car_id]

    return jsonify({
        "status": "success",
        "message": "Car deleted successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "deleted_car": car,
        "remaining_cars": len(cars_db)
    }), 200

# ============= SEARCH & FILTER ENDPOINTS =============

@app.route('/api/cars/search/by-name', methods=['GET'])
@authenticate
def search_cars_by_name():
    """Search cars by name query parameter (requires auth)."""
    name_query = request.args.get('q', '').lower()

    if not name_query:
        return jsonify({
            "status": "error",
            "error": "Missing Parameter",
            "message": "Query parameter 'q' is required",
            "example": "/api/cars/search/by-name?q=model"
        }), 400

    matching_cars = [
        car for car in cars_db.values()
        if name_query in car['name'].lower() or name_query in car['model'].lower()
    ]

    return jsonify({
        "status": "success",
        "message": f"Found {len(matching_cars)} cars matching '{name_query}'",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "query": name_query,
        "count": len(matching_cars),
        "data": matching_cars
    }), 200

@app.route('/api/cars/filter/by-price', methods=['GET'])
@authenticate
def filter_cars_by_price():
    """Filter cars by price range (requires auth)."""
    min_price = request.args.get('min', type=float)
    max_price = request.args.get('max', type=float)

    if min_price is None or max_price is None:
        return jsonify({
            "status": "error",
            "error": "Missing Parameters",
            "message": "Both 'min' and 'max' query parameters are required",
            "example": "/api/cars/filter/by-price?min=50000&max=150000"
        }), 400

    filtered_cars = [
        car for car in cars_db.values()
        if min_price <= car['price'] <= max_price
    ]

    return jsonify({
        "status": "success",
        "message": f"Found {len(filtered_cars)} cars in price range",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "price_range": {
            "min": min_price,
            "max": max_price
        },
        "count": len(filtered_cars),
        "data": filtered_cars
    }), 200

# ============= DATABASE ENDPOINTS =============

@app.route('/api/stats', methods=['GET'])
@authenticate
def get_stats():
    """Get database statistics (requires auth)."""
    if not cars_db:
        avg_price = 0
        total_price = 0
    else:
        prices = [car['price'] for car in cars_db.values()]
        total_price = sum(prices)
        avg_price = total_price / len(prices)

    return jsonify({
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "statistics": {
            "total_cars": len(cars_db),
            "total_value": total_price,
            "average_price": round(avg_price, 2),
            "price_range": {
                "min": min([car['price'] for car in cars_db.values()]) if cars_db else 0,
                "max": max([car['price'] for car in cars_db.values()]) if cars_db else 0
            }
        }
    }), 200

@app.route('/api/reset', methods=['POST'])
@authenticate
def reset_database():
    """Reset database to initial state (requires auth)."""
    global cars_db

    initial_cars = {
        "CAR001": {
            "id": "CAR001",
            "model": "Tesla Model S",
            "name": "Model S",
            "description": "Electric sedan with advanced autopilot features",
            "year": 2024,
            "price": 89990,
            "color": "Pearl White",
            "created_at": "2024-01-15T10:30:00Z"
        },
        "CAR002": {
            "id": "CAR002",
            "model": "BMW i8",
            "name": "i8",
            "description": "Plug-in hybrid sports car with iconic design",
            "year": 2023,
            "price": 156500,
            "color": "Metallic Blue",
            "created_at": "2024-02-20T14:45:00Z"
        },
        "CAR003": {
            "id": "CAR003",
            "model": "Audi e-tron GT",
            "name": "e-tron GT",
            "description": "High-performance electric grand tourer",
            "year": 2024,
            "price": 114000,
            "color": "Dynamite Black",
            "created_at": "2024-03-10T09:15:00Z"
        },
        "CAR004": {
            "id": "CAR004",
            "model": "Porsche 911",
            "name": "911",
            "description": "Iconic sports car with turbocharged engine",
            "year": 2024,
            "price": 120000,
            "color": "Racing Yellow",
            "created_at": "2024-01-25T11:20:00Z"
        },
        "CAR005": {
            "id": "CAR005",
            "model": "Mercedes-Benz EQE",
            "name": "EQE",
            "description": "Luxury electric sedan with cutting-edge technology",
            "year": 2024,
            "price": 104150,
            "color": "Diamond Silver",
            "created_at": "2024-02-05T16:00:00Z"
        }
    }

    cars_db = initial_cars

    return jsonify({
        "status": "success",
        "message": "Database reset to initial state",
        "timestamp": datetime.utcnow().isoformat(),
        "authenticated_user": request.authorization.username,
        "cars_restored": len(cars_db)
    }), 200

# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "path": request.path,
        "method": request.method,
        "available_endpoints": {
            "health": "GET /health",
            "info": "GET /api/info",
            "credentials": "GET /api/credentials",
            "cars_all": "GET /api/cars (auth required)",
            "car_by_id": "GET /api/cars/{model} (auth required)",
            "create_car": "POST /api/cars (auth required)",
            "update_car": "PUT /api/cars/{model} (auth required)",
            "delete_car": "DELETE /api/cars/{model} (auth required)",
            "search_by_name": "GET /api/cars/search/by-name?q=model (auth required)",
            "filter_by_price": "GET /api/cars/filter/by-price?min=X&max=Y (auth required)",
            "stats": "GET /api/stats (auth required)",
            "reset": "POST /api/reset (auth required)"
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))

    print("\n" + "="*70)
    print("TEST HTTP SERVICE - DocuSign Workflow Builder with Car Database")
    print("="*70)
    print("\nTest Credentials:")
    print(f"  Username: {VALID_USERNAME}")
    print(f"  Password: {VALID_PASSWORD}")
    print("\n" + "-"*70)
    print("PUBLIC ENDPOINTS (No Auth Required):")
    print("-"*70)
    print("  GET  /health                          - Service health check")
    print("  GET  /api/info                        - API information")
    print("  GET  /api/credentials                 - Show test credentials")
    print("\n" + "-"*70)
    print("CAR CRUD ENDPOINTS (Auth Required):")
    print("-"*70)
    print("  GET  /api/cars                        - Get all cars")
    print("  GET  /api/cars/{model}                - Get car by model ID")
    print("  POST /api/cars                        - Create new car")
    print("  PUT  /api/cars/{model}                - Update car")
    print("  DELETE /api/cars/{model}              - Delete car")
    print("\n" + "-"*70)
    print("SEARCH & FILTER (Auth Required):")
    print("-"*70)
    print("  GET  /api/cars/search/by-name?q=term  - Search cars by name")
    print("  GET  /api/cars/filter/by-price?min=X&max=Y - Filter by price")
    print("  GET  /api/stats                       - Database statistics")
    print("  POST /api/reset                       - Reset to initial data")
    print("\n" + "-"*70)
    print("Usage in DocuSign Workflow Builder:")
    print("-"*70)
    print("  1. Add 'Make a Web Request' step")
    print("  2. Set URL: https://your-public-url/api/cars")
    print("  3. Set Method: GET or POST")
    print("  4. Authentication Type: Basic Authentication")
    print(f"  5. Username: {VALID_USERNAME}")
    print(f"  6. Password: {VALID_PASSWORD}")
    print("  7. POST Body (for create): ")
    print("     {\"model\": \"Tesla Model X\", \"name\": \"Model X\",")
    print("      \"description\": \"Electric SUV\", \"price\": 99990}")
    print("\n" + "="*70)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("="*70 + "\n")

    app.run(debug=False, host='0.0.0.0', port=port)
