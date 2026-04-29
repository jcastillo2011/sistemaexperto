from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from functools import wraps
from .models import Estudiante, Evaluacion, Recomendacion, Instructor, Regla, LogSistema
from .forms import (CrearInstructorForm, EditarInstructorForm,
                    CrearEstudianteForm, EditarEstudianteForm, EvaluacionForm)
from .expert_system import ejecutar_motor, cargar_reglas_iniciales


def registrar_log(request, accion, descripcion):
    """Registra una acción en el log del sistema."""
    ip = request.META.get('REMOTE_ADDR')
    LogSistema.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion,
        descripcion=descripcion,
        ip=ip,
    )


# ─── Decoradores de rol ───────────────────────────────────────────────────────

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para acceder a esa sección.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def _es_estudiante(user):
    """Verifica si el usuario tiene un perfil de estudiante en la base de datos."""
    try:
        user.estudiante_perfil
        return True
    except Exception:
        return False


def instructor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_staff:
            return redirect('admin_dashboard')
        if _es_estudiante(request.user):
            return redirect('estudiante_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def estudiante_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not _es_estudiante(request.user):
            messages.error(request, 'Acceso restringido a estudiantes.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── Autenticación ────────────────────────────────────────────────────────────

def iniciar_sesion(request):
    if request.user.is_authenticated:
        return _redirigir_por_rol(request.user)
    if request.method == 'POST':
        user = authenticate(request,
                            username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user:
            login(request, user)
            registrar_log(request, 'login', f'Inicio de sesión: {user.username}')
            return _redirigir_por_rol(user)
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'sistex/login.html')


def _redirigir_por_rol(user):
    if user.is_staff:
        return redirect('admin_dashboard')
    if _es_estudiante(user):
        return redirect('estudiante_dashboard')
    return redirect('dashboard')


def cerrar_sesion(request):
    registrar_log(request, 'logout', f'Cierre de sesión: {request.user.username}')
    logout(request)
    return redirect('login')


# ─── Dashboard Instructor ─────────────────────────────────────────────────────

@instructor_required
def dashboard(request):
    cargar_reglas_iniciales()
    instructor = get_object_or_404(Instructor, usuario=request.user)
    estudiantes = Estudiante.objects.filter(instructor=instructor)
    total_evaluaciones = Evaluacion.objects.filter(instructor=instructor).count()
    return render(request, 'sistex/dashboard.html', {
        'instructor': instructor,
        'estudiantes': estudiantes,
        'total_evaluaciones': total_evaluaciones,
    })


# ─── Dashboard Estudiante ─────────────────────────────────────────────────────

@estudiante_required
def estudiante_dashboard(request):
    estudiante = request.user.estudiante_perfil
    evaluaciones = estudiante.evaluaciones.order_by('-fecha')
    return render(request, 'sistex/estudiante/dashboard.html', {
        'estudiante': estudiante,
        'evaluaciones': evaluaciones,
    })


@estudiante_required
def estudiante_ver_resultados(request, pk):
    estudiante = request.user.estudiante_perfil
    evaluacion = get_object_or_404(Evaluacion, pk=pk, estudiante=estudiante)
    recomendaciones = evaluacion.recomendaciones.all()
    return render(request, 'sistex/evaluaciones/resultados.html', {
        'evaluacion': evaluacion,
        'recomendaciones': recomendaciones,
    })


# ─── Panel Administrador ──────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    cargar_reglas_iniciales()
    total_instructores   = Instructor.objects.count()
    total_estudiantes    = Estudiante.objects.count()
    total_evaluaciones   = Evaluacion.objects.count()
    total_reglas         = Regla.objects.filter(activa=True).count()
    ultimas_evaluaciones = Evaluacion.objects.select_related('estudiante', 'instructor').order_by('-fecha')[:5]
    return render(request, 'sistex/admin/dashboard.html', {
        'total_instructores':   total_instructores,
        'total_estudiantes':    total_estudiantes,
        'total_evaluaciones':   total_evaluaciones,
        'total_reglas':         total_reglas,
        'ultimas_evaluaciones': ultimas_evaluaciones,
    })


# ── Gestión de Instructores ──

@admin_required
def admin_instructores(request):
    instructores = Instructor.objects.select_related('usuario').all()
    return render(request, 'sistex/admin/instructores.html', {'instructores': instructores})


@admin_required
def admin_crear_instructor(request):
    if request.method == 'POST':
        form = CrearInstructorForm(request.POST)
        if form.is_valid():
            user = form.save()
            registrar_log(request, 'crear', f'Instructor creado: {user.get_full_name()}')
            messages.success(request, f'Instructor {user.get_full_name()} creado correctamente.')
            return redirect('admin_instructores')
    else:
        form = CrearInstructorForm()
    return render(request, 'sistex/admin/form_instructor.html', {
        'form': form, 'titulo': 'Crear Instructor'
    })


@admin_required
def admin_editar_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        form = EditarInstructorForm(request.POST, instructor=instructor)
        if form.is_valid():
            form.save(instructor)
            registrar_log(request, 'editar', f'Instructor editado: {instructor}')
            messages.success(request, 'Instructor actualizado correctamente.')
            return redirect('admin_detalle_instructor', pk=pk)
    else:
        form = EditarInstructorForm(instructor=instructor)
    return render(request, 'sistex/admin/form_instructor.html', {
        'form': form, 'titulo': 'Editar Instructor'
    })


@admin_required
def admin_detalle_instructor(request, pk):
    instructor   = get_object_or_404(Instructor, pk=pk)
    estudiantes  = Estudiante.objects.filter(instructor=instructor)
    evaluaciones = Evaluacion.objects.filter(instructor=instructor).order_by('-fecha')
    return render(request, 'sistex/admin/detalle_instructor.html', {
        'instructor':  instructor,
        'estudiantes': estudiantes,
        'evaluaciones': evaluaciones,
    })


@admin_required
def admin_toggle_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        instructor.usuario.is_active = not instructor.usuario.is_active
        instructor.usuario.save()
        estado = 'activado' if instructor.usuario.is_active else 'desactivado'
        registrar_log(request, 'toggle', f'Instructor {estado}: {instructor}')
        messages.success(request, f'Instructor {instructor} {estado} correctamente.')
    return redirect('admin_instructores')


# ── Gestión de Estudiantes ──

@admin_required
def admin_estudiantes(request):
    estudiantes = Estudiante.objects.select_related('instructor__usuario').all()
    return render(request, 'sistex/admin/estudiantes.html', {'estudiantes': estudiantes})


@admin_required
def admin_crear_estudiante(request):
    if request.method == 'POST':
        form = CrearEstudianteForm(request.POST)
        if form.is_valid():
            estudiante = form.save()
            registrar_log(request, 'crear', f'Estudiante creado: {estudiante.nombre}')
            messages.success(request, f'Estudiante {estudiante.nombre} creado correctamente.')
            return redirect('admin_estudiantes')
    else:
        form = CrearEstudianteForm()
    return render(request, 'sistex/admin/form_estudiante.html', {
        'form': form, 'titulo': 'Crear Estudiante'
    })


@admin_required
def admin_editar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EditarEstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            registrar_log(request, 'editar', f'Estudiante editado: {estudiante.nombre}')
            messages.success(request, 'Estudiante actualizado correctamente.')
            return redirect('admin_estudiantes')
    else:
        form = EditarEstudianteForm(instance=estudiante)
    return render(request, 'sistex/admin/form_estudiante.html', {
        'form': form, 'titulo': 'Editar Estudiante'
    })


@admin_required
def admin_eliminar_estudiante(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        if estudiante.usuario:
            estudiante.usuario.delete()
        else:
            estudiante.delete()
        messages.success(request, f'Estudiante {estudiante.nombre} eliminado.')
        registrar_log(request, 'eliminar', f'Estudiante eliminado: {estudiante.nombre}')
        return redirect('admin_estudiantes')
    return render(request, 'sistex/admin/confirmar_eliminar.html', {'objeto': estudiante, 'tipo': 'estudiante'})


@admin_required
def admin_eliminar_instructor(request, pk):
    instructor = get_object_or_404(Instructor, pk=pk)
    if request.method == 'POST':
        instructor.usuario.delete()
        registrar_log(request, 'eliminar', f'Instructor eliminado: {instructor}')
        messages.success(request, 'Instructor eliminado correctamente.')
        return redirect('admin_instructores')
    return render(request, 'sistex/admin/confirmar_eliminar.html', {'objeto': instructor, 'tipo': 'instructor'})


# ── Evaluaciones ──

@admin_required
def admin_evaluaciones(request):
    evaluaciones = Evaluacion.objects.select_related('estudiante', 'instructor').order_by('-fecha')
    return render(request, 'sistex/admin/evaluaciones.html', {'evaluaciones': evaluaciones})


@admin_required
def admin_ver_evaluacion(request, pk):
    evaluacion = get_object_or_404(Evaluacion, pk=pk)
    recomendaciones = evaluacion.recomendaciones.all()
    return render(request, 'sistex/evaluaciones/resultados.html', {
        'evaluacion': evaluacion,
        'recomendaciones': recomendaciones,
        'es_admin': True,
    })


# ── Reglas ──

@admin_required
def admin_reglas(request):
    reglas = Regla.objects.all().order_by('campo_evaluado', 'valor_condicion')
    return render(request, 'sistex/admin/reglas.html', {'reglas': reglas})


@admin_required
def admin_toggle_regla(request, pk):
    regla = get_object_or_404(Regla, pk=pk)
    if request.method == 'POST':
        regla.activa = not regla.activa
        regla.save()
        estado = 'activada' if regla.activa else 'desactivada'
        registrar_log(request, 'toggle', f'Regla {estado}: {regla.nombre}')
        messages.success(request, f'Regla "{regla.nombre}" {estado}.')
    return redirect('admin_reglas')


# ── Mantenimiento ──

import os
import json
import shutil
from datetime import datetime
from django.http import HttpResponse
from django.core import serializers
from django.conf import settings


@admin_required
def admin_logs(request):
    logs = LogSistema.objects.select_related('usuario').order_by('-fecha')[:200]
    return render(request, 'sistex/admin/mantenimiento/logs.html', {'logs': logs})


@admin_required
def admin_respaldo(request):
    """Genera un respaldo de toda la base de datos en formato JSON y lo descarga."""
    from sistex.models import Instructor, Estudiante, Evaluacion, Regla, Recomendacion
    from django.contrib.auth.models import User

    if request.method == 'POST':
        registrar_log(request, 'respaldo', 'Respaldo de base de datos generado')
        datos = {}
        modelos = {
            'usuarios':       User.objects.all(),
            'instructores':   Instructor.objects.all(),
            'estudiantes':    Estudiante.objects.all(),
            'evaluaciones':   Evaluacion.objects.all(),
            'reglas':         Regla.objects.all(),
            'recomendaciones': Recomendacion.objects.all(),
        }
        for nombre, queryset in modelos.items():
            datos[nombre] = json.loads(serializers.serialize('json', queryset))

        contenido = json.dumps(datos, ensure_ascii=False, indent=2)
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        response = HttpResponse(contenido, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="respaldo_sistea_{fecha}.json"'
        return response

    return render(request, 'sistex/admin/mantenimiento/respaldo.html')


@admin_required
def admin_restaurar(request):
    """Restaura la base de datos desde un archivo JSON de respaldo."""
    from django.contrib.auth.models import User
    from sistex.models import Instructor, Estudiante, Evaluacion, Regla, Recomendacion

    if request.method == 'POST' and request.FILES.get('archivo'):
        try:
            archivo = request.FILES['archivo']
            datos = json.loads(archivo.read().decode('utf-8'))

            # Restaurar en orden para respetar dependencias
            orden = ['usuarios', 'instructores', 'estudiantes', 'reglas', 'evaluaciones', 'recomendaciones']
            total = 0
            for clave in orden:
                if clave in datos:
                    for obj in serializers.deserialize('json', json.dumps(datos[clave])):
                        obj.save()
                        total += 1

            messages.success(request, f'Restauración completada. {total} registros procesados.')
            registrar_log(request, 'restaurar', f'Restauración de base de datos: {total} registros')
        except Exception as e:
            messages.error(request, f'Error al restaurar: {str(e)}')
        return redirect('admin_restaurar')

    return render(request, 'sistex/admin/mantenimiento/restaurar.html')


# ─── Estudiantes (vista Instructor) ──────────────────────────────────────────

@instructor_required
def lista_estudiantes(request):
    instructor = get_object_or_404(Instructor, usuario=request.user)
    estudiantes = Estudiante.objects.filter(instructor=instructor)
    return render(request, 'sistex/estudiantes/lista.html', {'estudiantes': estudiantes})


@instructor_required
def detalle_estudiante(request, pk):
    instructor = get_object_or_404(Instructor, usuario=request.user)
    estudiante = get_object_or_404(Estudiante, pk=pk, instructor=instructor)
    evaluaciones = estudiante.evaluaciones.all()
    return render(request, 'sistex/estudiantes/detalle.html', {
        'estudiante': estudiante,
        'evaluaciones': evaluaciones,
    })


# ─── Evaluaciones ─────────────────────────────────────────────────────────────

@instructor_required
def nueva_evaluacion(request, estudiante_pk):
    instructor = get_object_or_404(Instructor, usuario=request.user)
    estudiante = get_object_or_404(Estudiante, pk=estudiante_pk, instructor=instructor)
    if request.method == 'POST':
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            evaluacion = form.save(commit=False)
            evaluacion.estudiante = estudiante
            evaluacion.instructor = instructor
            evaluacion.save()
            recomendaciones = ejecutar_motor(evaluacion)
            registrar_log(request, 'evaluar', f'Evaluación realizada: {estudiante.nombre} por {instructor}')
            messages.success(request, f'Evaluación completada. Se generaron {len(recomendaciones)} recomendaciones.')
            return redirect('resultados_evaluacion', pk=evaluacion.pk)
    else:
        form = EvaluacionForm()
    return render(request, 'sistex/evaluaciones/form.html', {
        'form': form, 'estudiante': estudiante,
    })


@login_required
def resultados_evaluacion(request, pk):
    if request.user.is_staff:
        evaluacion = get_object_or_404(Evaluacion, pk=pk)
    elif _es_estudiante(request.user):
        evaluacion = get_object_or_404(Evaluacion, pk=pk, estudiante=request.user.estudiante_perfil)
    else:
        instructor = get_object_or_404(Instructor, usuario=request.user)
        evaluacion = get_object_or_404(Evaluacion, pk=pk, instructor=instructor)
    recomendaciones = evaluacion.recomendaciones.all()
    return render(request, 'sistex/evaluaciones/resultados.html', {
        'evaluacion': evaluacion,
        'recomendaciones': recomendaciones,
        'es_admin': request.user.is_staff,
    })
