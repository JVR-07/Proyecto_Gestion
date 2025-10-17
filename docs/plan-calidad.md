

| Producto | Plan de calidad para *Sistema de Distribución Comunitario*. |
| :---- | :---- |
| **Emitido por** | Javier Machado. |
| **Versión** | 1.0 |
| **Fecha** | 29/09/2025 |

# **SDC (Sistema de Distribución Comunitario)**

## **Introducción**

El propósito de este documento es definir las actividades, procesos, métricas y estándares que aseguren la calidad del sistema en todos sus aspectos.Para la realización del mismo, se utilizaron estándares y modelos internacionales para la realización del plan de calidad.

El presente documento tiene como objetivos principales:

* Garantizar que el sistema cumpla con los requisitos funcionales y no funcionales definidos en el SRS.  
* Reducir errores en producción.  
* Asegurar la seguridad de datos verificando que se empleen las medidas necesarias.  
* Cumplir con la entrega dentro de los plazos establecidos.

Este documento aplica a todas las fases del ciclo de vida del Sistema de Distribución Comunitario (SDC): análisis, diseño, desarrollo, pruebas, despliegue y mantenimiento.  
**No cubre:** soporte post-producción fuera del alcance del proyecto académico, ni certificaciones externas (ej. ISO completa).

## **Responsabilidades**

| Rol | Responsabilidades | Persona |
| :---: | ----- | ----- |
| Líder del Proyecto | Planificación, seguimiento, control de entregables. | Javier Machado. |
| Responsables de calidad | Definir estándares, auditorías, métricas, validación de pruebas. | Omar Marcelino. |
| Equipo de Desarrollo | Codificación, revisión entre pares, corrección de defectos. | Javier Machado. Omar Marcelino. Cesar Gonzalez. Luis Jiménez. José Bautista. |
| Equipo de Pruebas | Ejecución de casos de prueba, reporte de defectos, validación. | Cesar Gonzales. Luis Jiménez. José Bautista. |

## **Estándares y modelos**

* **MOPROSOFT:** Organización de procesos en gestión de proyectos de software en México.  
* **CMMI:** Definición de actividades de mejora continua.

## **Actividades de Control de Calidad**

| Actividad | Responsable | Fase |
| ----- | ----- | ----- |
| Revisión de requisitos. | Calidad. | Inicio. |
| Inspección de código. | Desarrolladores. | Desarrollo. |
| Auditorías internas de calidad. | Calidad. | Desarrollo. |
| Reporte y control de incidencias. | Desarrolladores. | Pruebas. |

## **Estrategia de Pruebas**

| Pruebas | Objetivo | Entradas | Responsable | Criterios de salida |
| ----- | ----- | ----- | ----- | ----- |
| Unitarias. | Validar que cada módulo funcione de manera independiente. | Casos unitarios. | Desarrolladores. | 90% de cobertura unitaria. |
| Integración. | Verificar la interacción entre módulos. | Casos de integración. | Desarrolladores. | Todas las interfaces probadas sin errores críticos. |
| Sistema. | Validar que el sistema cumpla con los requisitos funcionales del SRS. | Casos de uso. | Calidad. | 100% de requisitos funcionales ejecutados exitosamente. |
| Seguridad. | Comprobar autenticación, permisos y encriptación de datos. | Usuarios de prueba. | Calidad. | 0 vulnerabilidades críticas, autenticación y privilegios correctos. |
| Aceptación. | Validar el sistema con usuarios reales. | Escenarios piloto, manual de usuario. | Calidad. | 80% satisfacción o mayor. |

Los criterios de aceptación de estas pruebas deben ser los siguientes:

* 100% de los requisitos funcionales probados correctamente.  
* 95% de los casos de prueba exitosos.  
* Cero defectos críticos abiertos.

## **Procedimiento de Control de Cambios**

