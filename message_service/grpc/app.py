import grpc
from concurrent import futures
import message_pb2
import message_pb2_grpc
import user_pb2
import user_pb2_grpc

from datetime import datetime
import redis
import json


# Redis Connections
redis_messages = redis.Redis(host="redis", port=6379, db=1)

# Initialize message_id_counter if it doesn't exist
if not redis_messages.exists("message_id_counter"):
    redis_messages.set("message_id_counter", 0)

# Connect to UserService
user_channel = grpc.insecure_channel("user_service_grpc:9797")
user_stub = user_pb2_grpc.UserServiceStub(user_channel)


class MessageService(message_pb2_grpc.MessageServiceServicer):
    def SendMessage(self, request, context):
        message = request.message

        # Check if sender exists
        sender_response = user_stub.CheckUserExists(
            user_pb2.CheckUserExistsRequest(email = message.sender_email)  # Missing parameters
        )
        if not sender_response.exists:
            context.set_details("User not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return message_pb2.SendMessageResponse(
                success=False, message="Sender does not exist"
            )

        # Check if receiver existe
        receiver_response = user_stub.CheckUserExists(
            user_pb2.CheckUserExistsRequest(email = message.receiver_email)  # Missing parameters
        )
        if not receiver_response.exists:
            context.set_details("User not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return message_pb2.SendMessageResponse(
                success=False, message="Receiver does not exist"
            )

        # Add message
        message_id = redis_messages.incr("message_id_counter")
        message.timestamp = datetime.utcnow().isoformat()

        redis_messages.set(
            f"message:{message_id}",
            json.dumps(
                {
                    "id": message_id,
                    "sender_email": message.sender_email,
                    "receiver_email": message.receiver_email,
                    "content": message.content,
                    "timestamp": message.timestamp,
                }
            ),
        )

        # Update conversations
        redis_messages.sadd(
            f"user:{message.sender_email}:conversations", message.receiver_email
        )
        redis_messages.sadd(
            f"user:{message.receiver_email}:conversations", message.sender_email
        )

        # Update conversation message list
        convo_key = f"conversation:{message.sender_email}:{message.receiver_email}"
        redis_messages.sadd(convo_key, message_id)

        return message_pb2.SendMessageResponse(
                success=True, message="Message sent"
            )

    def GetMessages(self, request, context):
        user_email = request.user_email
        user_messages = []

        # Get all conversation participants for the user
        convo_participants = redis_messages.smembers(f"user:{user_email}:conversations")

        if not convo_participants:
            return message_pb2.GetMessagesResponse(
                messages = []
            ) # return the appropiate response. Messages should be an empty list.

        # Retrieve messages from all conversations
        for participant in convo_participants:
            convo_key = f"conversation:{user_email}:{participant.decode("utf-8")}"

            message_ids = redis_messages.smembers(convo_key)

            for message_id in message_ids:
                message_data = json.loads(
                    redis_messages.get(f"message:{message_id.decode("utf-8")}")
                )

                user_messages.append(
                       message_pb2.Message(
                            message_id=str(message_data["id"]),
                            sender_email=message_data["sender_email"],
                            receiver_email=message_data["receiver_email"],
                            content=message_data["content"],
                            timestamp=message_data["timestamp"],
                        )
                )

        return message_pb2.GetMessagesResponse(
            messages = user_messages
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    server.add_insecure_port("[::]:9696")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
