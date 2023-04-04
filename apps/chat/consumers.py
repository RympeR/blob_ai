import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from apps.blog.models import Attachment
from apps.users.models import User, chat_sub_checker
from apps.users.serializers import (UserShortChatRetrieveSeriliazer,
                                    UserShortSocketRetrieveSeriliazer)
from django.db.models import Q

from .models import Chat, Room, UserMessage
from .serializers import ChatGetSerializer, RoomSocketSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            room = text_data_json['room_id']
            user = text_data_json['user']
            message = text_data_json['text']
            _file = text_data_json['attachments']
            room = Room.objects.get(pk=room)
            user = User.objects.get(pk=user)
            blocked = False
            logging.warning(f"Received json {text_data_json}")
            users_len = 1 + len(room.invited.all())
            if not room.creator.is_staff:
                if users_len == 2:
                    if user == room.creator:
                        blocked = True if user in room.invited.first().blocked_users.all() else False
                    else:
                        blocked = True if user in room.creator.blocked_users.all() else False
                    logging.warning(f"block logic {blocked}")
                if not blocked:
                    chat = Chat.objects.create(
                        room=room,
                        user=user,
                        text=message,
                    )
                    chat.attachment.set(
                        Attachment.objects.filter(pk__in=_file))
                    logging.warning(f"created chat {chat.pk}")
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'attachments': _file,
                            'text': message,
                            'date': chat.date.timestamp(),
                            'id': chat.pk,
                            'user': UserShortChatRetrieveSeriliazer(
                                instance=user).data,
                            'room_id': room.pk,
                        }
                    )

                else:
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'attachments': [],
                            'text': '',
                            'date': 0,
                            'id': -1,
                            'user': 0,
                            'room_id': 0,
                        }
                    )
            else:
                chat = Chat.objects.create(
                    room=room,
                    user=user,
                    text=message,
                )
                chat.attachment.set(
                    Attachment.objects.filter(pk__in=_file)
                )
                logging.warning(f"created chat {chat.pk}")
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'attachments': _file,
                        'text': message,
                        'date': chat.date.timestamp(),
                        'id': chat.pk,
                        'user': UserShortChatRetrieveSeriliazer(
                            instance=user).data,
                        'room_id': room.pk,
                    }
                )
        except Exception as e:
            print(e)
            logging.error(e)

    def chat_message(self, event):
        print('chat_message')
        try:
            _id = event['id']
            message = event['text']
            room = event['room_id']
            user = event['user']
            date = event['date']
            event_attachments = event['attachments']
            attachments_info = []

            if event_attachments:
                attachments_pk = event_attachments
                attachments = Attachment.objects.filter(pk__in=attachments_pk)
                for attachment in attachments:
                    try:
                        if attachment._file and hasattr(attachment._file, 'url'):
                            path_file = attachment._file.url
                            file_url = 'https://hype-fans.com/{path}'.format(
                                path=path_file)
                            attachments_info.append(
                                {
                                    "file_type": attachment.file_type,
                                    "file_url": file_url,
                                }
                            )
                    except Exception as e:
                        print(e)
        except Exception as e:
            user = 0
            logging.error(e)

        self.send(text_data=json.dumps({
            "room_id": room,
            "user": user,
            "text": message,
            "date": date,
            "id": _id,
            "attachments": attachments_info
        }))


class ReadedConsumer(WebsocketConsumer):
    def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'readed_chat_{self.room_name}'
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
        except Exception as e:
            print(e)
            logging.error(e)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            user = text_data_json['user']
            message = text_data_json['id']
            if message == 0:
                readed_chat = UserMessage.objects.filter(
                    user__pk=user,
                    message__room__pk=int(self.room_name),
                    readed=False
                )
            else:
                readed_chat = UserMessage.objects.filter(
                    message__pk=message,
                    user__pk=user,
                    readed=False
                )
            logging.warning(f'Readed qs {readed_chat}')
            readed_chat.update(readed=True)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': message,
                    'user': user,
                }
            )
        except Exception as e:
            logging.error(e)

    def chat_message(self, event):
        message = event['id']
        user = event['user']

        self.send(text_data=json.dumps({
            "user": user,
            'id': message,
        }))
