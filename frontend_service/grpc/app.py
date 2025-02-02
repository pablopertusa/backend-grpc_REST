import grpc
from concurrent import futures
import frontend_pb2
import frontend_pb2_grpc


class FrontendService:
    def ReceiveNotification(self, request, context):
        return frontend_pb2.ReceiveNotificationResponse(
            success = True
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    frontend_pb2_grpc.add_FrontendServiceServicer_to_server(FrontendService(), server)
    server.add_insecure_port("[::]:3030")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
