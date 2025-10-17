# **Especificación de Requerimientos de Software (SRS)**

## Proyecto: Sistema de Distribución Comunitario

## **1\. Introducción**

### **1.1 Propósito**

El propósito de este proyecto es desarrollar una plataforma que permita agilizar y facilitar la donación masiva de recursos a comunidades vulnerables a través de la implementación de sistemas digitales para automatizar, simplificar y optimizar operaciones de recolección, contacto y entrega.

### **1.2 Alcance**

El sistema permitirá:

* Registrar usuarios de distintos tipos (donadores, donatarios, instituciones, administradores).  
* Realizar solicitudes de recursos.  
* Realizar campañas de donación masiva.  
* Realizar donaciones.  
* Registrar alimentos recibidos y entregados.  
* Registrar almacenes (Administradores).  
* Gestionar inventario individual de cada almacen.  
* Generar gráficas  con la información de operaciones recolectada.  
* Realizar reportes o denuncias de usuarios y publicaciones.

### **1.3 Definiciones**

* **Donador o Donante:** Persona u organización que entrega recursos, bienes o dinero de manera voluntaria.  
* **Donatario:** Persona u organización que recibe una donación.  
* **Aplicación Web:** Programa accesible mediante un navegador, que funciona en internet sin necesidad de instalación local.  
* **Automatización:** Proceso de realizar tareas de forma automática mediante tecnología, reduciendo la intervención humana.  
* **Responsividad:**  Capacidad de una aplicación o sitio web para adaptarse correctamente a diferentes tamaños de pantalla y dispositivos.

## **2\. Descripción General**

### **2.1 Perspectiva del Producto**

El sistema será una aplicación web accesible desde navegadores con diseño responsivo adaptado a diferentes pantallas. Busca facilitar y promover la participación ciudadana en los programas de donación masiva proporcionando una vía directa, segura y transparente que beneficia a los más necesitados.

Su principal objetivo es digitalizar y optimizar la gestión de donaciones, brindando una herramienta confiable que facilite la interacción entre donadores, instituciones y administradores.

El sistema se diseñará como una plataforma centralizada que integrará en un mismo lugar las funciones de control de inventario, donaciones, administración, registro y comunicación, evitando los procesos manuales y reduciendo riesgos de pérdida de información o fraudes.

**2.2 Funciones del Sistema**

* Registro de usuarios con roles y permisos.  
* Solicitud de recursos por parte de donatarios e instituciones.  
* Realizar donaciones por parte de donadores e instituciones.  
* Gestionar almacenes y sus inventarios.  
* Recolectar datos de operaciones y mostrarlos en reportes y gráficas.  
* Gestionar y moderar contenido para evitar usos fraudulentos.

### **2.3 Características de los Usuarios**

* **Administrador:** controla inventario, modera contenido, atiende denuncias, registra almacenes.  
* **Donador:** Puede realizar donaciones en las solicitudes de recursos.  
* **Donatario:** Puede realizar solicitudes de donaciones.  
* **Institución:** Puede realizar solicitudes de donaciones masivas y también hacer donaciones masivas. 

### **2.4 Restricciones**

* El sistema no implementará algoritmos de verificación y credibilidad de las instituciones o voluntarios.  
* El sistema no contará con versión móvil o de escritorio.  
* El usuario no podrá solicitar, aceptar o realizar donaciones si no tiene una sesión activa.  
* El sistema no verificará los correos electrónicos usados para el registro de usuarios.  
* El sistema no contará con métricas avanzadas con análisis de datos, únicamente se presentará información básica sobre las operaciones realizadas.  
* El sistema no funcionará sin acceso a internet.  
* El sistema no contará con opciones de accesibilidad.  
* El sistema no priorizará la optimización en la transferencia de datos para conexiones lentas.

## **3\. Requisitos Específicos**

### **3.1 Requisitos Funcionales**

1. Implementar vistas modernas donde se muestren las solicitudes de donaciones, donaciones masivas y publicaciones.  
2. Implementar un motor de búsqueda para encontrar solicitudes de donación, donaciones masivas y publicaciones.  
3. Implementar el sistema de creación, edición, eliminación y visualización de donaciones.  
4. Implementar el sistema de creación, edición, eliminación y visualización de las solicitudes de donaciones.  
5. Implementar el sistema de creación, edición, eliminación y visualización de usuarios distinguiendo entre administradores, donadores, donatarios e instituciones.  
6. Implementar el sistema de creación, edición, eliminación, visualización y gestión de almacenes  
7. Implementar el sistema de gráficas para desglose de información.  
8. Implementar el sistema de incidencias o denuncias.

### **3.2 Requisitos No Funcionales**

1. La interfaz del sistema se mostrará en español   
2. Las contraseñas de los usuarios serán almacenadas con métodos de encriptación.  
3. El sistema implementará un sistema de privilegios para proteger la información.  
4. El sistema será transparente con el historial de actividades de los usuarios.  
5. El sistema estará optimizado para los navegadores web más populares y para dispositivos de bajo rendimiento.

## **4\. Requisitos de Implementación**

* **Frontend:** HTML, CSS, JavaScript.  
* **Backend:** Python.  
* **Base de Datos:** PostgreSQL.  
* **Hosting:** Servidor local para desarrollo y demo en nube para presentación  
* **Frameworks:** React, Django, TailwindCSS.

## **5.Tabla de control de versiones**

| No. Versión | Fecha | Observaciones |
| :---- | :---- | :---- |
| 1.0 | 02/09/2025 | Agregar más diagramas, revisar restricciones, añadir tabla de control de versiones y tabla de autorización |
