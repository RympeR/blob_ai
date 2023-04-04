from rest_framework import generics, permissions, views
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.shop.models import Prompt
from blob.utils.default_responses import api_created_201, api_block_by_policy_451, api_bad_request_400, \
    api_accepted_202, api_not_found_404
from .models import User, Subscription, Like
from .serializers import CustomUserSerializer, UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, \
    UserFavouritesSerializer, UserPartialSerializer, UserSettingsSerializer, \
    UserGetProfileSerializer, SubscriptionCreateSerializer, LikeCreateSerializer


class ProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserRegisterView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        try:
            username = request.data['username']
            user, created = User.objects.get_or_create(
                email=request.data['email'].lower(),
                username=username
            )
            if not created:
                assert created, "Already exists"
            else:
                user.set_password(request.data['password'])
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
            return api_created_201({"auth_token": token.key})
        except Exception:
            return api_block_by_policy_451({"info": "already exists"})


class UserLoginView(views.APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key}, status=status.HTTP_200_OK)


class MarkFavourite(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserFavouritesSerializer
    queryset = User.objects.all()

    def put(self, request):
        data = request.data
        user = request.user
        if self.serializer_class(data=data).is_valid():
            prompt = Prompt.objects.get(pk=data['prompt_id'])
            if data.get('favorite'):
                prompt.favorite_prompts.add(user)
                return Response(data)
            prompt.favorite_prompts.remove(user)
            return Response(data)


class LogoutView(APIView):

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class UsernameProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'


class UserPartialUpdateAPI(generics.GenericAPIView, UpdateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserPartialSerializer


class SettingsView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSettingsSerializer

    def get_object(self):
        return self.request.user


class GoogleRegisterView(APIView):

    def post(self, request):
        data = request.data
        if not data.get('Ca'):
            return api_bad_request_400({'status': 'unknown'})

        g_user_id = data['googleId']
        g_email = data['profileObj']['email']
        g_name = data['profileObj']['name']
        if g_name and len(g_name.split(" ")) == 1:
            username = g_name
        else:
            username = ''.join(g_name.split(" ")).lower()
        if User.objects.filter(email=g_email).first():
            return api_bad_request_400({'status': 'already exists email'})
        user = User.create_user(
            g_email,
            g_email,
            username=username,
            google_id=g_user_id,
            register_provider='google'
        )
        token, _ = Token.objects.get_or_create(user=user)
        return api_created_201({'token': token.key})


class GoogleLoginView(APIView):

    def post(self, request):
        data = request.data
        if not data.get('Ca'):
            return api_bad_request_400({'status': 'unknown'})

        g_email = data['profileObj']['email']
        user = User.objects.filter(email=g_email).first()
        if not user or user.register_provider != 'google':
            return api_bad_request_400({'status': 'already exists email'})
        token, _ = Token.objects.get_or_create(user=user)
        return api_accepted_202({'token': token.key})


class CreateSubscriptionsView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateLikeView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeleteSubscriptionsView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Subscription.objects.get(
            sender=self.request.user,
            receiver=User.objects.get(username=self.kwargs['username'])
        )


class DeleteLikeView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = LikeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Like.objects.get(
            sender=self.request.user,
            receiver=User.objects.get(username=self.kwargs['username'])
        )


class GetMySubscriptionsView(generics.ListAPIView):
    serializer_class = UserGetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscriptions__sender=self.request.user)


class GetMySubscribersView(generics.ListAPIView):
    serializer_class = UserGetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(subscriptions__receiver=self.request.user)


class UpdateUserLookups(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.query_params.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            return api_not_found_404({'status': 'error', 'message': 'User not found'})
        if request.user != user:
            user.amount_of_lookups += 1
            user.save()
        return api_accepted_202({'status': 'ok', 'amount_of_lookups': user.amount_of_lookups, 'username': username})
