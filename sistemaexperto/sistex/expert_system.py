"""
Motor de inferencia del sistema experto TEA.
Implementa encadenamiento hacia adelante (forward chaining):
- Se parte de los hechos (datos de la evaluación)
- Se recorren las reglas activas
- Se disparan las reglas cuyas condiciones se cumplen
- Se generan las recomendaciones correspondientes
"""

from .models import Regla, Recomendacion


def ejecutar_motor(evaluacion):
    """
    Recibe una instancia de Evaluacion y aplica todas las reglas activas.
    Retorna la lista de Recomendaciones generadas.
    """
    Recomendacion.objects.filter(evaluacion=evaluacion).delete()

    hechos = {
        'dificultad_comunicacion': evaluacion.dificultad_comunicacion,
        'conductas_repetitivas':   evaluacion.conductas_repetitivas,
        'interaccion_social':      evaluacion.interaccion_social,
        'sensibilidad_sensorial':  evaluacion.sensibilidad_sensorial,
        'atencion_concentracion':  evaluacion.atencion_concentracion,
        'habilidades_motoras':     evaluacion.habilidades_motoras,
    }

    recomendaciones_generadas = []

    for regla in Regla.objects.filter(activa=True):
        valor_hecho = hechos.get(regla.campo_evaluado)
        if valor_hecho == regla.valor_condicion:
            rec = Recomendacion.objects.create(
                evaluacion=evaluacion,
                regla=regla,
                descripcion=regla.recomendacion,
                recurso_didactico=regla.recurso_didactico,
            )
            recomendaciones_generadas.append(rec)

    return recomendaciones_generadas


