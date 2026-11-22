"""Ejemplos de estimaciones previas que se inyectan en el prompt (contexto CAG).

Son el "conocimiento" del sistema: estimaciones históricas (ficticias) de la
empresa que el modelo usa como referencia para estimar proyectos nuevos.

Reglas comunes a todos los ejemplos:
    - Coste de cada tarea = horas x tarifa del perfil (HOURLY_RATES).
    - Testing y QA = 15 % de las horas de desarrollo (frontend, backend, móvil).
    - Gestión del proyecto = 10 % del total de horas.
    - Horas redondeadas a múltiplos de 5 y totales precalculados.

Attributes:
    HOURLY_RATES: Tarifa por hora (en EUR) de cada perfil.
    ESTIMATION_EXAMPLES: Estimaciones de referencia. Cada una es un
        diccionario con "meeting_summary" (lo que pidió el cliente) y
        "estimation" (la estimación en Markdown).
"""

HOURLY_RATES: dict[str, int] = {
    "PM": 50,
    "UX/UI": 45,
    "Frontend": 50,
    "Backend": 55,
    "Móvil": 55,
    "QA": 40,
    "DevOps": 60,
}

ESTIMATION_EXAMPLES: list[dict[str, str]] = [
    {
        "meeting_summary": (
            "Una tienda de artículos deportivos quiere vender online. Necesita "
            "catálogo con búsqueda y filtros, ficha de producto, carrito y pago con "
            "tarjeta, además de un panel para gestionar productos y pedidos. Solo "
            "web; quieren lanzarla en unos dos meses."
        ),
        "estimation": """
## Estimación: Tienda online

### Desglose de tareas

| Tarea | Perfil | Horas | Tarifa | Coste |
|---|---|---|---|---|
| Diseño UX/UI de catálogo, ficha, carrito y checkout | UX/UI | 40 | 45 €/h | 1.800 € |
| Maquetación de catálogo y ficha de producto | Frontend | 50 | 50 €/h | 2.500 € |
| Carrito y checkout (frontend) | Frontend | 35 | 50 €/h | 1.750 € |
| API de productos con búsqueda y filtros | Backend | 45 | 55 €/h | 2.475 € |
| Carrito y gestión de pedidos (backend) | Backend | 40 | 55 €/h | 2.200 € |
| Integración con pasarela de pago | Backend | 30 | 55 €/h | 1.650 € |
| Panel de administración de productos y pedidos | Backend | 35 | 55 €/h | 1.925 € |
| Despliegue e integración continua | DevOps | 20 | 60 €/h | 1.200 € |
| Testing y QA | QA | 35 | 40 €/h | 1.400 € |
| Gestión del proyecto | PM | 35 | 50 €/h | 1.750 € |

**Total estimado: 365 horas · 18.650 €**

**Equipo recomendado:** 1 desarrollador frontend, 1 desarrollador backend, diseño UX/UI, QA y gestión a tiempo parcial.

**Duración estimada:** 6–7 semanas.
""",
    },
    {
        "meeting_summary": (
            "Una cadena de restaurantes quiere una app para iOS y Android con la "
            "que sus clientes reserven mesa. Debe mostrar los locales, la "
            "disponibilidad en tiempo real y enviar notificaciones de confirmación "
            "y recordatorio. Ya tienen web; la app es nueva."
        ),
        "estimation": """
## Estimación: App móvil de reservas

### Desglose de tareas

| Tarea | Perfil | Horas | Tarifa | Coste |
|---|---|---|---|---|
| Diseño UX/UI de la app | UX/UI | 50 | 45 €/h | 2.250 € |
| Registro, login y perfil | Móvil | 30 | 55 €/h | 1.650 € |
| Listado y búsqueda de restaurantes | Móvil | 40 | 55 €/h | 2.200 € |
| Reserva con disponibilidad en tiempo real | Móvil | 50 | 55 €/h | 2.750 € |
| Notificaciones push | Móvil | 25 | 55 €/h | 1.375 € |
| API de reservas y disponibilidad | Backend | 50 | 55 €/h | 2.750 € |
| Envío de notificaciones (backend) | Backend | 20 | 55 €/h | 1.100 € |
| Publicación en App Store y Google Play | DevOps | 25 | 60 €/h | 1.500 € |
| Testing y QA | QA | 30 | 40 €/h | 1.200 € |
| Gestión del proyecto | PM | 30 | 50 €/h | 1.500 € |

**Total estimado: 350 horas · 18.275 €**

**Equipo recomendado:** 1 desarrollador móvil, 1 desarrollador backend, diseño UX/UI, QA y gestión a tiempo parcial.

**Duración estimada:** 6–7 semanas.
""",
    },
    {
        "meeting_summary": (
            "Una empresa de servicios gestiona sus clientes y encargos con hojas de "
            "cálculo. Quiere un panel web interno para dar de alta clientes y "
            "encargos, con usuarios y roles (administración y técnicos) y "
            "exportación de informes a Excel. El diseño puede ser sencillo."
        ),
        "estimation": """
## Estimación: Herramienta interna de gestión

### Desglose de tareas

| Tarea | Perfil | Horas | Tarifa | Coste |
|---|---|---|---|---|
| Diseño UX/UI del panel | UX/UI | 15 | 45 €/h | 675 € |
| Panel de administración (frontend) | Frontend | 40 | 50 €/h | 2.000 € |
| CRUD de entidades (backend) | Backend | 35 | 55 €/h | 1.925 € |
| Autenticación y roles | Backend | 25 | 55 €/h | 1.375 € |
| Informes y exportación a Excel | Backend | 20 | 55 €/h | 1.100 € |
| Despliegue en servidor interno | DevOps | 10 | 60 €/h | 600 € |
| Testing y QA | QA | 20 | 40 €/h | 800 € |
| Gestión del proyecto | PM | 15 | 50 €/h | 750 € |

**Total estimado: 180 horas · 9.225 €**

**Equipo recomendado:** 1 desarrollador full-stack, con apoyo puntual de diseño UX/UI, QA y gestión.

**Duración estimada:** 4 semanas.
""",
    },
    {
        "meeting_summary": (
            "Una distribuidora quiere sincronizar automáticamente los clientes y "
            "pedidos de su ERP con su CRM en la nube, en ambos sentidos y varias "
            "veces al día. No necesita interfaz: solo un servicio fiable que "
            "registre los errores y reintente los fallos."
        ),
        "estimation": """
## Estimación: Integración con CRM

### Desglose de tareas

| Tarea | Perfil | Horas | Tarifa | Coste |
|---|---|---|---|---|
| Análisis de APIs y mapeo de datos | Backend | 25 | 55 €/h | 1.375 € |
| Conector con la API del CRM | Backend | 40 | 55 €/h | 2.200 € |
| Sincronización bidireccional programada | Backend | 45 | 55 €/h | 2.475 € |
| Gestión de errores y reintentos | Backend | 25 | 55 €/h | 1.375 € |
| Logs y monitorización | DevOps | 15 | 60 €/h | 900 € |
| Despliegue | DevOps | 15 | 60 €/h | 900 € |
| Testing y QA | QA | 20 | 40 €/h | 800 € |
| Gestión del proyecto | PM | 20 | 50 €/h | 1.000 € |

**Total estimado: 205 horas · 11.025 €**

**Equipo recomendado:** 1 desarrollador backend, con apoyo puntual de DevOps, QA y gestión.

**Duración estimada:** 4–5 semanas.
""",
    },
    {
        "meeting_summary": (
            "Una startup quiere lanzar el MVP de una plataforma SaaS de gestión de "
            "turnos para pequeñas empresas. Necesita landing, registro de empresas "
            "con varios usuarios, suscripción mensual con pago recurrente y un "
            "panel de cliente con la funcionalidad principal."
        ),
        "estimation": """
## Estimación: MVP de un SaaS

### Desglose de tareas

| Tarea | Perfil | Horas | Tarifa | Coste |
|---|---|---|---|---|
| Diseño UX/UI (landing, registro y panel) | UX/UI | 60 | 45 €/h | 2.700 € |
| Landing y registro (frontend) | Frontend | 35 | 50 €/h | 1.750 € |
| Panel de cliente (frontend) | Frontend | 60 | 50 €/h | 3.000 € |
| Autenticación y cuentas multiempresa | Backend | 50 | 55 €/h | 2.750 € |
| Suscripciones y pagos recurrentes | Backend | 45 | 55 €/h | 2.475 € |
| API del núcleo del producto | Backend | 70 | 55 €/h | 3.850 € |
| Infraestructura cloud y CI/CD | DevOps | 40 | 60 €/h | 2.400 € |
| Testing y QA | QA | 40 | 40 €/h | 1.600 € |
| Gestión del proyecto | PM | 40 | 50 €/h | 2.000 € |

**Total estimado: 440 horas · 22.525 €**

**Equipo recomendado:** 1 desarrollador frontend, 2 desarrolladores backend, diseño UX/UI, DevOps, QA y gestión.

**Duración estimada:** 8–10 semanas.
""",
    },
]
