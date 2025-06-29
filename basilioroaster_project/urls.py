from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView # RECOMMENDED: Import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# This is the main URL router for the entire project.
# Its job is to direct traffic to the correct "app".

urlpatterns = [
    # RECOMMENDED: Redirects the root URL ('/') to the login page.
    path('', RedirectView.as_view(url='/users/login/', permanent=False), name='home'),

    # This is your existing admin path.
    path('admin/', admin.site.urls),

    # RECOMMENDED: Include the URLs for your users app (login, logout).
    path('users/', include('users.urls')),
    
    # This is your existing path for the core application.
    path('app/', include('core.urls')), 
]

# This is a helper for development mode to serve uploaded files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)