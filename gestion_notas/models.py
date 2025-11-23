from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Sum

class Usuario(AbstractUser):
    """Usuario base con roles específicos"""
    ROLES = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('administrador', 'Administrador'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_rol_display()}"


class Programa(models.Model):
    """Programa académico (carrera)"""
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'
    
    def __str__(self):
        return self.nombre


class PeriodoAcademico(models.Model):
    """Periodo académico (semestre)"""
    nombre = models.CharField(max_length=50)  # Ej: "2025-1"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    """Perfil de estudiante"""
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('graduado', 'Graduado'),
        ('retirado', 'Retirado'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_estudiante')
    programa = models.ForeignKey(Programa, on_delete=models.PROTECT)
    semestre = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    codigo_estudiantil = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    fecha_ingreso = models.DateField()
    
    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.codigo_estudiantil}"
    
    def obtener_promedio_periodo(self, periodo):
        """Calcula el promedio del estudiante en un periodo específico"""
        inscripciones = self.inscripciones.filter(curso__periodo=periodo)
        promedios = [insc.calcular_promedio() for insc in inscripciones if insc.calcular_promedio() is not None]
        return sum(promedios) / len(promedios) if promedios else 0.0


class Profesor(models.Model):
    """Perfil de profesor"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_profesor')
    especialidad = models.CharField(max_length=200)
    titulo_academico = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
    
    def __str__(self):
        return f"Prof. {self.usuario.get_full_name()}"


class Administrador(models.Model):
    """Perfil de administrador"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_administrador')
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
    
    def __str__(self):
        return f"Admin. {self.usuario.get_full_name()}"


class Materia(models.Model):
    """Materia o asignatura"""
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=20, unique=True)
    creditos = models.IntegerField(validators=[MinValueValidator(1)])
    programa = models.ForeignKey(Programa, on_delete=models.PROTECT)
    semestre_sugerido = models.IntegerField(validators=[MinValueValidator(1)])
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Curso(models.Model):
    """Curso específico (una materia en un periodo con un profesor)"""
    materia = models.ForeignKey(Materia, on_delete=models.PROTECT)
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.PROTECT)
    profesor = models.ForeignKey(Profesor, on_delete=models.PROTECT, related_name='cursos')
    grupo = models.CharField(max_length=10)  # Ej: "A", "B", "01"
    horario = models.TextField(blank=True)
    aula = models.CharField(max_length=50, blank=True)
    cupo_maximo = models.IntegerField(default=30)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        unique_together = ['materia', 'periodo', 'grupo']
    
    def __str__(self):
        return f"{self.materia.codigo} - Grupo {self.grupo} - {self.periodo.nombre}"
    
    def estudiantes_inscritos(self):
        return self.inscripciones.count()


class TipoEvaluacion(models.Model):
    """Tipos de evaluación (parcial, taller, participación, etc.)"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Evaluación'
        verbose_name_plural = 'Tipos de Evaluación'
    
    def __str__(self):
        return self.nombre


class ConfiguracionEvaluacion(models.Model):
    """Configuración de porcentajes por tipo de evaluación para un curso"""
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='configuracion_evaluaciones')
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.PROTECT)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, 
                                     validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        verbose_name = 'Configuración de Evaluación'
        verbose_name_plural = 'Configuraciones de Evaluación'
        unique_together = ['curso', 'tipo_evaluacion']
    
    def __str__(self):
        return f"{self.curso} - {self.tipo_evaluacion.nombre}: {self.porcentaje}%"


class InscripcionCurso(models.Model):
    """Inscripción de un estudiante en un curso"""
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Inscripción a Curso'
        verbose_name_plural = 'Inscripciones a Cursos'
        unique_together = ['estudiante', 'curso']
    
    def __str__(self):
        return f"{self.estudiante} - {self.curso}"
    
    def calcular_promedio(self):
        """Calcula el promedio ponderado del estudiante en este curso"""
        calificaciones = self.calificaciones.all()
        if not calificaciones:
            return None
        
        total_ponderado = 0
        total_porcentaje = 0
        
        for calificacion in calificaciones:
            config = ConfiguracionEvaluacion.objects.filter(
                curso=self.curso,
                tipo_evaluacion=calificacion.tipo_evaluacion
            ).first()
            
            if config:
                peso = float(config.porcentaje) / 100
                total_ponderado += float(calificacion.nota) * peso
                total_porcentaje += peso
        
        return round(total_ponderado, 2) if total_porcentaje > 0 else 0.0
    
    def estado_aprobacion(self):
        """Determina si el estudiante aprobó o reprobó"""
        promedio = self.calcular_promedio()
        if promedio is None:
            return "Pendiente"
        return "Aprobado" if promedio >= 3.0 else "Reprobado"


class Calificacion(models.Model):
    """Calificación individual de un estudiante"""
    inscripcion = models.ForeignKey(InscripcionCurso, on_delete=models.CASCADE, related_name='calificaciones')
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.PROTECT)
    nota = models.DecimalField(max_digits=3, decimal_places=2, 
                               validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    registrada_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ['inscripcion', 'tipo_evaluacion']
    
    def __str__(self):
        return f"{self.inscripcion.estudiante} - {self.tipo_evaluacion.nombre}: {self.nota}"


class Notificacion(models.Model):
    """Notificaciones para usuarios"""
    TIPOS = [
        ('nueva_nota', 'Nueva Nota'),
        ('modificacion_nota', 'Modificación de Nota'),
        ('inscripcion', 'Inscripción'),
        ('general', 'General'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"


class LogActividad(models.Model):
    """Registro de actividades para auditoría"""
    ACCIONES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('consultar', 'Consultar'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modelo = models.CharField(max_length=50)
    objeto_id = models.IntegerField()
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.modelo} - {self.fecha}"