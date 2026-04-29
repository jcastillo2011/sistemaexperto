from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Dashboard Instructor
    path('dashboard/', views.dashboard, name='dashboard'),
    path('estudiantes/', views.lista_estudiantes, name='lista_estudiantes'),
    path('estudiantes/<int:pk>/', views.detalle_estudiante, name='detalle_estudiante'),
    path('estudiantes/<int:estudiante_pk>/evaluar/', views.nueva_evaluacion, name='nueva_evaluacion'),
    path('evaluaciones/<int:pk>/resultados/', views.resultados_evaluacion, name='resultados_evaluacion'),

    # Dashboard Estudiante
    path('mi-perfil/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('mi-perfil/evaluaciones/<int:pk>/', views.estudiante_ver_resultados, name='estudiante_ver_resultados'),

    # Panel Administrador
    path('panel/', views.admin_dashboard, name='admin_dashboard'),

    # Instructores
    path('panel/instructores/', views.admin_instructores, name='admin_instructores'),
    path('panel/instructores/crear/', views.admin_crear_instructor, name='admin_crear_instructor'),
    path('panel/instructores/<int:pk>/', views.admin_detalle_instructor, name='admin_detalle_instructor'),
    path('panel/instructores/<int:pk>/editar/', views.admin_editar_instructor, name='admin_editar_instructor'),
    path('panel/instructores/<int:pk>/toggle/', views.admin_toggle_instructor, name='admin_toggle_instructor'),
    path('panel/instructores/<int:pk>/eliminar/', views.admin_eliminar_instructor, name='admin_eliminar_instructor'),

    # Estudiantes
    path('panel/estudiantes/', views.admin_estudiantes, name='admin_estudiantes'),
    path('panel/estudiantes/crear/', views.admin_crear_estudiante, name='admin_crear_estudiante'),
    path('panel/estudiantes/<int:pk>/editar/', views.admin_editar_estudiante, name='admin_editar_estudiante'),
    path('panel/estudiantes/<int:pk>/eliminar/', views.admin_eliminar_estudiante, name='admin_eliminar_estudiante'),

    # Reglas
    path('panel/reglas/', views.admin_reglas, name='admin_reglas'),
    path('panel/reglas/<int:pk>/toggle/', views.admin_toggle_regla, name='admin_toggle_regla'),

    # Evaluaciones (admin)
    path('panel/evaluaciones/', views.admin_evaluaciones, name='admin_evaluaciones'),
    path('panel/evaluaciones/<int:pk>/', views.admin_ver_evaluacion, name='admin_ver_evaluacion'),

    # Mantenimiento
    path('panel/mantenimiento/logs/', views.admin_logs, name='admin_logs'),
    path('panel/mantenimiento/respaldo/', views.admin_respaldo, name='admin_respaldo'),
    path('panel/mantenimiento/restaurar/', views.admin_restaurar, name='admin_restaurar'),
]
