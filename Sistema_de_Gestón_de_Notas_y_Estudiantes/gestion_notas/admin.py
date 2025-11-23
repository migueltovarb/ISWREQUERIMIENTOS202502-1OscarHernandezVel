from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

# Personalización del admin de Usuario
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'rol', 'first_name', 'last_name', 'is_active')
    list_filter = ('rol', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'documento', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'documento', 'telefono', 'foto_perfil')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Adicional', {
            'fields': ('rol', 'documento', 'telefono', 'email', 'first_name', 'last_name')
        }),
    )


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'codigo')


@admin.register(PeriodoAcademico)
class PeriodoAcademicoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    date_hierarchy = 'fecha_inicio'


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('codigo_estudiantil', 'get_nombre_completo', 'programa', 'semestre', 'estado')
    list_filter = ('estado', 'programa', 'semestre')
    search_fields = ('codigo_estudiantil', 'usuario__first_name', 'usuario__last_name', 'usuario__documento')
    date_hierarchy = 'fecha_ingreso'
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'especialidad', 'titulo_academico')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'especialidad')
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'cargo', 'departamento')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'cargo')
    
    def get_nombre_completo(self, obj):
        return obj.usuario.get_full_name()
    get_nombre_completo.short_description = 'Nombre Completo'


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'creditos', 'programa', 'semestre_sugerido')
    list_filter = ('programa', 'creditos', 'semestre_sugerido')
    search_fields = ('codigo', 'nombre')


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'grupo', 'get_profesor', 'periodo', 'get_inscritos')
    list_filter = ('periodo', 'materia__programa')
    search_fields = ('materia__nombre', 'materia__codigo', 'profesor__usuario__last_name')
    
    def get_nombre_completo(self, obj):
        return f"{obj.materia.codigo} - {obj.materia.nombre}"
    get_nombre_completo.short_description = 'Materia'
    
    def get_profesor(self, obj):
        return obj.profesor.usuario.get_full_name()
    get_profesor.short_description = 'Profesor'
    
    def get_inscritos(self, obj):
        return obj.estudiantes_inscritos()
    get_inscritos.short_description = 'Inscritos'


@admin.register(TipoEvaluacion)
class TipoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)


@admin.register(ConfiguracionEvaluacion)
class ConfiguracionEvaluacionAdmin(admin.ModelAdmin):
    list_display = ('curso', 'tipo_evaluacion', 'porcentaje')
    list_filter = ('tipo_evaluacion',)
    search_fields = ('curso__materia__nombre',)


@admin.register(InscripcionCurso)
class InscripcionCursoAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante', 'curso', 'fecha_inscripcion', 'get_promedio', 'get_estado')
    list_filter = ('curso__periodo', 'curso__materia')
    search_fields = ('estudiante__codigo_estudiantil', 'estudiante__usuario__first_name', 
                    'estudiante__usuario__last_name', 'curso__materia__nombre')
    date_hierarchy = 'fecha_inscripcion'
    
    def get_estudiante(self, obj):
        return f"{obj.estudiante.codigo_estudiantil} - {obj.estudiante.usuario.get_full_name()}"
    get_estudiante.short_description = 'Estudiante'
    
    def get_promedio(self, obj):
        promedio = obj.calcular_promedio()
        return f"{promedio:.2f}" if promedio is not None else "Sin notas"
    get_promedio.short_description = 'Promedio'
    
    def get_estado(self, obj):
        return obj.estado_aprobacion()
    get_estado.short_description = 'Estado'


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('get_estudiante', 'get_materia', 'tipo_evaluacion', 'nota', 
                   'get_registrada_por', 'fecha_registro')
    list_filter = ('tipo_evaluacion', 'fecha_registro')
    search_fields = ('inscripcion__estudiante__codigo_estudiantil', 
                    'inscripcion__estudiante__usuario__first_name',
                    'inscripcion__curso__materia__nombre')
    date_hierarchy = 'fecha_registro'
    readonly_fields = ('fecha_registro', 'fecha_modificacion')
    
    def get_estudiante(self, obj):
        return obj.inscripcion.estudiante.usuario.get_full_name()
    get_estudiante.short_description = 'Estudiante'
    
    def get_materia(self, obj):
        return obj.inscripcion.curso.materia.nombre
    get_materia.short_description = 'Materia'
    
    def get_registrada_por(self, obj):
        return obj.registrada_por.get_full_name()
    get_registrada_por.short_description = 'Registrada Por'


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'titulo', 'leida', 'fecha_creacion')
    list_filter = ('tipo', 'leida', 'fecha_creacion')
    search_fields = ('usuario__username', 'titulo', 'mensaje')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('fecha_creacion',)


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'modelo', 'objeto_id', 'fecha', 'ip_address')
    list_filter = ('accion', 'modelo', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha',)
    
    # Solo lectura en el admin
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


# Personalización del sitio de admin
admin.site.site_header = "Sistema de Gestión de Notas UCC"
admin.site.site_title = "Admin UCC"
admin.site.index_title = "Panel de Administración"