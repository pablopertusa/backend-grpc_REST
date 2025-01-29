import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc
import notification_pb2_grpc
import notification_pb2
import redis
import json
import datetime

# Redis connection
redis_notifications = redis.Redis(host="redis", port=6379, db=2)

# Connect to UserService
user_channel = grpc.insecure_channel("user_service_grpc:9797")
user_stub = user_pb2_grpc.UserServiceStub(user_channel)


class NotificationService(notification_pb2_grpc.NotificationServiceServicer):
    def CreateNotification(self, request, context):
        try:
            receiver_email = request.receiver_email
            sender_email = request.sender_email

            # Check if sender exists
            sender_response = user_stub.CheckUserExists(
                user_pb2.CheckUserExistsRequest(email = sender_email)  # Missing parameters
            )
            if not sender_response.exists:
                return notification_pb2.CreateNotificationResponse(
                    success=False
                )

            # Check if receiver existe
            receiver_response = user_stub.CheckUserExists(
                user_pb2.CheckUserExistsRequest(email = receiver_email) # Missing parameters
            )
            if not receiver_response.exists:
                return notification_pb2.CreateNotificationResponse(
                    success=False
                )
            
            # Ahora vemos si el receiver esta suscrito y si lo esta creamos una notificacion

            user_data = redis_notifications.hgetall(f'subscriptions:{receiver_email}')
            decoded_data = {k.decode(): v.decode() for k, v in user_data.items()}
            has_data = 'subscribed' in decoded_data
            
            if has_data:
                receiver_subscribed = decoded_data['subscribed']
            else:
                return notification_pb2.CreateNotificationResponse(
                    success = False
                )
            if receiver_subscribed:

                notification = {
                    "sender_email": sender_email,
                    "receiver_email": receiver_email,
                    "timestamp": datetime.utcnow().isoformat(),
                    "read": False
                }
                
                # Almacenar la notificación como JSON en la lista
                redis_notifications.lpush(f'notifications:{receiver_email}', json.dumps(notification))

                return notification_pb2.CreateNotificationResponse(
                    success = True
                )
            else:
                return notification_pb2.CreateNotificationResponse(
                    success = False
                )

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return notification_pb2.CreateNotificationResponse(
                    success=False
                ) 

    def SubscribeUser(self, request, context): ...

    def UnsubscribeUser(self, request, context): ...

    def CheckUserSubscribed(self, request, context): ...


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationService(), server)
    server.add_insecure_port("[::]:9898")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
