from flask import Flask, request, jsonify
import redis

app = Flask(__name__)

# Redis connection
redis_messages = redis.Redis(host="redis", port=6379, db=1)


@app.route("/list_converations", methods=["GET"])
def list_conversations():
    """
    Lists all conversations for a given user email.
    """
    user_email = request.args.get("email")
    if not user_email:
        return jsonify({"success": False, "message": "User email is required"}), 400

    # Fetch conversations for the user
    convo_participants = redis_messages.smembers(f"user:{user_email}:conversations")
    if not convo_participants:
        return jsonify({"success": True, "conversations": []}), 200

    # Decode Redis binary data
    conversations = [participant.decode("utf-8") for participant in convo_participants]

    return jsonify({"success": True, "conversations": conversations}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8181, debug=True)
