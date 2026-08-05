from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.authentication.api.urls')),
    path('api/v1/notifications/', include('apps.notifications.api.urls')),
    path('api/v1/templates/', include('apps.templates.api.urls')),
    path('api/v1/organizations/', include('apps.organizations.api.urls')),
    path('api/v1/providers/', include('apps.providers.api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
