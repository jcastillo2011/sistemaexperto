from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Instructor, Estudiante, Evaluacion, Regla, Recomendacion

# Personalizar el título del panel admin
admin.site.site_header  = 'SisTEA · Administración'
admin.site.site_title   = 'SisTEA Admin'
admin.site.index_title  = 'Panel de Administración · Fundación Infocentro'


class InstructorInline(admin.StackedInline):
    model = Instructor
    can_delete = False
    verbose_name_plural = 'Datos del Instructor'
    fields = ['telefono', 'especialidad']


class CustomUserAdmin(UserAdmin):
    inlines = [InstructorInline]
    list_display  = ['username', 'get_full_name', 'email', 'is_active', 'date_joined']
    list_filter   = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering      = ['-date_joined']

    def get_full_name(self, obj):
        return obj.get_full_name() or '—'
    get_full_name.short_description = 'Nombre completo'


# Re-registrar User con el admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display   = ['get_nombre', 'get_email', 'especialidad', 'telefono', 'get_total_estudiantes']
    search_fields  = ['usuario__first_name', 'usuario__last_name', 'usuario__email', 'especialidad']
    list_filter    = ['especialidad']
    readonly_fields = ['get_total_estudiantes']

    def get_nombre(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    get_nombre.short_description = 'Nombre'

    def get_email(self, obj):
        return obj.usuario.email
    get_email.short_description = 'Correo'

    def get_total_estudiantes(self, obj):
        return obj.estudiantes.count()
    get_total_estudiantes.short_description = 'Estudiantes asignados'


class EvaluacionInline(admin.TabularInline):
    model = Evaluacion
    extra = 0
    readonly_fields = ['fecha', 'instructor', 'dificultad_comunicacion', 'conductas_repetitivas',
                       'interaccion_social', 'sensibilidad_sensorial', 'atencion_concentracion', 'habilidades_motoras']
    can_delete = False
    show_change_link = True
    verbose_name_plural = 'Evaluaciones realizadas'


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display   = ['nombre', 'fecha_nacimiento', 'get_instructor', 'get_total_evaluaciones', 'fecha_registro']
    list_filter    = ['instructor', 'fecha_registro']
    search_fields  = ['nombre', 'instructor__usuario__first_name', 'instructor__usuario__last_name']
    ordering       = ['nombre']
    inlines        = [EvaluacionInline]
    readonly_fields = ['fecha_registro']

    fieldsets = [
        ('Datos del Estudiante', {
            'fields': ['nombre', 'fecha_nacimiento', 'instructor', 'observaciones']
        }),
        ('Información del Sistema', {
            'fields': ['fecha_registro'],
            'classes': ['collapse']
        }),
    ]

    def get_instructor(self, obj):
        return obj.instructor or '—'
    get_instructor.short_description = 'Instructor'

    def get_total_evaluaciones(self, obj):
        return obj.evaluaciones.count()
    get_total_evaluaciones.short_description = 'Evaluaciones'


class RecomendacionInline(admin.TabularInline):
    model = Recomendacion
    extra = 0
    readonly_fields = ['regla', 'descripcion', 'recurso_didactico', 'fecha_generacion']
    can_delete = False
    verbose_name_plural = 'Recomendaciones generadas'


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display  = ['get_estudiante', 'get_instructor', 'fecha',
                     'dificultad_comunicacion', 'conductas_repetitivas',
                     'interaccion_social', 'get_total_recomendaciones']
    list_filter   = ['instructor', 'dificultad_comunicacion', 'conductas_repetitivas',
                     'interaccion_social', 'fecha']
    search_fields = ['estudiante__nombre', 'instructor__usuario__first_name']
    ordering      = ['-fecha']
    readonly_fields = ['fecha']
    inlines       = [RecomendacionInline]

    fieldsets = [
        ('Información General', {
            'fields': ['estudiante', 'instructor', 'fecha']
        }),
        ('Áreas Evaluadas', {
            'fields': [
                'dificultad_comunicacion', 'conductas_repetitivas',
                'interaccion_social', 'sensibilidad_sensorial',
                'atencion_concentracion', 'habilidades_motoras'
            ]
        }),
        ('Notas', {
            'fields': ['notas'],
            'classes': ['collapse']
        }),
    ]

    def get_estudiante(self, obj):
        return obj.estudiante.nombre
    get_estudiante.short_description = 'Estudiante'

    def get_instructor(self, obj):
        return obj.instructor or '—'
    get_instructor.short_description = 'Instructor'

    def get_total_recomendaciones(self, obj):
        return obj.recomendaciones.count()
    get_total_recomendaciones.short_description = 'Recomendaciones'


@admin.register(Regla)
class ReglaAdmin(admin.ModelAdmin):
    list_display   = ['nombre', 'campo_evaluado', 'valor_condicion', 'fuente_bibliografica', 'activa']
    list_filter    = ['campo_evaluado', 'valor_condicion', 'activa']
    search_fields  = ['nombre', 'recomendacion', 'fuente_bibliografica']
    list_editable  = ['activa']
    ordering       = ['campo_evaluado', 'valor_condicion']

    fieldsets = [
        ('Condición (SI)', {
            'fields': ['nombre', 'campo_evaluado', 'valor_condicion']
        }),
        ('Acción (ENTONCES)', {
            'fields': ['recomendacion', 'recurso_didactico']
        }),
        ('Respaldo Académico', {
            'fields': ['fuente_bibliografica']
        }),
        ('Estado', {
            'fields': ['activa']
        }),
    ]


@admin.register(Recomendacion)
class RecomendacionAdmin(admin.ModelAdmin):
    list_display   = ['get_estudiante', 'regla', 'fecha_generacion']
    list_filter    = ['fecha_generacion', 'regla']
    search_fields  = ['evaluacion__estudiante__nombre', 'descripcion']
    readonly_fields = ['evaluacion', 'regla', 'descripcion', 'recurso_didactico', 'fecha_generacion']
    ordering       = ['-fecha_generacion']

    def get_estudiante(self, obj):
        return obj.evaluacion.estudiante.nombre
    get_estudiante.short_description = 'Estudiante'
