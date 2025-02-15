import grpc
from concurrent import futures
import notification_pb2_grpc
import notification_pb2
import frontend_pb2
import frontend_pb2_grpc
import redis
import json
from datetime import datetime, timezone


# Redis connection
redis_notifications = redis.Redis(host="redis", port=6379, db=2)
frontend_channel = grpc.insecure_channel("frontend_service_grpc:3030")
frontend_stub = frontend_pb2_grpc.FrontendServiceStub(frontend_channel)


class NotificationService(notification_pb2_grpc.NotificationServiceServicer):
    def CreateNotification(self, request, context): # Este se podría bajar la complejidad quitando elses
        try:
            receiver_email = request.receiver_email
            sender_email = request.sender_email
            
            # Check if receiver is subscribed
            user_data = redis_notifications.hgetall(f'subscriptions:{receiver_email}')
            decoded_data = {k.decode(): v.decode() for k, v in user_data.items()}

            # Check if Redis has dada for the receiver
            if 'subscribed' in decoded_data:
                receiver_subscribed = decoded_data['subscribed']
                if int(receiver_subscribed) == 1:

                    timestamp = datetime.now(timezone.utc).isoformat()
                    notification = {
                        "sender_email": sender_email,
                        "receiver_email": receiver_email,
                        "timestamp": timestamp,
                        "read": False
                    }
                    
                    # Almacenar la notificación como JSON en la lista
                    redis_notifications.lpush(f'notifications:{receiver_email}', json.dumps(notification))
                    
                    frontend_stub.ReceiveNotification(
                        frontend_pb2.Notification(
                            sender_email = sender_email,
                            receiver_email = receiver_email,
                            timestamp = timestamp,
                            read = False
                        )
                    )

                    return notification_pb2.CreateNotificationResponse(
                        success = True
                    )
                else:
                    return notification_pb2.CreateNotificationResponse(
                    success = False
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

    def SubscribeUser(self, request, context):
        try:
            email = request.email
            # Change Redis data for the user
            data = {
                'user_email' : email,
                'subscribed' : "1"
            }
            redis_notifications.hset(f'subscriptions:{email}', mapping=data)
            return notification_pb2.SubscribeUserResponse(
            success=True
            )
        
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return notification_pb2.SubscribeUserResponse(
                    success=False
                ) 

    def UnsubscribeUser(self, request, context):
        try:
            email = request.email
            # Change Redis data for the user
            data = {
                'user_email' : email,
                'subscribed' : "0"
            }
            redis_notifications.hset(f'subscriptions:{email}', mapping=data)
            return notification_pb2.UnsubscribeUserResponse(
            success=True
            )
        
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return notification_pb2.UnsubscribeUserResponse(
                    success=False
                ) 

    def CheckUserSubscribed(self, request, context): # Aquí también se podría mejorar
        try:
            email = request.email
            # Fetch user data
            user_data = redis_notifications.hgetall(f'subscriptions:{email}')
            decoded_data = {k.decode(): v.decode() for k, v in user_data.items()}
            if 'subscribed' in decoded_data:
                # Check user state
                is_subscribed = int(decoded_data['subscribed']) == 1
                return notification_pb2.CheckUserSubscribedResponse(
                    subscribed = is_subscribed
                )
            else:
                return notification_pb2.CheckUserSubscribedResponse(
                    subscribed = False
                )

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return notification_pb2.CheckUserSubscribedResponse(
                    success=False
                ) 


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notification_pb2_grpc.add_NotificationServiceServicer_to_server(NotificationService(), server)
    server.add_insecure_port("[::]:9898")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
