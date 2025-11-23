from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Avg
from django.utils import timezone
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

from gestion_notas.models import Calificacion, Curso, Curso, Estudiante, InscripcionCurso, LogActividad, Notificacion, PeriodoAcademico, Profesor, TipoEvaluacion


# ==================== UTILIDADES ====================

def es_estudiante(user):
    return user.is_authenticated and user.rol == 'estudiante'

def es_profesor(user):
    return user.is_authenticated and user.rol == 'profesor'

def es_administrador(user):
    return user.is_authenticated and user.rol == 'administrador'

def registrar_actividad(request, accion, modelo, objeto_id, descripcion):
    """Registra actividad en el log"""
    LogActividad.objects.create(
        usuario=request.user,
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        descripcion=descripcion,
        ip_address=request.META.get('REMOTE_ADDR')
    )


# ==================== AUTENTICACIÓN ====================

def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            registrar_actividad(request, 'consultar', 'Usuario', user.id, 'Inicio de sesión')
            return redirect('dashboard')
        else:
            messages.error(request, 'Credenciales incorrectas')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    """Vista de logout"""
    registrar_actividad(request, 'consultar', 'Usuario', request.user.id, 'Cierre de sesión')
    logout(request)
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    """Dashboard principal según rol del usuario"""
    user = request.user
    
    # Obtener notificaciones no leídas
    notificaciones = user.notificaciones.filter(leida=False)[:5]
    
    context = {
        'notificaciones': notificaciones,
        'notificaciones_count': notificaciones.count(),
    }
    
    if user.rol == 'estudiante':
        estudiante = user.perfil_estudiante
        periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
        
        # Inscripciones del periodo actual
        inscripciones = estudiante.inscripciones.filter(curso__periodo=periodo_actual)
        
        # Calcular promedio general
        promedios = [insc.calcular_promedio() for insc in inscripciones if insc.calcular_promedio() is not None]
        promedio_general = sum(promedios) / len(promedios) if promedios else 0.0
        
        context.update({
            'estudiante': estudiante,
            'inscripciones': inscripciones,
            'promedio_general': round(promedio_general, 2),
            'periodo_actual': periodo_actual,
        })
        return render(request, 'estudiante/dashboard.html', context)
    
    elif user.rol == 'profesor':
        profesor = user.perfil_profesor
        periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
        
        # Cursos del profesor en el periodo actual
        cursos = profesor.cursos.filter(periodo=periodo_actual)
        
        context.update({
            'profesor': profesor,
            'cursos': cursos,
            'periodo_actual': periodo_actual,
        })
        return render(request, 'profesor/dashboard.html', context)
    
    elif user.rol == 'administrador':
        administrador = user.perfil_administrador
        periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
        
        # Estadísticas generales
        total_estudiantes = Estudiante.objects.filter(estado='activo').count()
        total_profesores = Profesor.objects.count()
        total_cursos = Curso.objects.filter(periodo=periodo_actual).count()
        
        context.update({
            'administrador': administrador,
            'total_estudiantes': total_estudiantes,
            'total_profesores': total_profesores,
            'total_cursos': total_cursos,
            'periodo_actual': periodo_actual,
        })
        return render(request, 'administrador/dashboard.html', context)
    
    return redirect('login')


# ==================== ESTUDIANTE ====================

@login_required
@user_passes_test(es_estudiante)
def mis_notas(request):
    """Vista de notas del estudiante"""
    estudiante = request.user.perfil_estudiante
    periodo_id = request.GET.get('periodo')
    
    if periodo_id:
        inscripciones = estudiante.inscripciones.filter(curso__periodo_id=periodo_id)
        periodo_actual = PeriodoAcademico.objects.get(id=periodo_id)
    else:
        periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
        inscripciones = estudiante.inscripciones.filter(curso__periodo=periodo_actual)
    
    periodos = PeriodoAcademico.objects.all()
    
    # Calcular promedio general del periodo
    promedios = [insc.calcular_promedio() for insc in inscripciones if insc.calcular_promedio() is not None]
    promedio_general = sum(promedios) / len(promedios) if promedios else 0.0
    
    context = {
        'inscripciones': inscripciones,
        'periodos': periodos,
        'periodo_actual': periodo_actual,
        'promedio_general': round(promedio_general, 2),
    }
    
    return render(request, 'estudiante/mis_notas.html', context)

