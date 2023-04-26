from django.db.models import Sum, Avg
from rest_framework import generics, permissions
from rest_framework.views import APIView

from blob.utils.customFilters import PromptFilter
from blob.utils.default_responses import api_accepted_202, api_not_found_404
from .models import Category, ModelCategory, Prompt, Order, Attachment, PromptLike, Tag
from apps.users.models import User
from apps.users.serializers import CustomUserSerializer
from .serializers import CategoryGetSerializer, ModelCategoryGetSerializer, ModelCategorySerializer, PromptSerializer, TagGetSerializer, UserOrderSerializer, OrderSerializer, \
    AttachmentCreateSerializer, PromptCreateSerializer, PromptLikeCreateSerializer, TagSerializer
from django_filters import rest_framework as filters
from blob.utils.wayforpay.wayforpay import PaymentRequests
import calendar
import time
from googlesearch import search


class MarketplaceView(generics.GenericAPIView):
    queryset = Prompt.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        top_prompts = self.queryset.filter().order_by('-sell_amount')[:4]
        featured_prompts = Prompt.get_prompts_ordered_by_completed_orders()[:8]
        new_prompts = self.queryset.order_by('-creation_date')[:8]
        return api_accepted_202(obj={
            'top_prompts': PromptSerializer(top_prompts, many=True, context={'request': request}).data,
            'featured_prompts': PromptSerializer(featured_prompts, many=True, context={'request': request}).data,
            'new_prompts': PromptSerializer(new_prompts, many=True, context={'request': request}).data
        })


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

    def get_queryset(self, queryset=None):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name', '')
        categories = self.request.query_params.getlist('categories', [])
        tags = self.request.query_params.getlist('tags', [])
        sort_by = self.request.query_params.getlist('sort_by', [])
        model_categories = self.request.query_params.getlist('model_categories', [])
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by categories
        if categories:
            category_ids = [int(cat_id) for cat_id in categories]
            print(category_ids)
            queryset = queryset.filter(categories__pk__in=category_ids)

        # Filter by model_categories
        if model_categories:
            model_category_ids = [int(mc_id) for mc_id in model_categories]
            queryset = queryset.filter(model_category__pk__in=model_category_ids)
        # Filter by tags
        if tags:
            tags_ids = [int(mc_id) for mc_id in tags]
            queryset = queryset.filter(tags__pk__in=tags_ids)

        if not sort_by:
            return queryset
        if 'sell_amount' in sort_by:
            queryset = queryset.order_by('-sell_amount')
        if 'average_rating' in sort_by:
            queryset = queryset.annotate(average_rate=Avg('ratings__amount_of_stars')).order_by('-average_rate')
        if 'creation_date' in sort_by:
            queryset = queryset.order_by('-creation_date')
        return queryset


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


class CreatePromptLikeView(generics.CreateAPIView):
    queryset = PromptLike.objects.all()
    serializer_class = PromptLikeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class DeletePromptLikeView(generics.DestroyAPIView):
    queryset = PromptLike.objects.all()
    serializer_class = PromptLikeCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.queryset.filter(sender=self.request.user, receiver__pk=self.kwargs['pk']).first()

class UpdatePromptLookups(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pk = request.query_params.get('pk')

        prompt = Prompt.objects.filter(pk=pk).first()
        if not prompt:
            return api_not_found_404({'status': 'error', 'message': 'Prompt not found'})
        if request.user != prompt.user:
            prompt.amount_of_lookups += 1
            prompt.save()
        return api_accepted_202({'status': 'ok', 'amount_of_lookups': prompt.amount_of_lookups, 'pk': pk})


class CreateTagView(generics.CreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


class GeneratePaymentWidget(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        wayforpay = PaymentRequests(
            merchant_account='test_merch_n1',
            merchant_key='secret',
            merchant_domain='http://localhost:8000',
            merchant_password='secret'
        )

        ts = calendar.timegm(time.gmtime())
        product_names = data['product_names'] #['value', 'value2']
        product_cost = data['product_cost'] #['1', '2']
        product_count = data['product_count'] # ['1', '1']
        widget_data = {
            'orderReference': ts,
            'orderDate': ts,
            'amount': str(data['amount']), # '3'
            'currency': data['currency'], #UAH
            'productName': product_names,
            'productPrice': product_cost,
            'serviceUrl': 'http://127.0.0.1:8000/finish-order/',
            'returnUrl': 'http://127.0.0.1:8000/finish-order/',
            'productCount': product_count,
            'language': data['language'], #uk
            'straightWidget': True
        }
        widget = wayforpay.generateWidgetJson(widget_data)
        order = Order.objects.filter(pk=data['order_pk']).first()
        order.status = '1'
        order.save()
        if not order:
            return api_not_found_404({'status': 'error', 'message': 'Order not found'})
        if order.buyer != request.user:
            return api_not_found_404({'status': 'error', 'message': 'Order not found'})
        return api_accepted_202({'status': 'ok', 'payment_object': widget, 'order_pk': data['order_pk']})


class FinishOrder(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        order = Order.objects.filter(pk=data['order_pk']).first()
        if not order:
            return api_not_found_404({'status': 'error', 'message': 'Order not found'})
        if order.buyer != request.user:
            return api_not_found_404({'status': 'error', 'message': 'Order not found'})
        order.status = '2'
        order.save()
        return api_accepted_202({'status': 'ok', 'message': 'Order successfully paid'})


class GetCategories(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryGetSerializer


class GetModelCategories(generics.ListAPIView):
    queryset = ModelCategory.objects.all()
    serializer_class = ModelCategoryGetSerializer


class GetTags(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagGetSerializer


class GetInfoForPromptCreation(generics.RetrieveAPIView):
    queryset = ModelCategory.objects.all()
    serializer_class = ModelCategorySerializer


class GetResultPrompt(generics.GenericAPIView):

    def post(self, request):
        data = request.data
        style = data.get('style', '')
        tone = data.get('tone', '')
        result_amount = data.get('result_amount', 5)
        text = data.get('text')
        if not text:
            return api_not_found_404({'status': 'error', 'message': 'Text not found'})
        google_links =[link for link in  search(text, tld="co.in", num=result_amount, stop=result_amount, pause=0)]
        result_prompt = f'''
            {text}
            {f'Style: {style}' if style else ''}
            {f'Tone: {tone}' if tone else ''}
            {f'Include this resources: {" ".join(google_links)}' if google_links else 'No google links were found'}
        '''
        return api_accepted_202({'status': 'ok', 'prompt_text': result_prompt})
