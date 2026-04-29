from django import forms
from django.contrib.auth.models import User
from .models import Instructor, Estudiante, Evaluacion


class CrearInstructorForm(forms.Form):
    """Formulario para que el admin cree un instructor con su cuenta de usuario."""
    first_name   = forms.CharField(max_length=50,  label='Nombre')
    last_name    = forms.CharField(max_length=50,  label='Apellido')
    email        = forms.EmailField(label='Correo electrónico')
    username     = forms.CharField(max_length=50,  label='Nombre de usuario')
    password     = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    telefono     = forms.CharField(max_length=20,  required=False, label='Teléfono')
    especialidad = forms.CharField(max_length=100, required=False, label='Especialidad')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
        )
        Instructor.objects.create(
            usuario=user,
            telefono=data.get('telefono', ''),
            especialidad=data.get('especialidad', ''),
        )
        return user


class EditarInstructorForm(forms.Form):
    """Formulario para editar los datos de un instructor."""
    first_name   = forms.CharField(max_length=50,  label='Nombre')
    last_name    = forms.CharField(max_length=50,  label='Apellido')
    email        = forms.EmailField(label='Correo electrónico')
    telefono     = forms.CharField(max_length=20,  required=False, label='Teléfono')
    especialidad = forms.CharField(max_length=100, required=False, label='Especialidad')

    def __init__(self, *args, instructor=None, **kwargs):
        super().__init__(*args, **kwargs)
        if instructor:
            self.fields['first_name'].initial   = instructor.usuario.first_name
            self.fields['last_name'].initial    = instructor.usuario.last_name
            self.fields['email'].initial        = instructor.usuario.email
            self.fields['telefono'].initial     = instructor.telefono
            self.fields['especialidad'].initial = instructor.especialidad

    def save(self, instructor):
        data = self.cleaned_data
        instructor.usuario.first_name = data['first_name']
        instructor.usuario.last_name  = data['last_name']
        instructor.usuario.email      = data['email']
        instructor.usuario.save()
        instructor.telefono     = data.get('telefono', '')
        instructor.especialidad = data.get('especialidad', '')
        instructor.save()
        return instructor


class CrearEstudianteForm(forms.Form):
    """Formulario para que el admin cree un estudiante con su cuenta de usuario."""
    first_name       = forms.CharField(max_length=50,  label='Nombre')
    last_name        = forms.CharField(max_length=50,  label='Apellido')
    username         = forms.CharField(max_length=50,  label='Nombre de usuario')
    password         = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    instructor       = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        label='Instructor asignado'
    )
    observaciones    = forms.CharField(
        required=False,
        label='Observaciones',
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ese nombre de usuario ya está en uso.')
        return username

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
        estudiante = Estudiante.objects.create(
            usuario=user,
            nombre=f"{data['first_name']} {data['last_name']}",
            fecha_nacimiento=data['fecha_nacimiento'],
            instructor=data['instructor'],
            observaciones=data.get('observaciones', ''),
        )
        return estudiante


class EditarEstudianteForm(forms.ModelForm):
    """Formulario para editar datos de un estudiante."""
    class Meta:
        model = Estudiante
        fields = ['nombre', 'fecha_nacimiento', 'instructor', 'observaciones']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'observaciones':    forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nombre':           'Nombre completo',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'instructor':       'Instructor asignado',
            'observaciones':    'Observaciones generales',
        }


class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = [
            'dificultad_comunicacion',
            'conductas_repetitivas',
            'interaccion_social',
            'sensibilidad_sensorial',
            'atencion_concentracion',
            'habilidades_motoras',
            'notas',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'dificultad_comunicacion': 'Dificultad en comunicación',
            'conductas_repetitivas':   'Conductas repetitivas',
            'interaccion_social':      'Dificultad en interacción social',
            'sensibilidad_sensorial':  'Sensibilidad sensorial',
            'atencion_concentracion':  'Dificultad en atención/concentración',
            'habilidades_motoras':     'Dificultad en habilidades motoras',
            'notas':                   'Notas adicionales del instructor',
        }
