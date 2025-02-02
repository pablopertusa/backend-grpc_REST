from flask import Flask, request, jsonify
import redis
import json

app = Flask(__name__)

# Redis connection
redis_notifications = redis.Redis(host="redis", port=6379, db=2)

@app.route("/list_notifications", methods=["GET"])
def list_conversations():

    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"success": False, "message": "User email is required"}), 400

    # Fetch notifications for the user
    notifications = redis_notifications.lrange(f"notifications:{user_email}", 0, -1)
    if not notifications:
        return jsonify({"success": True, "notifications": []}), 200

    # Decode Redis binary data
    notifications_decode = [json.loads(notification) for notification in notifications]

    return jsonify({"success": True, "notifications": notifications_decode}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8282, debug=True)
