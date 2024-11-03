from flask import Flask, jsonify, request
from neo4j import GraphDatabase

app = Flask(__name__)

# Neo4j database configuration
NEO4J_URI = "neo4j+s://f9b42879.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "9LUzbLprDtDGaYUp4LY50oonIjfXunaB5LSqxEIexZ0"

# Neo4j driver initialization
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

@app.route('/')
def home():
    return "Welcome to the Car Rental API"


def execute_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters)
        return [record for record in result]

@app.teardown_appcontext
def close_driver(exception):
    if driver:
        driver.close()

# Function to convert a Node to dictionary
def node_to_dict(node):
    return dict(node)

# CRUD for Cars
@app.route('/cars', methods=['POST'])
def create_car():
    data = request.json
    query = """
    CREATE (c:Car {car_id: $car_id, make: $make, model: $model, year: $year, location: $location, status: 'available'})
    RETURN c
    """
    with driver.session() as session:
        result = session.run(query, data)
        car = result.single()
    return jsonify(node_to_dict(car['c'])), 201

@app.route('/cars', methods=['GET'])
def get_cars():
    query = "MATCH (c:Car) RETURN c"
    result = execute_query(query)
    cars = [node_to_dict(record["c"]) for record in result]
    return jsonify(cars)

@app.route('/cars/<int:car_id>', methods=['PUT'])
def update_car(car_id):
    data = request.json
    query = """
    MATCH (c:Car {car_id: $car_id})
    SET c += $data
    RETURN c
    """
    result = execute_query(query, {"car_id": car_id, "data": data})
    car = result[0] if result else None
    if car:
        return jsonify(node_to_dict(car['c']))
    return jsonify({"error": "Car not found"}), 404

@app.route('/cars/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    query = "MATCH (c:Car {car_id: $car_id}) DETACH DELETE c"
    execute_query(query, {"car_id": car_id})
    return jsonify({"message": "Car deleted successfully!"})

# CRUD for Customers
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    query = """
    CREATE (c:Customer {customer_id: $customer_id, name: $name, age: $age, address: $address})
    RETURN c
    """
    with driver.session() as session:
        result = session.run(query, data)
        customer = result.single()
    return jsonify(node_to_dict(customer['c'])), 201

@app.route('/customers', methods=['GET'])
def get_customers():
    query = "MATCH (c:Customer) RETURN c"
    result = execute_query(query)
    customers = [node_to_dict(record["c"]) for record in result]
    return jsonify(customers)

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.json
    query = """
    MATCH (c:Customer {customer_id: $customer_id})
    SET c += $data
    RETURN c
    """
    result = execute_query(query, {"customer_id": customer_id, "data": data})
    customer = result[0] if result else None
    if customer:
        return jsonify(node_to_dict(customer['c']))
    return jsonify({"error": "Customer not found"}), 404

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    query = "MATCH (c:Customer {customer_id: $customer_id}) DETACH DELETE c"
    execute_query(query, {"customer_id": customer_id})
    return jsonify({"message": "Customer deleted successfully!"})

# CRUD for Employees
@app.route('/employees', methods=['POST'])
def create_employee():
    data = request.json
    query = """
    CREATE (e:Employee {employee_id: $employee_id, name: $name, address: $address, branch: $branch})
    RETURN e
    """
    params = data
    result = execute_query(query, params)
    
    # Convert Node to dictionary format
    created_employee = node_to_dict(result[0]['e'])  # Use the node_to_dict function
    return jsonify(created_employee), 201


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    query = "MATCH (e:Employee {employee_id: $employee_id}) RETURN e"
    result = execute_query(query, {"employee_id": employee_id})
    if not result:
        return jsonify({"error": "Employee not found"}), 404

    # Convert Node to dictionary format
    employee_node = result[0]['e']
    employee_data = node_to_dict(employee_node)  # Convert the node to a dictionary
    return jsonify(employee_data)

@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.json
    query = """
    MATCH (e:Employee {employee_id: $employee_id})
    SET e += $data
    RETURN e
    """
    result = execute_query(query, {"employee_id": employee_id, "data": data})
    employee = result[0] if result else None
    if employee:
        return jsonify(node_to_dict(employee['e']))  # Use the node_to_dict function
    return jsonify({"error": "Employee not found"}), 404

@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    query = "MATCH (e:Employee {employee_id: $employee_id}) DETACH DELETE e"
    execute_query(query, {"employee_id": employee_id})
    return jsonify({"message": "Employee deleted successfully!"})

# Order a Car
@app.route('/order-car', methods=['POST'])
def order_car():
    data = request.json
    customer_id, car_id = data["customer_id"], data["car_id"]

    # Check if customer has already booked another car
    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[:HAS_BOOKED]->(c:Car)
    RETURN c
    """
    result = execute_query(query, {"customer_id": customer_id})
    if result:
        return jsonify({"error": "Customer has already booked a car"}), 400

    # Book the car if available
    query = """
    MATCH (cust:Customer {customer_id: $customer_id}), (car:Car {car_id: $car_id, status: 'available'})
    CREATE (cust)-[:HAS_BOOKED]->(car)
    SET car.status = 'booked'
    RETURN car
    """
    result = execute_query(query, {"customer_id": customer_id, "car_id": car_id})
    if not result:
        return jsonify({"error": "Car is not available"}), 400

    return jsonify({"message": "Car booked successfully"}), 200

# Cancel Car Order
@app.route('/cancel-order-car', methods=['POST'])
def cancel_order_car():
    data = request.json
    customer_id, car_id = data["customer_id"], data["car_id"]

    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[r:HAS_BOOKED]->(car:Car {car_id: $car_id})
    DELETE r
    SET car.status = 'available'
    RETURN car
    """
    result = execute_query(query, {"customer_id": customer_id, "car_id": car_id})
    if not result:
        return jsonify({"error": "Booking not found"}), 400

    return jsonify({"message": "Car booking cancelled successfully"}), 200

# Rent a Car
@app.route('/rent-car', methods=['POST'])
def rent_car():
    data = request.json
    customer_id, car_id = data["customer_id"], data["car_id"]

    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[:HAS_BOOKED]->(car:Car {car_id: $car_id})
    REMOVE car.status
    SET car.status = 'rented'
    RETURN car
    """
    result = execute_query(query, {"customer_id": customer_id, "car_id": car_id})
    if not result:
        return jsonify({"error": "Booking not found"}), 400

    return jsonify({"message": "Car rented successfully"}), 200

# Return a Car
@app.route('/return-car', methods=['POST'])
def return_car():
    data = request.json
    customer_id, car_id, condition = data["customer_id"], data["car_id"], data["condition"]

    status = "damaged" if condition == "damaged" else "available"
    query = """
    MATCH (cust:Customer {customer_id: $customer_id})-[r:HAS_BOOKED]->(car:Car {car_id: $car_id})
    DELETE r
    SET car.status = $status
    RETURN car
    """
    result = execute_query(query, {"customer_id": customer_id, "car_id": car_id, "status": status})
    if not result:
        return jsonify({"error": "Rental not found"}), 400

    return jsonify({"message": "Car returned successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
