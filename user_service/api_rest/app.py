from flask import Flask, request, jsonify
import redis
import json
import bcrypt
import os

app = Flask(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def get_user_key(email):
    return f"users:{email}"


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    if "email" not in data or "password" not in data or "name" not in data:
        return jsonify({"success": False, "message": "Invalid input data"}), 400

    user_mail = data["email"]

    if redis_client.exists(get_user_key(user_mail)):
        return jsonify({"success": False, "message": "User already exists"}), 300

    hashed_password = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    data["password"] = hashed_password.decode()

    try:
        redis_client.set(get_user_key(user_mail), json.dumps(data))
    except redis.RedisError as e:
        return jsonify({"success": False, "message": "Error storing user data"}), 500

    return jsonify({"success": True, "message": "User created successfully"}), 201


@app.route("/users/<user_mail>", methods=["PUT"])
def update_user(user_mail):
    # Check if user exists in Redis
    if not redis_client.exists(get_user_key(user_mail)):
        return jsonify({"success": False, "message": "User not found"}), 200

    updated_data = request.json
    # Validate data
    for key in updated_data:
        if key not in ["password", "name"]:
            return jsonify({"success": False, "message": "Invalid input data"}), 400
    try:
        # Update user data in Redis
        redis_client.set(get_user_key(user_mail), json.dumps(updated_data))
    except redis.RedisError as e:
        return jsonify({"success": False, "message": "Error updating user data"}), 500

    return jsonify({"success": True, "message": "User updated successfully"}), 200


@app.route("/users/<user_mail>", methods=["POST"])
def delete_user(user_mail):
    if not redis_client.exists(get_user_key(user_mail)):
        return jsonify({"success": False, "message": "User not found"}), 404

    try:
        redis_client.delete(get_user_key(user_mail))
    except redis.RedisError as e:
        return jsonify({"success": False, "message": "Error deleting user data"}), 500

    return jsonify({"success": True, "message": "User deleted successfully"}), 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1234)
