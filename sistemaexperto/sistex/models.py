from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    especialidad = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.usuario.username})"

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructores"


class Estudiante(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='estudiante_perfil')
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True, related_name='estudiantes')
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class Evaluacion(models.Model):
    # Niveles de dificultad para cada área
    NIVEL = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='evaluaciones')
    instructor = models.ForeignKey(Instructor, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    # Áreas de evaluación TEA
    dificultad_comunicacion = models.CharField(max_length=10, choices=NIVEL, default='bajo')
    conductas_repetitivas = models.CharField(max_length=10, choices=NIVEL, default='bajo')
    interaccion_social = models.CharField(max_length=10, choices=NIVEL, default='bajo')
    sensibilidad_sensorial = models.CharField(max_length=10, choices=NIVEL, default='bajo')
    atencion_concentracion = models.CharField(max_length=10, choices=NIVEL, default='bajo')
    habilidades_motoras = models.CharField(max_length=10, choices=NIVEL, default='bajo')

    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Evaluación de {self.estudiante.nombre} - {self.fecha.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"
        ordering = ['-fecha']


class Regla(models.Model):
    """
    Representa una regla del tipo SI-ENTONCES en la base de conocimientos.
    condicion: descripción textual de la condición (para documentación)
    campo_evaluado: campo del modelo Evaluacion que se evalúa
    valor_condicion: valor que activa la regla (bajo, medio, alto)
    recomendacion: acción pedagógica sugerida
    """
    nombre = models.CharField(max_length=200)
    campo_evaluado = models.CharField(max_length=50)
    valor_condicion = models.CharField(max_length=10)
    recomendacion = models.TextField()
    recurso_didactico = models.CharField(max_length=200, blank=True)
    fuente_bibliografica = models.CharField(max_length=300, blank=True, verbose_name='Fuente bibliográfica')
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Regla"
        verbose_name_plural = "Reglas"


class Recomendacion(models.Model):
    """
    Resultado generado por el motor de inferencia para una evaluación específica.
    """
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='recomendaciones')
    regla = models.ForeignKey(Regla, on_delete=models.SET_NULL, null=True, related_name='recomendaciones_generadas')
    descripcion = models.TextField()
    recurso_didactico = models.CharField(max_length=200, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recomendación para {self.evaluacion.estudiante.nombre}"

    class Meta:
        verbose_name = "Recomendación"
        verbose_name_plural = "Recomendaciones"


class LogSistema(models.Model):
    ACCIONES = [
        ('login',         'Inicio de sesión'),
        ('logout',        'Cierre de sesión'),
        ('crear',         'Creación'),
        ('editar',        'Edición'),
        ('eliminar',      'Eliminación'),
        ('evaluar',       'Evaluación'),
        ('respaldo',      'Respaldo de BD'),
        ('restaurar',     'Restauración de BD'),
        ('toggle',        'Cambio de estado'),
    ]

    usuario     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion      = models.CharField(max_length=20, choices=ACCIONES)
    descripcion = models.CharField(max_length=300)
    fecha       = models.DateTimeField(auto_now_add=True)
    ip          = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"[{self.fecha.strftime('%d/%m/%Y %H:%M')}] {self.usuario} - {self.accion}"

    class Meta:
        verbose_name = "Log del Sistema"
        verbose_name_plural = "Logs del Sistema"
        ordering = ['-fecha']
