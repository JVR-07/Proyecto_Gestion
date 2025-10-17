![Wallpaper](docs/resources/wallpaper_itt.png)
# Sistema de Distribución Comunitario (SDC)

> **Proyecto académico desarrollado para optimizar la gestión de donaciones y la distribución de recursos en comunidades vulnerables.**  
> Plataforma web integral basada en Django con renderizado del lado del servidor (SSR) para ofrecer una experiencia unificada, segura y eficiente.

## Tabla de Contenido
- [Descripción General](#descripción-general)
- [Funcionalidades Principales](#funcionalidades-principales)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Plan de Desarrollo de Software](#plan-de-desarrollo-de-software)
- [Calidad y Seguridad](#calidad-y-seguridad)
- [Equipo de Desarrollo](#equipo-de-desarrollo)
- [Documentación Extra](#documentación-extra)
---

## Descripción General

El **Sistema de Distribución Comunitario (SDC)** permite conectar **donadores, donatarios e instituciones** en un entorno digital seguro y transparente.  
Su objetivo es **automatizar y centralizar** los procesos de registro, solicitudes de ayuda, donaciones, control de inventario y generación de reportes.

**Objetivos principales:**
- Facilitar la gestión de donaciones masivas y solicitudes individuales.
- Proporcionar control y trazabilidad de recursos mediante un inventario digital.
- Garantizar transparencia y control administrativo.

---

## Funcionalidades Principales

| Módulo | Descripción |
|--------|--------------|
| **Usuarios** | Registro, autenticación y gestión de roles (Donador, Donatario, Institución, Administrador). |
| **Solicitudes de Donación** | Creación, seguimiento y cierre de solicitudes de recursos. |
| **Publicaciones** | Difusión de campañas y necesidades activas. |
| **Almacenes e Inventario** | Control de recursos donados y entregados. |
| **Reportes y Gráficas** | Visualización de datos e indicadores de desempeño. |
| **Denuncias y Moderación** | Control y revisión de reportes de usuarios o publicaciones sospechosas. |

---

## Tecnologías Utilizadas

**Framework principal**
- Django 5.x (Python)
- Django Templates (renderizado del lado del servidor)
- Bootstrap / TailwindCSS para la interfaz
- PostgreSQL para base de datos

**Infraestructura**
- Servidor local durante el desarrollo  
- Despliegue en nube (Render / Railway / AWS EC2)

---

## Arquitectura del Sistema

El sistema utiliza una arquitectura **monolítica MVC (Modelo–Vista–Controlador)**, con las siguientes capas:

1. **Modelo (Models):** Representación de entidades como usuarios, donaciones, almacenes y reportes.  
2. **Vista (Templates):** Interfaz web renderizada del lado del servidor con HTML dinámico.  
3. **Controlador (Views):** Lógica de negocio y control de flujo.  

> Todo el sistema se ejecuta bajo un solo servidor Django, lo que simplifica la integración, el despliegue y la seguridad.

---

## Instalación y Ejecución

### 1\. Clonar el repositorio
```bash
git clone https://github.com/Zer0M4n/Proyecto_Gestion
cd SDC-Django
```
### 2\. Crear entorno virtual e instalar dependencias
> Crear un entorno virtual para el proyecto es opcional; sin embargo, se recomienda crear un entorno virtual específico para gestionar de mejor forma las dependencias.
```bash
python -m venv sdc_env
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3\. Configurar base de datos PostgreSQL
> ⚠ Pendiente...
### 4\. Ejecutar migraciones y servidor
```bash
python manage.py migrate
python manage.py runserver
```

## Plan de Desarrollo de Software
| Iteración | Objetivo                                         | Funcionalidades                     |
| --------- | ------------------------------------------------ | ----------------------------------- |
| **1**     | Configuración del entorno y registro de usuarios | Login, roles, autenticación         |
| **2**     | Solicitudes y donaciones                         | CRUD de solicitudes y donaciones    |
| **3**     | Gestión de inventarios y almacenes               | Administración de recursos físicos  |
| **4**     | Reportes y gráficas                              | Panel de estadísticas e indicadores |
| **5**     | Denuncias y moderación                           | Control de publicaciones y usuarios |
| **6**     | Optimización y despliegue                        | Pruebas finales, métricas y entrega |
## Calidad y Seguridad
- Cumple con estándares **ISO 9001**, **MOPROSOFT** y **CMMI**.
- Contraseñas cifradas con algoritmos robustos.
- Control de acceso basado en roles.
- Validación de formularios y control de errores.
- Auditorías internas y métricas de calidad implementadas (ver `docs/plan-calidad.md`).
## Equipo de Desarrollo
| Nombre         | Rol                    | Responsabilidad                    |
| -------------- | ---------------------- | ---------------------------------- |
| Javier Machado | Líder de Proyecto | Coordinación y documentación       |
| Omar Marcelino | QA / DBA       | Pruebas, validaciones y base de datos             |
| Cesar González | Desarrollador Backend  | API Rest y endpoits |
| Luis Jiménez   | Desarrollador Frontend  | SSR y apoyo en UX/UI     |
| José Bautista  | Dev Frontend          | Encargado de UX/UI      |
## Documentación Extra
- [SRS](docs/SRS.md)
- [Plan de Calidad](docs/plan-calidad.md)