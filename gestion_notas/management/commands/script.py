# management/commands/poblar_datos.py
# Guardar en: gestion_notas/management/commands/poblar_datos.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from gestion_notas.models import (
    Administrador, 
    Calificacion, 
    ConfiguracionEvaluacion, 
    Curso, 
    Estudiante, 
    InscripcionCurso, 
    Materia, 
    Notificacion, 
    PeriodoAcademico, 
    Profesor, 
    Programa, 
    TipoEvaluacion,
    Usuario,
    LogActividad
)
from gestion_notas.models import *
from datetime import date, datetime, timedelta
import random

Usuario = get_user_model()

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de ejemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando población de datos...')
        
        # Limpiar datos existentes (opcional)
        # self.limpiar_datos()
        
        # Crear datos
        self.crear_programas()
        self.crear_periodos()
        self.crear_tipos_evaluacion()
        self.crear_usuarios()
        self.crear_materias()
        self.crear_cursos()
        self.crear_inscripciones()
        self.crear_configuracion_evaluaciones()
        self.crear_calificaciones()
        self.crear_notificaciones()
        
        self.stdout.write(self.style.SUCCESS('¡Datos creados exitosamente!'))

    def limpiar_datos(self):
        self.stdout.write('Limpiando datos existentes...')
        Calificacion.objects.all().delete()
        InscripcionCurso.objects.all().delete()
        ConfiguracionEvaluacion.objects.all().delete()
        Curso.objects.all().delete()
        Materia.objects.all().delete()
        Estudiante.objects.all().delete()
        Profesor.objects.all().delete()
        Administrador.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        TipoEvaluacion.objects.all().delete()
        PeriodoAcademico.objects.all().delete()
        Programa.objects.all().delete()

    def crear_programas(self):
        self.stdout.write('Creando programas...')
        programas = [
            ('Ingeniería de Sistemas', 'ISC'),
            ('Ingeniería de Software', 'ISW'),
            ('Ingeniería Industrial', 'IND'),
            ('Administración de Empresas', 'ADM'),
        ]
        
        for nombre, codigo in programas:
            Programa.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'descripcion': f'Programa de {nombre}'}
            )

    def crear_periodos(self):
        self.stdout.write('Creando periodos académicos...')
        periodos = [
            ('2024-2', date(2024, 8, 1), date(2024, 12, 15), False),
            ('2025-1', date(2025, 1, 15), date(2025, 6, 15), True),
            ('2025-2', date(2025, 8, 1), date(2025, 12, 15), False),
        ]
        
        for nombre, inicio, fin, activo in periodos:
            PeriodoAcademico.objects.get_or_create(
                nombre=nombre,
                defaults={'fecha_inicio': inicio, 'fecha_fin': fin, 'activo': activo}
            )

    def crear_tipos_evaluacion(self):
        self.stdout.write('Creando tipos de evaluación...')
        tipos = [
            ('Parcial', 'Examen parcial escrito'),
            ('Taller', 'Trabajo práctico o taller'),
            ('Participación', 'Participación en clase'),
            ('Proyecto Final', 'Proyecto final del curso'),
            ('Quiz', 'Evaluación corta'),
        ]
        
        for nombre, descripcion in tipos:
            TipoEvaluacion.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )

    def crear_usuarios(self):
        self.stdout.write('Creando usuarios...')
        
        # Crear superusuario si no existe
        if not Usuario.objects.filter(username='admin').exists():
            Usuario.objects.create_superuser(
                username='admin',
                email='admin@ucc.edu.co',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                documento='1000000000',
                rol='administrador'
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado: admin/admin123'))

        # Crear administradores
        admin_user = Usuario.objects.create_user(
            username='mtorres',
            email='mtorres@ucc.edu.co',
            password='password123',
            first_name='Miguel',
            last_name='Torres',
            documento='1000000001',
            rol='administrador'
        )
        Administrador.objects.create(
            usuario=admin_user,
            cargo='Director Académico',
            departamento='Coordinación Académica'
        )

        # Crear profesores
        profesores_data = [
            ('crodriguez', 'Carlos', 'Rodríguez', 'Ingeniería de Software', 'Magister en Ingeniería'),
            ('mgonzalez', 'María', 'González', 'Bases de Datos', 'Doctora en Ciencias de la Computación'),
            ('lmartinez', 'Luis', 'Martínez', 'Arquitectura de Software', 'Magister en Sistemas'),
            ('aramirez', 'Ana', 'Ramírez', 'Redes de Computadores', 'Especialista en Redes'),
        ]
        
        for i, (username, nombre, apellido, especialidad, titulo) in enumerate(profesores_data):
            user = Usuario.objects.create_user(
                username=username,
                email=f'{username}@ucc.edu.co',
                password='password123',
                first_name=nombre,
                last_name=apellido,
                documento=f'100000001{i}',
                rol='profesor'
            )
            Profesor.objects.create(
                usuario=user,
                especialidad=especialidad,
                titulo_academico=titulo
            )

        # Crear estudiantes
        programa_isc = Programa.objects.get(codigo='ISC')
        programa_isw = Programa.objects.get(codigo='ISW')
        
        estudiantes_data = [
            ('jperez', 'Juan', 'Pérez', '2021001', programa_isc, 6),
            ('mlopez', 'María', 'López', '2021002', programa_isc, 6),
            ('cgomez', 'Carlos', 'Gómez', '2021003', programa_isw, 5),
            ('arojas', 'Ana', 'Rojas', '2021004', programa_isw, 5),
            ('pcastro', 'Pedro', 'Castro', '2022001', programa_isc, 4),
            ('lsanchez', 'Laura', 'Sánchez', '2022002', programa_isc, 4),
            ('dmendez', 'Diego', 'Méndez', '2022003', programa_isw, 3),
            ('sgarcia', 'Sara', 'García', '2022004', programa_isw, 3),
        ]
        
        for username, nombre, apellido, codigo, programa, semestre in estudiantes_data:
            user = Usuario.objects.create_user(
                username=username,
                email=f'{username}@ucc.edu.co',
                password='password123',
                first_name=nombre,
                last_name=apellido,
                documento=codigo,
                rol='estudiante'
            )
            Estudiante.objects.create(
                usuario=user,
                codigo_estudiantil=codigo,
                programa=programa,
                semestre=semestre,
                fecha_ingreso=date(2021, 1, 15)
            )

    def crear_materias(self):
        self.stdout.write('Creando materias...')
        programa_isc = Programa.objects.get(codigo='ISC')
        
        materias_data = [
            ('ISW-501', 'Ingeniería de Software', 3, 5),
            ('BDA-402', 'Bases de Datos Avanzadas', 4, 4),
            ('ARC-305', 'Arquitectura de Computadores', 3, 3),
            ('RED-408', 'Redes de Computadores', 4, 4),
            ('PRG-402', 'Programación Avanzada', 4, 4),
            ('ARQ-503', 'Arquitectura de Software', 3, 5),
        ]
        
        for codigo, nombre, creditos, semestre in materias_data:
            Materia.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'creditos': creditos,
                    'programa': programa_isc,
                    'semestre_sugerido': semestre,
                    'descripcion': f'Curso de {nombre}'
                }
            )

    def crear_cursos(self):
        self.stdout.write('Creando cursos...')
        periodo = PeriodoAcademico.objects.get(activo=True)
        
        cursos_data = [
            ('ISW-501', 'crodriguez', 'A', 'Lun-Mie 10:00-12:00', 'Aula 301'),
            ('BDA-402', 'mgonzalez', 'B', 'Mar-Jue 14:00-16:00', 'Aula 205'),
            ('ARC-305', 'lmartinez', 'A', 'Vie 08:00-12:00', 'Aula 401'),
            ('RED-408', 'aramirez', 'C', 'Lun-Vie 16:00-18:00', 'Lab 102'),
            ('PRG-402', 'crodriguez', 'B', 'Mar-Jue 14:00-16:00', 'Lab 205'),
            ('ARQ-503', 'lmartinez', 'A', 'Vie 14:00-18:00', 'Aula 301'),
        ]
        
        for codigo_materia, username_prof, grupo, horario, aula in cursos_data:
            materia = Materia.objects.get(codigo=codigo_materia)
            profesor = Profesor.objects.get(usuario__username=username_prof)
            
            Curso.objects.get_or_create(
                materia=materia,
                periodo=periodo,
                grupo=grupo,
                defaults={
                    'profesor': profesor,
                    'horario': horario,
                    'aula': aula,
                    'cupo_maximo': 35
                }
            )

    def crear_inscripciones(self):
        self.stdout.write('Creando inscripciones...')
        periodo = PeriodoAcademico.objects.get(activo=True)
        cursos = Curso.objects.filter(periodo=periodo)
        estudiantes = Estudiante.objects.all()
        
        # Inscribir cada estudiante en 4-6 cursos aleatorios
        for estudiante in estudiantes:
            cursos_seleccionados = random.sample(list(cursos), random.randint(4, 6))
            for curso in cursos_seleccionados:
                InscripcionCurso.objects.get_or_create(
                    estudiante=estudiante,
                    curso=curso
                )

    def crear_configuracion_evaluaciones(self):
        self.stdout.write('Creando configuración de evaluaciones...')
        periodo = PeriodoAcademico.objects.get(activo=True)
        cursos = Curso.objects.filter(periodo=periodo)
        
        # Configuración estándar: 40% Parcial, 30% Taller, 20% Proyecto, 10% Participación
        config_estandar = [
            ('Parcial', 40),
            ('Taller', 30),
            ('Proyecto Final', 20),
            ('Participación', 10),
        ]
        
        for curso in cursos:
            for tipo_nombre, porcentaje in config_estandar:
                tipo = TipoEvaluacion.objects.get(nombre=tipo_nombre)
                ConfiguracionEvaluacion.objects.get_or_create(
                    curso=curso,
                    tipo_evaluacion=tipo,
                    defaults={'porcentaje': porcentaje}
                )

    def crear_calificaciones(self):
        self.stdout.write('Creando calificaciones...')
        inscripciones = InscripcionCurso.objects.all()
        
        for inscripcion in inscripciones:
            # Obtener configuraciones del curso
            configuraciones = ConfiguracionEvaluacion.objects.filter(curso=inscripcion.curso)
            
            for config in configuraciones:
                # Generar nota aleatoria entre 3.0 y 5.0
                nota = round(random.uniform(3.0, 5.0), 2)
                
                observaciones = [
                    'Excelente trabajo',
                    'Buen desempeño',
                    'Cumple con los objetivos',
                    'Puede mejorar',
                    ''
                ]
                
                Calificacion.objects.get_or_create(
                    inscripcion=inscripcion,
                    tipo_evaluacion=config.tipo_evaluacion,
                    defaults={
                        'nota': nota,
                        'observaciones': random.choice(observaciones),
                        'registrada_por': inscripcion.curso.profesor.usuario
                    }
                )

    def crear_notificaciones(self):
        self.stdout.write('Creando notificaciones...')
        estudiantes = Usuario.objects.filter(rol='estudiante')
        
        mensajes = [
            ('nueva_nota', 'Nueva nota publicada', 'Tu nota del parcial ha sido publicada'),
            ('modificacion_nota', 'Nota modificada', 'Se actualizó tu calificación'),
            ('general', 'Recordatorio', 'Tienes una entrega pendiente'),
            ('inscripcion', 'Inscripción exitosa', 'Te has inscrito correctamente al curso'),
        ]
        
        for estudiante in estudiantes[:5]:  # Solo para algunos estudiantes
            for tipo, titulo, mensaje in random.sample(mensajes, 2):
                Notificacion.objects.create(
                    usuario=estudiante,
                    tipo=tipo,
                    titulo=titulo,
                    mensaje=mensaje,
                    leida=random.choice([True, False])
                )

        self.stdout.write(self.style.SUCCESS('Notificaciones creadas'))