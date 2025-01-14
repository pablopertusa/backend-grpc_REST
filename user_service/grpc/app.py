import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc
import redis
import json
import bcrypt
import os


# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def get_user_key(email):
    return f"users:{email}"


class UserService:  # Change if necessary
    def AuthenticateUser(self, request, context):
        try:
            user_data = redis_client.get(get_user_key(request.email))
        except redis.RedisError as e:
            context.set_details("Redis error")
            context.set_code(grpc.StatusCode.INTERNAL)
            return  # return the appropiate response

        if user_data:
            user = json.loads(user_data)
            if bcrypt.checkpw(request.password.encode(), user["password"].encode()):
                return  # return the appropiate response

        return  # return the appropiate response

    def CheckUserExists(self, request, context):
        try:
            user_data = redis_client.get(get_user_key(request.email))
            exists = user_data is not None
        except redis.RedisError as e:
            context.set_details("Redis error")
            context.set_code(grpc.StatusCode.INTERNAL)
            return  # return the appropiate response

        return  # return the appropiate response

    def ListUsers(self, request, context):
        users = []
        try:
            for key in redis_client.scan_iter(match="users:*"):
                user_data = redis_client.get(key)
                if user_data:
                    user = json.loads(user_data)
                    if "name" in user and "email" in user:
                        users.append(
                            # append the appropiate User element
                        )
        except redis.RedisError as e:
            context.set_details("Redis error")
            context.set_code(grpc.StatusCode.INTERNAL)
            return  # return the appropiate response

        return  # return the appropiate response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:1111")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
