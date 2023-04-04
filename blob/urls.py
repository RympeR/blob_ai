from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from blob import settings

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/user/', include('apps.users.urls')),
    path('api/shop/', include('apps.shop.urls')),
    # path('', include('apps.front.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
