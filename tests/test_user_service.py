import requests
import grpc
import os
import subprocess

# Constants
HTTP_USER_SERVICE = "http://localhost:8080"
GRPC_USER_SERVER = "localhost:9797"


# Test user service connections
def test_create_protobuf_user_service():
    command = [
        "python",
        "-m",
        "grpc_tools.protoc",
        "--proto_path=proto_definitions/",
        "--python_out=./tests",
        "--grpc_python_out=./tests",
        "proto_definitions/user.proto",
    ]
    subprocess.run(command)

    file_exists = os.path.exists("tests/user_pb2.py") and os.path.exists("tests/user_pb2_grpc.py")
    assert file_exists


def test_connection_user_service_http():
    try:
        response = requests.get(HTTP_USER_SERVICE)
        assert True  # If an error has not been raised, port is working
    except Exception as e:
        raise e


def test_connection_user_service_grpc():
    try:
        with grpc.insecure_channel(GRPC_USER_SERVER) as channel:
            grpc.channel_ready_future(channel).result(timeout=3)
    except Exception as e:
        raise e


def test_create_user():
    users = [
        {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "password123",
        },
        {
            "name": "Sender",
            "email": "sender@example.com",
            "password": "password123",
        },
        {
            "name": "Receiver",
            "email": "receiver@example.com",
            "password": "password123",
        },
    ]
    for user in users:
        payload = user
        response = requests.post(f"{HTTP_USER_SERVICE}/users", json=payload)
        assert response.status_code == 201 or response.status_code == 300


def test_list_users():
    try:
        import user_pb2
        import user_pb2_grpc

        # Set up the channel for the gRPC service
        with grpc.insecure_channel(GRPC_USER_SERVER) as channel:
            user_stub = user_pb2_grpc.UserServiceStub(channel)
            list_response = user_stub.ListUsers(
                user_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
            )
            # Assert that the response contains a list of users
            assert len(list_response.users) > 0  # At least one user should be returned
            assert "alice@example.com" in [
                user.email for user in list_response.users
            ]  # Assuming Alice exists from the previous test

    except Exception as e:
        raise e
    

def test_checkUser():
    try:
        import user_pb2
        import user_pb2_grpc

        with grpc.insecure_channel(GRPC_USER_SERVER) as channel:
            user_stub = user_pb2_grpc.UserServiceStub(channel)
            check_response = user_stub.CheckUserExists(
                user_pb2.CheckUserExistsRequest(
                    email = 'alice@example.com'
                )
            )
            print(check_response.exists)
            assert check_response.exists
    except Exception as e:
        raise e
    


def test_checkUser_not_valid():
    try:
        import user_pb2
        import user_pb2_grpc

        with grpc.insecure_channel(GRPC_USER_SERVER) as channel:
            user_stub = user_pb2_grpc.UserServiceStub(channel)
            check_response = user_stub.CheckUserExists(
                user_pb2.CheckUserExistsRequest(
                    email = 'aaaaaaaaaaaaaa@example.com'
                )
            )
            assert not check_response.exists
    except Exception as e:
        raise e

test_create_protobuf_user_service()    
test_connection_user_service_grpc()
test_connection_user_service_http()
test_create_user()
test_list_users()
test_checkUser()
test_checkUser_not_valid()