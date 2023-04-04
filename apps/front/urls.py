from django.urls import path, re_path
from .views import (
    IndexView,
)
urlpatterns = [
    re_path('^(?!api).*$',IndexView.as_view()),
]
