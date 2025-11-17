from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cvs import views as cv_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', cv_views.home, name='home'),
    path('', include('cvs.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