| Etapa | Descripción | Responsable |
| ----- | ----- | ----- |
| Solicitud de cambio. | Un miembro del equipo o cliente solicita un cambio (requisito, código, documento). | Solicitante. |
| Registro del cambio. | El cambio se documenta con ID único, descripción y prioridad. | Responsable de calidad. |
| Evaluación de impacto. | Se analiza el efecto en tiempo, costo y calidad. | Líder de Proyecto. |
| Aprobación o rechazo. | Se decide si el cambio procede o no. | Líder \+ Calidad |
| Implementación. | Se realiza el cambio en una rama de Git y se documenta. | Desarrollador asignado. |
| Pruebas de regresión. | Se ejecutan pruebas para asegurar que el cambio no rompe funcionalidades previas. | Equipo de pruebas. |
| Liberación y cierre. | El cambio aprobado pasa a la rama principal, se documenta y se actualiza la tabla de versiones. | Responsable de calidad. |

## 

## **Estrategia de Ramas y Control de Versiones**

| Rama | Propósito | Quién la usa | Reglas de calidad |
| ----- | ----- | ----- | ----- |
| main | Contiene el código estable y en producción. | Líder de Proyecto / Calidad. | Solo se actualiza mediante *merge* desde *develop* tras pasar todas las pruebas y revisiones. |
| develop | Rama de integración de nuevas funcionalidades. | Todo el equipo de desarrollo. | Los cambios deben pasar revisión de código (pull request) y pruebas unitarias antes de fusionarse. |
| feature/\* | Una rama por cada funcionalidad o requisito del SRS. | Desarrolladores. | Nace desde *develop*, debe incluir pruebas unitarias y documentación mínima antes de integrarse. |
| hotfix/\* | Corrección urgente de errores críticos detectados en producción. | Desarrolladores / Calidad. | Nace desde *main*, se prueba y se integra tanto a *main* como a *develop*. |
| release/\* | Preparación de una nueva versión estable antes de pasar a *main* o *develop*. | Líder de Proyecto / Calidad. | Incluye pruebas de regresión, métricas de calidad y documentación de la versión. |

**Buenas prácticas adicionales:**

* Todo *commit* debe estar ligado a un requerimiento o incidencia.  
* Cada *commit* debe describir lo que cambia (“fix: error en validación de inventario”).  
* Un *commit* por cambio lógico.  
* *Pull Requests* obligatorios antes de fusionar a *develop* o *main*.  
* Se realizarán *code reviews* obligatorios antes de fusionar a *develop* o *main*.  
* Se etiquetarán (*tags*) las versiones liberadas siguiendo el esquema **vX.Y.Z**.

## **Estrategia de Métricas**

| Métricas | Fórmula | Frecuencia | Responsable | Umbral de aceptación |
| ----- | ----- | ----- | ----- | ----- |
| Densidad de defectos. | Defectos / LOC | Cada iteración. | Calidad. | ≤ 5 defectos/KLOC |
| Cobertura de pruebas. | Casos ejecutados / Casos totales | Cada entrega. | Calidad. | ≥ 95% |
| Retrabajo. | Horas de corrección / Horas totales | Mensual. | Jefe de proyecto. | ≤ 15% |
| Cumplimiento de entregas. | Entregas a tiempo / Total entregas | Cada hito. | Jefe de proyecto. | ≥ 90% |
| Defectos reabiertos. | Defectos reabiertos / Defectos corregidos | Mensual. | Calidad. | ≤ 10% |

## **Gestión de riesgos de calidad**

| Riesgos | Impacto | Mitigación |
| ----- | :---: | ----- |
| Fallos en seguridad. | Alto | Pruebas de penetración. |
| Retrasos por integración. | Medio | Integración continua. |
| Baja aceptación del usuario. | Bajo | Pruebas piloto con feedback. |
| Alta conexión a internet. | Alto | Optimizar para baja latencia, implementar caché local donde sea posible. |
| Fallas de compatibilidad en navegadores. | Medio | Pruebas cruzadas en distintos navegadores. |
| Pérdida de datos en el servidor. | Alto | Respaldos automáticos y replicación de BD. |
| Errores en reportes/gráficas. | Medio | Validación de cálculos y pruebas de regresión. |

## **Aprobación y Control**

Elaborado por: Cesar Gonzales, Luis Jimenez, Jose Bautista.

Revisado por: Omar Marcelino, Javier Machado.

Aprobado por: Ray Brunnet Parra Galaviz.

### **Versiones del documento**

| Version | Observaciones |
| ----- | ----- |
| 1.0 |  |

