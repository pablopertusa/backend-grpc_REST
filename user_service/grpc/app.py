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

class UserService(user_pb2_grpc.UserServiceServicer):
    def AuthenticateUser(self, request, context):
        email = request.email
        try:
            user_data = redis_client.get(get_user_key(email))
        except redis.RedisError as e:
            context.set_details(f"Redis:{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_pb2.AuthenticateResponse(email = email, success = False)

        if user_data:
            user = json.loads(user_data)
            if bcrypt.checkpw(request.password.encode(), user["password"].encode()):
                return user_pb2.AuthenticateResponse(email = email, success = True)
       
        context.set_details("User not found")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return user_pb2.AuthenticateResponse(email = email, success = False)

    def CheckUserExists(self, request, context):
        email = request.email
        try:
            user_data = redis_client.get(get_user_key(email))
            exists = user_data is not None
            if exists:
                return user_pb2.CheckUserExistsResponse(exists = True)
            else:
                return user_pb2.CheckUserExistsResponse(exists = False)
        
        except redis.RedisError as e:
            context.set_details(f"Redis:{e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_pb2.CheckUserExistsResponse(exists = False)

        

    def ListUsers(self, request , context):
        users = []
        try:
            for key in redis_client.scan_iter(match="users:*"):
                user_data = redis_client.get(key)
                if user_data:
                    user = json.loads(user_data)
                    if "name" in user and "email" in user:
                        users.append(
                            user_pb2.User(
                                name=user["name"],
                                email=user["email"]
                            )
                        ) # Append all users
            return user_pb2.ListUsersResponse(users = users)
        except redis.RedisError as e:
            context.set_details(f"Redis error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return user_pb2.ListUsersResponse(users = [])
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:9797")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
