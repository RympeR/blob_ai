from django.db.models import Sum, Avg
from rest_framework import generics, permissions
from blob.utils.customFilters import PromptFilter
from .models import Prompt, Order, Attachment, Tag
from apps.users.models import User
from apps.users.serializers import CustomUserSerializer
from .serializers import PromptSerializer, UserOrderSerializer, OrderSerializer, \
    AttachmentCreateSerializer, PromptCreateSerializer, TagSerializer
from django_filters import rest_framework as filters


class MarketplaceView(generics.ListAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = PromptFilter
    # ordering_fields = ['average_rating', 'creation_date', 'sell_amount']

    def get_queryset(self, queryset=None):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort_by', None)
        if not sort_by:
            return queryset
        if 'sell_amount' in sort_by:
            queryset = queryset.order_by('-sell_amount')
        if 'average_rating' in sort_by:
            queryset = queryset.annotate(average_rating=Avg('ratings__amount_of_stars'))
        if 'creation_date' in sort_by:
            queryset = queryset.order_by('-creation_date')
        return queryset


class TopPromptEngineersView(generics.ListAPIView):
    queryset = User.objects.annotate(total_sells=Sum('prompt_creator__sell_amount')).order_by('-total_sells')[:4]
    serializer_class = CustomUserSerializer


class FavoritePromptsView(generics.ListAPIView):
    queryset = User.favorited_by.through.objects.all()
    serializer_class = PromptSerializer


class PromptSearchFilter(filters.CharFilter):
    search_param = 'name'

    def filter_queryset(self, request, queryset, view):
        search = request.query_params.get(self.search_param, None)
        if search:
            return queryset.filter(name__icontains=search)
        return queryset


class MainPageView(generics.ListAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer


class PromptSearchView(generics.ListAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer
    filter_backends = [PromptSearchFilter]
    search_fields = ['name']


class PromptDetailView(generics.RetrieveAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer


class CreatePromptView(generics.CreateAPIView):
    queryset = Prompt.objects.all()
    serializer_class = PromptCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateOrderView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserOrdersView(generics.ListAPIView):
    serializer_class = UserOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


class CreateAttachmentView(generics.CreateAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class CreateTagView(generics.CreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
