"""
URLs principales del proyecto Sistema de Gestión de Notas y Estudiantes
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # URLs de la aplicación principal
    path('', include('gestion_notas.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Sistema de Gestión de Notas"
admin.site.site_title = "Administración de Notas"
admin.site.index_title = "Panel de Administración"