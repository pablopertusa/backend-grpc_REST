import grpc
from concurrent import futures


class NotificationService:
    def CreateNotification(self, request, context): ...

    def SubscribeUser(self, request, context): ...

    def UnsubscribeUser(self, request, context): ...

    def CheckUserSubscribed(self, request, context): ...


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
