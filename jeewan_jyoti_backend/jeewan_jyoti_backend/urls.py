from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('jeewanjyoti_data.urls')),
    path('api/', include('jeewanjyoti_user.urls')),
    path('api/', include('hospital.urls')),
    path('api/', include('chat.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
