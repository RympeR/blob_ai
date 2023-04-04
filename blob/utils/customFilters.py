from django_filters import rest_framework as filters
from apps.shop.models import Prompt
from apps.users.models import User

class PromptFilter(filters.FilterSet):
    model = filters.CharFilter(field_name='model_category__name', lookup_expr='icontains')
    category = filters.CharFilter(field_name='categories__name', lookup_expr='icontains')

    class Meta:
        model = Prompt
        fields = ['model', 'category']

class UserFilter(filters.FilterSet):
    username = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = User
        fields = (
            'username',
        )


class PromptNameFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Prompt
        fields = (
            'name',
        )
