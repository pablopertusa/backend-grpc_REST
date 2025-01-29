import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc
import notification_pb2_grpc
import notification_pb2
import redis
import json

# Redis connection
redis_notifications = redis.Redis(host="redis", port=6379, db=2)

# Connect to UserService
user_channel = grpc.insecure_channel("user_service_grpc:9797")
user_stub = user_pb2_grpc.UserServiceStub(user_channel)


class NotificationService(notification_pb2_grpc.NotificationServiceServicer):
    def CreateNotification(self, request, context):
        pass

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