@login_required
@user_passes_test(es_estudiante)
def detalle_materia(request, inscripcion_id):
    """Detalle de una materia específica"""
    inscripcion = get_object_or_404(InscripcionCurso, id=inscripcion_id, estudiante=request.user.perfil_estudiante)
    calificaciones = inscripcion.calificaciones.all()
    
    context = {
        'inscripcion': inscripcion,
        'calificaciones': calificaciones,
        'promedio': inscripcion.calcular_promedio(),
        'estado': inscripcion.estado_aprobacion(),
    }
    
    return render(request, 'estudiante/detalle_materia.html', context)

@login_required
@user_passes_test(es_estudiante)
def actualizar_perfil(request):
    """Actualizar datos personales del estudiante"""
    if request.method == 'POST':
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        
        request.user.email = email
        request.user.telefono = telefono
        request.user.save()
        
        registrar_actividad(request, 'editar', 'Usuario', request.user.id, 'Actualización de perfil')
        messages.success(request, 'Perfil actualizado correctamente')
        return redirect('dashboard')
    
    return render(request, 'estudiante/actualizar_perfil.html')

@login_required
@user_passes_test(es_estudiante)
def descargar_boletin(request, periodo_id):
    """Descargar boletín de notas en PDF"""
    estudiante = request.user.perfil_estudiante
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    inscripciones = estudiante.inscripciones.filter(curso__periodo=periodo)
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    titulo = Paragraph(f"<b>Boletín de Notas - {periodo.nombre}</b>", styles['Title'])
    elements.append(titulo)
    elements.append(Spacer(1, 12))
    
    # Información del estudiante
    info_estudiante = Paragraph(f"""
        <b>Estudiante:</b> {estudiante.usuario.get_full_name()}<br/>
        <b>Código:</b> {estudiante.codigo_estudiantil}<br/>
        <b>Programa:</b> {estudiante.programa.nombre}<br/>
        <b>Semestre:</b> {estudiante.semestre}
    """, styles['Normal'])
    elements.append(info_estudiante)
    elements.append(Spacer(1, 20))
    
    # Tabla de notas
    data = [['Materia', 'Profesor', 'Promedio', 'Estado']]
    
    for insc in inscripciones:
        promedio = insc.calcular_promedio() or 0.0
        estado = insc.estado_aprobacion()
        data.append([
            insc.curso.materia.nombre,
            insc.curso.profesor.usuario.get_full_name(),
            f"{promedio:.2f}",
            estado
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    
    # Promedio general
    promedios = [insc.calcular_promedio() for insc in inscripciones if insc.calcular_promedio() is not None]
    promedio_general = sum(promedios) / len(promedios) if promedios else 0.0
    
    elements.append(Spacer(1, 20))
    promedio_text = Paragraph(f"<b>Promedio General: {promedio_general:.2f}</b>", styles['Heading2'])
    elements.append(promedio_text)
    
    doc.build(elements)
    buffer.seek(0)
    
    registrar_actividad(request, 'consultar', 'Boletin', periodo_id, f'Descarga de boletín - {periodo.nombre}')
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boletin_{periodo.nombre}_{estudiante.codigo_estudiantil}.pdf"'
    return response


# ==================== PROFESOR ====================

@login_required
@user_passes_test(es_profesor)
def mis_cursos(request):
    """Lista de cursos del profesor"""
    profesor = request.user.perfil_profesor
    periodo_actual = PeriodoAcademico.objects.filter(activo=True).first()
    cursos = profesor.cursos.filter(periodo=periodo_actual)
    
    context = {
        'cursos': cursos,
        'periodo_actual': periodo_actual,
    }
    
    return render(request, 'profesor/mis_cursos.html', context)

@login_required
@user_passes_test(es_profesor)
def estudiantes_curso(request, curso_id):
    """Lista de estudiantes de un curso"""
    curso = get_object_or_404(Curso, id=curso_id, profesor=request.user.perfil_profesor)
    inscripciones = curso.inscripciones.all().order_by('estudiante__usuario__last_name')
    
    context = {
        'curso': curso,
        'inscripciones': inscripciones,
    }
    
    return render(request, 'profesor/estudiantes_curso.html', context)

@login_required
@user_passes_test(es_profesor)
def registrar_calificacion(request, inscripcion_id):
    """Registrar o editar calificación"""
    inscripcion = get_object_or_404(InscripcionCurso, id=inscripcion_id)
    
    # Verificar que el profesor pertenece al curso
    if inscripcion.curso.profesor != request.user.perfil_profesor:
        messages.error(request, 'No tiene permiso para calificar este curso')
        return redirect('mis_cursos')
    
    if request.method == 'POST':
        tipo_evaluacion_id = request.POST.get('tipo_evaluacion')
        nota = request.POST.get('nota')
        observaciones = request.POST.get('observaciones', '')
        
        calificacion, created = Calificacion.objects.update_or_create(
            inscripcion=inscripcion,
            tipo_evaluacion_id=tipo_evaluacion_id,
            defaults={
                'nota': nota,
                'observaciones': observaciones,
                'registrada_por': request.user
            }
        )
        
        # Crear notificación
        Notificacion.objects.create(
            usuario=inscripcion.estudiante.usuario,
            tipo='nueva_nota' if created else 'modificacion_nota',
            titulo=f"{'Nueva nota' if created else 'Nota modificada'} en {inscripcion.curso.materia.nombre}",
            mensaje=f"Se ha {'registrado' if created else 'modificado'} tu nota de {calificacion.tipo_evaluacion.nombre}: {nota}"
        )
        
        accion = 'crear' if created else 'editar'
        registrar_actividad(request, accion, 'Calificacion', calificacion.id, 
                          f"{accion.capitalize()} calificación para {inscripcion.estudiante}")
        
        messages.success(request, 'Calificación registrada correctamente')
        return redirect('estudiantes_curso', curso_id=inscripcion.curso.id)
    
    tipos_evaluacion = TipoEvaluacion.objects.all()
    calificaciones_existentes = inscripcion.calificaciones.all()
    
    context = {
        'inscripcion': inscripcion,
        'tipos_evaluacion': tipos_evaluacion,
        'calificaciones_existentes': calificaciones_existentes,
    }
    
    return render(request, 'profesor/registrar_calificacion.html', context)


# ==================== ADMINISTRADOR ====================

@login_required
@user_passes_test(es_administrador)
def gestion_cursos(request):
    """Gestión de cursos"""
    cursos = Curso.objects.all().order_by('-periodo__fecha_inicio')
    
    context = {
        'cursos': cursos,
    }
    
    return render(request, 'administrador/gestion_cursos.html', context)

@login_required
@user_passes_test(es_administrador)
def generar_reporte(request):
    """Generar reportes académicos"""
    if request.method == 'POST':
        tipo_reporte = request.POST.get('tipo_reporte')
        formato = request.POST.get('formato')  # pdf o excel
        periodo_id = request.POST.get('periodo')
        
        periodo = PeriodoAcademico.objects.get(id=periodo_id)
        
        if tipo_reporte == 'rendimiento_general':
            return generar_reporte_rendimiento_general(request, periodo, formato)
        
    periodos = PeriodoAcademico.objects.all()
    context = {
        'periodos': periodos,
    }
    
    return render(request, 'administrador/generar_reporte.html', context)

def generar_reporte_rendimiento_general(request, periodo, formato):
    """Reporte de rendimiento académico general"""
    cursos = Curso.objects.filter(periodo=periodo)
    
    if formato == 'pdf':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        titulo = Paragraph(f"<b>Reporte de Rendimiento Académico - {periodo.nombre}</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 20))
        
        data = [['Curso', 'Profesor', 'Inscritos', 'Promedio']]
        
        for curso in cursos:
            inscripciones = curso.inscripciones.all()
            total_inscritos = inscripciones.count()
            promedios = [insc.calcular_promedio() for insc in inscripciones if insc.calcular_promedio() is not None]
            promedio_curso = sum(promedios) / len(promedios) if promedios else 0.0
            
            data.append([
                f"{curso.materia.codigo} - Grupo {curso.grupo}",
                curso.profesor.usuario.get_full_name(),
                str(total_inscritos),
                f"{promedio_curso:.2f}"
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        registrar_actividad(request, 'consultar', 'Reporte', periodo.id, 'Generación de reporte PDF')
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_rendimiento_{periodo.nombre}.pdf"'
        return response
    
    # Formato Excel similar...
    return redirect('generar_reporte')


# ==================== NOTIFICACIONES ====================

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Marcar notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leida = True
    notificacion.save()
    
    return JsonResponse({'success': True})

@login_required
def todas_notificaciones(request):
    """Ver todas las notificaciones"""
    notificaciones = request.user.notificaciones.all()
    
    context = {
        'notificaciones': notificaciones,
    }
    
    return render(request, 'notificaciones.html', context)