def cargar_reglas_iniciales():
    """
    Carga la base de conocimientos completa si no existen reglas.
    Cada regla incluye fuente bibliográfica para respaldo académico.
    """
    if Regla.objects.exists():
        return

    reglas = [

        # ── COMUNICACIÓN ──────────────────────────────────────────────────────
        {
            'nombre': 'Comunicación nivel bajo → Estimulación del lenguaje',
            'campo_evaluado': 'dificultad_comunicacion',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante muestra buenas habilidades comunicativas. Continuar estimulando con actividades de narración, conversación espontánea y ampliación de vocabulario para potenciar el logro alcanzado.',
            'recurso_didactico': 'Cuentos interactivos, juegos de palabras, diálogos guiados, lectura compartida',
            'fuente_bibliografica': 'American Speech-Language-Hearing Association (ASHA, 2006). Guidelines for Speech-Language Pathologists in Diagnosis, Assessment, and Treatment of Autism Spectrum Disorders.',
        },
        {
            'nombre': 'Comunicación nivel medio → Apoyo visual y conversación estructurada',
            'campo_evaluado': 'dificultad_comunicacion',
            'valor_condicion': 'medio',
            'recomendacion': 'Reforzar la comunicación con apoyos visuales, rutinas de conversación estructuradas y modelado del lenguaje. Introducir el uso de frases completas y turnos de conversación.',
            'recurso_didactico': 'Láminas visuales, cuentos sociales, videos modelados, tarjetas de secuencias',
            'fuente_bibliografica': 'Bondy, A. & Frost, L. (2001). The Picture Exchange Communication System. Behavior Modification, 25(5), 725-744.',
        },
        {
            'nombre': 'Comunicación nivel alto → Sistema CAA y PECS',
            'campo_evaluado': 'dificultad_comunicacion',
            'valor_condicion': 'alto',
            'recomendacion': 'Implementar sistema de Comunicación Aumentativa y Alternativa (CAA) con pictogramas PECS. Coordinar con terapeuta del lenguaje para intervención intensiva y establecer un sistema funcional de comunicación.',
            'recurso_didactico': 'Tarjetas PECS, tableros de comunicación, aplicación Proloquo2Go, ARASAAC',
            'fuente_bibliografica': 'Bondy, A. & Frost, L. (1994). The Picture Exchange Communication System. Focus on Autistic Behavior, 9(3), 1-19. / Mirenda, P. (2003). Toward Functional Augmentative and Alternative Communication for Students with Autism. Language, Speech, and Hearing Services in Schools, 34(3), 203-216.',
        },

        # ── CONDUCTAS REPETITIVAS ─────────────────────────────────────────────
        {
            'nombre': 'Conductas repetitivas nivel bajo → Mantenimiento de rutinas positivas',
            'campo_evaluado': 'conductas_repetitivas',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante muestra flexibilidad conductual adecuada. Mantener rutinas predecibles y continuar fomentando la adaptación a cambios graduales para consolidar la flexibilidad cognitiva.',
            'recurso_didactico': 'Agenda diaria visual, actividades de transición, juegos de cambio de roles',
            'fuente_bibliografica': 'Schopler, E., Mesibov, G. & Hearsey, K. (1995). Structured Teaching in the TEACCH System. En E. Schopler & G. Mesibov (Eds.), Learning and Cognition in Autism. Plenum Press.',
        },
        {
            'nombre': 'Conductas repetitivas nivel medio → Rutinas con variaciones graduales',
            'campo_evaluado': 'conductas_repetitivas',
            'valor_condicion': 'medio',
            'recomendacion': 'Introducir variaciones graduales en las rutinas para fomentar la flexibilidad cognitiva. Usar historias sociales para preparar al estudiante ante cambios y redirigir conductas repetitivas hacia actividades funcionales.',
            'recurso_didactico': 'Tablero de rutinas, juegos de roles, historias sociales de Carol Gray, tarjetas de anticipación',
            'fuente_bibliografica': 'Gray, C. (1993). Social Stories: Improving Responses of Students with Autism with Accurate Social Information. Focus on Autistic Behavior, 8(1), 1-10.',
        },
        {
            'nombre': 'Conductas repetitivas nivel alto → Estructura TEACCH y ABA',
            'campo_evaluado': 'conductas_repetitivas',
            'valor_condicion': 'alto',
            'recomendacion': 'Diseñar actividades altamente estructuradas con horarios visuales y transiciones claras siguiendo el modelo TEACCH. Aplicar técnicas ABA para redirigir conductas repetitivas hacia comportamientos funcionales mediante refuerzo diferencial.',
            'recurso_didactico': 'Agenda visual, temporizador visual, cajas de trabajo TEACCH, sistema de economía de fichas',
            'fuente_bibliografica': 'Mesibov, G., Shea, V. & Schopler, E. (2005). The TEACCH Approach to Autism Spectrum Disorders. Springer. / Cooper, J., Heron, T. & Heward, W. (2007). Applied Behavior Analysis (2nd ed.). Pearson.',
        },

        # ── INTERACCIÓN SOCIAL ────────────────────────────────────────────────
        {
            'nombre': 'Interacción social nivel bajo → Potenciar habilidades de liderazgo',
            'campo_evaluado': 'interaccion_social',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante muestra buenas habilidades sociales. Promover roles de liderazgo en actividades grupales, trabajo colaborativo y situaciones sociales más complejas para seguir desarrollando sus competencias.',
            'recurso_didactico': 'Proyectos grupales, juegos cooperativos, actividades de tutoría entre pares',
            'fuente_bibliografica': 'Strain, P. & Schwartz, I. (2001). ABA and the Development of Meaningful Social Relations for Young Children with Autism. Focus on Autism and Other Developmental Disabilities, 16(2), 120-128.',
        },
        {
            'nombre': 'Interacción social nivel medio → Juego paralelo y actividades en parejas',
            'campo_evaluado': 'interaccion_social',
            'valor_condicion': 'medio',
            'recomendacion': 'Promover el juego paralelo y actividades en parejas con mediación del instructor. Usar historias sociales para enseñar habilidades de inicio de conversación, turnos y resolución de conflictos.',
            'recurso_didactico': 'Juegos de mesa adaptados, actividades de turno, títeres, historias sociales',
            'fuente_bibliografica': 'Gray, C. & Garand, J. (1993). Social Stories: Improving Responses of Students with Autism. Focus on Autistic Behavior, 8(1), 1-10.',
        },
        {
            'nombre': 'Interacción social nivel alto → Entrenamiento en habilidades sociales',
            'campo_evaluado': 'interaccion_social',
            'valor_condicion': 'alto',
            'recomendacion': 'Implementar programa estructurado de entrenamiento en habilidades sociales (EHS) con grupos pequeños. Usar modelado por video, role-playing y refuerzo positivo para enseñar habilidades básicas de interacción.',
            'recurso_didactico': 'Programa PEERS, modelado por video, grupos de habilidades sociales, juegos cooperativos guiados',
            'fuente_bibliografica': 'Laugeson, E. & Frankel, F. (2010). Social Skills for Teenagers with Developmental and Autism Spectrum Disorders: The PEERS Treatment Manual. Routledge.',
        },

        # ── SENSIBILIDAD SENSORIAL ────────────────────────────────────────────
        {
            'nombre': 'Sensibilidad sensorial nivel bajo → Enriquecimiento sensorial',
            'campo_evaluado': 'sensibilidad_sensorial',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante tolera adecuadamente los estímulos sensoriales. Enriquecer el ambiente con experiencias sensoriales variadas y controladas para estimular el desarrollo sensorial integral.',
            'recurso_didactico': 'Rincón sensorial, materiales de diferentes texturas, actividades de exploración sensorial',
            'fuente_bibliografica': 'Ayres, A.J. (1972). Sensory Integration and Learning Disorders. Western Psychological Services.',
        },
        {
            'nombre': 'Sensibilidad sensorial nivel medio → Integración sensorial gradual',
            'campo_evaluado': 'sensibilidad_sensorial',
            'valor_condicion': 'medio',
            'recomendacion': 'Incorporar actividades de integración sensorial de forma gradual y controlada. Identificar los estímulos que generan incomodidad y diseñar un plan de desensibilización progresiva.',
            'recurso_didactico': 'Materiales de texturas, pelotas sensoriales, actividades de movimiento, dieta sensorial',
            'fuente_bibliografica': 'Ayres, A.J. (1979). Sensory Integration and the Child. Western Psychological Services. / Miller, L.J. (2006). Sensational Kids: Hope and Help for Children with Sensory Processing Disorder. Putnam.',
        },
        {
            'nombre': 'Sensibilidad sensorial nivel alto → Adaptación ambiental y autorregulación',
            'campo_evaluado': 'sensibilidad_sensorial',
            'valor_condicion': 'alto',
            'recomendacion': 'Adaptar el ambiente reduciendo estímulos sensoriales perturbadores. Implementar una dieta sensorial personalizada con el apoyo de terapeuta ocupacional y enseñar estrategias de autorregulación.',
            'recurso_didactico': 'Auriculares reductores de ruido, iluminación tenue, rincón de calma, chaleco de presión, fidget tools',
            'fuente_bibliografica': 'Wilbarger, P. & Wilbarger, J. (1991). Sensory Defensiveness in Children Aged 2-12. Avanti Educational Programs. / Marco, E., Hinkley, L., Hill, S. & Nagarajan, S. (2011). Sensory Processing in Autism. Neuron, 70(2), 187-199.',
        },

        # ── ATENCIÓN Y CONCENTRACIÓN ──────────────────────────────────────────
        {
            'nombre': 'Atención nivel bajo → Actividades de enriquecimiento cognitivo',
            'campo_evaluado': 'atencion_concentracion',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante muestra buena capacidad de atención y concentración. Proponer actividades cognitivas más complejas y desafiantes para mantener la motivación y seguir desarrollando las funciones ejecutivas.',
            'recurso_didactico': 'Rompecabezas complejos, juegos de estrategia, actividades de resolución de problemas',
            'fuente_bibliografica': 'Dawson, G. & Osterling, J. (1997). Early Intervention in Autism. En M. Guralnick (Ed.), The Effectiveness of Early Intervention. Brookes Publishing.',
        },
        {
            'nombre': 'Atención nivel medio → Estrategias de focalización',
            'campo_evaluado': 'atencion_concentracion',
            'valor_condicion': 'medio',
            'recomendacion': 'Usar estrategias de focalización como señales visuales, recordatorios de tarea y segmentación de actividades. Alternar tareas de alta y baja demanda cognitiva para mantener el nivel de atención.',
            'recurso_didactico': 'Marcadores de posición, listas de verificación, música de fondo suave, temporizador visual',
            'fuente_bibliografica': 'Koegel, R. & Koegel, L. (2006). Pivotal Response Treatments for Autism. Brookes Publishing.',
        },
        {
            'nombre': 'Atención nivel alto → Tareas cortas con refuerzo positivo ABA',
            'campo_evaluado': 'atencion_concentracion',
            'valor_condicion': 'alto',
            'recomendacion': 'Dividir las tareas en pasos muy cortos (5-10 minutos) con refuerzo positivo inmediato tras cada logro. Implementar pausas activas entre actividades y usar el sistema de economía de fichas para motivar la participación.',
            'recurso_didactico': 'Temporizador visual, sistema de economía de fichas, actividades de 5-10 minutos, pausas activas',
            'fuente_bibliografica': 'Cooper, J., Heron, T. & Heward, W. (2007). Applied Behavior Analysis (2nd ed.). Pearson. / Lovaas, O.I. (1987). Behavioral Treatment and Normal Educational and Intellectual Functioning in Young Autistic Children. Journal of Consulting and Clinical Psychology, 55(1), 3-9.',
        },

        # ── HABILIDADES MOTORAS ───────────────────────────────────────────────
        {
            'nombre': 'Habilidades motoras nivel bajo → Actividades de mantenimiento motor',
            'campo_evaluado': 'habilidades_motoras',
            'valor_condicion': 'bajo',
            'recomendacion': 'El estudiante presenta buen desarrollo motor. Mantener y enriquecer las habilidades motoras con actividades que integren motricidad fina y gruesa de forma lúdica y creativa.',
            'recurso_didactico': 'Actividades artísticas, deportes adaptados, juegos de construcción avanzados',
            'fuente_bibliografica': 'Provost, B., Lopez, B. & Heimerl, S. (2007). A Comparison of Motor Delays in Young Children: Autism Spectrum Disorder, Developmental Delay, and Developmental Concerns. Journal of Autism and Developmental Disorders, 37(2), 321-328.',
        },
        {
            'nombre': 'Habilidades motoras nivel medio → Ejercicios de motricidad integrados',
            'campo_evaluado': 'habilidades_motoras',
            'valor_condicion': 'medio',
            'recomendacion': 'Incluir ejercicios de motricidad fina y gruesa en la rutina diaria de forma sistemática. Usar actividades funcionales que requieran coordinación ojo-mano y control postural.',
            'recurso_didactico': 'Actividades de recorte, enhebrado, juegos de construcción, circuitos de psicomotricidad',
            'fuente_bibliografica': 'Fournier, K., Hass, C., Naik, S., Lodha, N. & Cauraugh, J. (2010). Motor Coordination in Autism Spectrum Disorders: A Synthesis and Meta-Analysis. Journal of Autism and Developmental Disorders, 40(10), 1227-1240.',
        },
        {
            'nombre': 'Habilidades motoras nivel alto → Terapia ocupacional especializada',
            'campo_evaluado': 'habilidades_motoras',
            'valor_condicion': 'alto',
            'recomendacion': 'Coordinar con terapia ocupacional para un plan de intervención motora individualizado. Adaptar materiales y herramientas del aula para facilitar la participación. Trabajar la motricidad fina con actividades graduadas en dificultad.',
            'recurso_didactico': 'Lápices adaptados, plastilina terapéutica, actividades de motricidad gruesa, equipamiento de psicomotricidad',
            'fuente_bibliografica': 'Case-Smith, J. & Arbesman, M. (2008). Evidence-Based Review of Interventions for Autism Used in or of Relevance to Occupational Therapy. American Journal of Occupational Therapy, 62(4), 416-429.',
        },
    ]

    for r in reglas:
        Regla.objects.create(**r)
