# Verificar Servicio Windows con acceso a Oracle

Este proyecto está diseñado para **monitorizar y reiniciar automáticamente un servicio en Windows** cuando deja de funcionar con normalidad.  
El servicio monitorizado realiza consultas a una base de datos Oracle; si deja de ejecutar consultas durante un tiempo prolongado, el script lo reinicia.  

Además, se registran los reinicios en un log y opcionalmente se puede enviar un correo de alerta.

---

## 📂 Estructura del proyecto

- LogReiniciosServicio.log  
- main.py  
- config/  
  - config.json  
  - credenciales.json  
  - known_hosts  
- log/  
- module/  
  - shp_bbdd.py       # Conexión y consultas a Oracle
  - shp_correo.py     # Envío de alertas por correo
  - shp_exe.py  
  - shp_ficheros.py  
  - shp_log.py  
  - shp_metadatos.py  
  - shp_servicios.py  # Control de servicios Windows
  - shp_sftp.py  
  - shp_uuid.py  
  - shp_varios.py  
  - shp_xml.py  
  - shp_zip.py  

---

 ⚙️ Configuración

El archivo principal de configuración es [`config/config.json`](config/config.json).  
Ejemplo:

```json
{
    "FicheroCredenciales" : "config/credenciales.json",
    "FicheroReinicios" : "log_reinicio.txt",

    "sqlInstancias" : "SELECT INST_ID, HOST_NAME, INSTANCE_NAME, STATUS FROM GV$INSTANCE;",

    "programa_servicio" : "NOMBRESERVICIO.exe",
    "esquema_base_de_datos" :  "ESQUEMA_BBDD",    
    "sql" : "SELECT NVL( (SYSDATE - MAX(LAST_ACTIVE_TIME) ) * 24 * 60 * 60, 61) AS diferencia_segundos FROM V$SQLAREA T WHERE PARSING_SCHEMA_NAME='%%ESQUEMABASEDATOS%%' AND MODULE = '%%PROGRAMASERVICIO%%' ORDER BY T.LAST_ACTIVE_TIME DESC;",

    "nombre_servicio" : "NOMBRESERVICIO",
    "ComenarioLog" : "Cambiar el atributo BorrarLog a false si no queremos borrar el log y a true si no queremos el log que va ganerando su programa",
    "BorrarLog" : true,

    "AlertaCorreo" : {
        "destinatario" : "it@dominio.com",
        "asunto" : "Se ha reiniciado el servicio %%NOMBRESERVICIO%% en la máquina %%SERVIDORCLIENTE%%",
        "cuerpo" : "<p>Se adjunta el fichero de reinicios de la máquina. Revisar el porqué se ha reiniciado.</p><br>Adfunto los datos de la máquina donde se ejecuta<br>"
    },
    "EnviarCorreo" : false
}

## ⚙️ ConfiguraciónCampos principales:

* programa_servicio → ejecutable del servicio a monitorizar.

* nombre_servicio → nombre del servicio en Windows.

* sql / sqlInstancias → consultas de validación contra Oracle.

* BorrarLog → controla si se limpia el log en cada ejecución.

* EnviarCorreo → habilita o deshabilita el envío de correos de alerta.

* AlertaCorreo → plantilla de correo en caso de reinicio.

## 📦Instalación de dependencias
Ejecutar en la raíz del proyecto:
```bash
pip install -r requirements.txt
```

##▶️ Ejecución

### Requisitos previos

* Python 3.9+
* Acceso a Oracle (con cx_Oracle instalado).
* Ejecución en Windows con permisos de Administrador

### Ejecutar el script

```bash
# Abrir PowerShell como Administrador
python main.py
```

## Lógica

* Comprueba si el servicio está corriendo.
* Verifica si sigue interactuando con Oracle.
* Si no hay actividad, reinicia el servicio.
* Registra el evento en LogReiniciosServicio.log.
* (Opcional) Envía un correo de alerta.

## Despliegue en Windows

* Copiar la carpeta completa en el servidor donde debe ejecutarse.
* Configurar config/config.json y credenciales.json.
* Probar la ejecución manual del script.
* (Opcional) Configurar una tarea programada de Windows para que se ejecute de forma periódica:
    * Abrir Task Scheduler
    * Crear tarea nueva → Ejecutar con permisos de administrador
    * Configurar disparador (cada X minutos)

    * Acción:
    ```bash
    python C:\Apps\VerificarServicio\main.py
    ```

## 📝 Logs

* LogReiniciosServicio.log → registro general de ejecución.
* log_reinicio.txt (definido en config) → historial de reinicios.

## 📧 Notificaciones por correo

Si EnviarCorreo = true en el config.json, cada reinicio genera un correo de aviso.
El mensaje se basa en la plantilla configurada en el bloque AlertaCorreo.