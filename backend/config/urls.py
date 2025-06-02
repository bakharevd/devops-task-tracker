from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

admin.site.site_url = '/tasks'

urlpatterns = ([
                   path('admin/', admin.site.urls),
                   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                   path('api/users/', include('apps.users.urls')),
                   path('api/tasks/', include('apps.tasks.urls')),
               ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
