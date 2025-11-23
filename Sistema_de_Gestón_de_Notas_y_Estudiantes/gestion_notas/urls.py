from django.urls import include, path
from gestion_notas import admin
from . import views

urlpatterns = [

    # Autenticación
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Estudiante
    path('estudiante/notas/', views.mis_notas, name='mis_notas'),
    path('estudiante/materia/<int:inscripcion_id>/', views.detalle_materia, name='detalle_materia'),
    path('estudiante/perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path('estudiante/boletin/<int:periodo_id>/', views.descargar_boletin, name='descargar_boletin'),
    path('estudiante/historial/exportar/', views.exportar_historial_notas, name='exportar_historial_notas'),
    
    # Profesor
    path('profesor/cursos/', views.mis_cursos, name='mis_cursos'),
    path('profesor/curso/<int:curso_id>/estudiantes/', views.estudiantes_curso, name='estudiantes_curso'),
    path('profesor/calificacion/<int:inscripcion_id>/', views.registrar_calificacion, name='registrar_calificacion'),
    path('profesor/calificacion/<int:calificacion_id>/eliminar/', views.eliminar_calificacion, name='eliminar_calificacion'),
    
    # Administrador
    path('administrador/cursos/', views.gestion_cursos, name='gestion_cursos'),
    path('administrador/reportes/', views.generar_reporte, name='generar_reporte'),
    path('administrador/estadisticas/', views.estadisticas_dashboard, name='estadisticas_dashboard'),
    
    # Notificaciones
    path('notificaciones/', views.todas_notificaciones, name='todas_notificaciones'),
    path('notificaciones/<int:notificacion_id>/leer/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    
    # API/AJAX endpoints (para modales y vistas emergentes)
    path('api/calificaciones/<int:inscripcion_id>/', views.obtener_calificaciones_estudiante, name='api_calificaciones'),
    path('api/validar-nota/', views.validar_nota, name='validar_nota'),
    path('api/buscar/', views.busqueda_global, name='busqueda_global'),
]

# En gestion_notas/urls.py
path('estudiante/notas/', views.mis_notas, name='mis_notas'),
path('estudiante/boletin/<int:periodo_id>/', views.descargar_boletin, name='descargar_boletin'),
path('api/calificaciones/<int:inscripcion_id>/', views.obtener_calificaciones_estudiante, name='api_calificaciones'),