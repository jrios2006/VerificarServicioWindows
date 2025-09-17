#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Verifico si un servicio en una máquina local está activo y compruebo que este 
# servicio no está consultando a la base de datos
# SI se cumple esto, Reinicio el servicio y lo anoto en un log para saber cuando 
# se ha reinicio la máquina. Es posible que me envíe un correo de alerta.

# Parametriar el fichero de credenciales con el acceso a la base de datos
# Parametrizar el fichero config.json y revisar los siguientes atributos:
# "BorrarLog" : true -- Para borrar la traza del log False si no lo queremos borrar. Ojo con los ficheros que se generan
# "programa_servicio" : "LugHL7GwAnlzSvc.exe" -- poner el programa que queremos revisar el cual escribe en Oracle
# "esquema_base_de_datos" :  "ACVH_M" -- Poner el que toca analizar
# "nombre_servicio" : "Zoom Sharing Service" -- Poner como se identifica el servicio en la máquina
# "destinatario" : "jrios@safetyhp.com" -- Cambiar el correo del destinatario

# Al final esta carpeta debe de contener un fichero "FicheroReinicios" : "log_reinicio.txt" que contendrá cunado ha ocurrido
# Es necesario ejecutar en una tarea administrativa com permisos suficientes.
# Activar el log y probar el reinicio y verificar que la máquina reinicia biene el servicio
# Junio 2024

# Librerías de uso
import datetime
import json
import logging
from time import time  # Para calcular tiempo de ejecución del programa
from module.shp_ficheros import BorrarFichero
from module.shp_log import InicializoDatosLog
from module.shp_correo import EnviarCorreoSSL
from module.shp_bbdd import ObtenerDatos_Oracle_enJSON
from module.shp_servicios import listar_servicios_locales, reiniciar_servicio_local
from module.shp_varios import add_fecha_archivo, generar_tabla_html

def main(args):
    DataLogInicial = InicializoDatosLog() # Es un diccionario que voy a utilizar para ir generando Logs
    FechaInicial = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    FicheroLog = FechaInicial + ".log" # Nombre del log
    HoraInicial = time() # Para calcular timepo de ejecución y cuando tardamos en procesar todo el proceso
    try:
        with open('config/config.json', encoding='utf-8') as fichero_inicial:
            ParametrosIniciales = json.load(fichero_inicial)
        # Cargo el fichero de credenciales
        with open(ParametrosIniciales["FicheroCredenciales"], encoding='utf-8') as fichero_credenciales:
            Credenciales = json.load(fichero_credenciales)
    except:
        ParametrosIniciales = {}
        Credenciales = {}
    if ParametrosIniciales or Credenciales:
        # Empizo a poner lo necesario para lanzar el proceso
        logging.basicConfig(handlers=[logging.FileHandler(filename='log/' + FicheroLog, encoding='utf-8', mode='w')],
                            level=logging.INFO,
                            format='%(asctime)s : %(levelname)s : %(message)s',)
        
        logging.info("Comienza el proceso de verificación de servicios")
        logging.info(DataLogInicial)

        logging.info("Consulto los nodos de la base de datos por si hubiera más de uno")
        # Obtenemos la lista instancias donde ejecutar la senetencia sql
        resultado, datos = ObtenerDatos_Oracle_enJSON(credenciales=Credenciales['BBDD'], sql=ParametrosIniciales['sqlInstancias'])
        if resultado:
            # Tengo datos y la BBDD está correctamete configurada
            # datos = [{'INST_ID': 1, 'HOST_NAME': 'LUGHTESMADSER03', 'INSTANCE_NAME': 'lught', 'STATUS': 'OPEN'}]
            ListaSegundos = [] #Guarda cada consulta que voy a hacer en tiempos 
            for instancia in datos:
                NombreInstancia = instancia['HOST_NAME']
                logging.info(f'Ejecuto sobre lainstancia {NombreInstancia }')
                CredencialesInstancia = Credenciales['BBDD'] # Copio la lista original a otra variable
                CredencialesInstancia[0] = instancia['HOST_NAME'] # Cambio para hacer una consulta SQL
                # Ejecuto la consulta SQL
                sql = ParametrosIniciales['sql'].replace("%%ESQUEMABASEDATOS%%", ParametrosIniciales['esquema_base_de_datos'])
                sql = sql.replace("%%PROGRAMASERVICIO%%", ParametrosIniciales['programa_servicio'])
                logging.info(sql)
                resultadoInstancia, datosInstancia = ObtenerDatos_Oracle_enJSON(credenciales=CredencialesInstancia, sql=sql)
                if resultadoInstancia:
                    ListaSegundos.append(datosInstancia[0]['DIFERENCIA_SEGUNDOS'])
                    logging.info(ListaSegundos)
            TiempoHaceUltimaConsulta = min(ListaSegundos)
            logging.info(f"El último timepo es de {TiempoHaceUltimaConsulta}")
            # Compruebo la lista de servicios locales de la máquina
            servicios = listar_servicios_locales()
            logging.info(servicios)

            # Verificamos que el servicio corre en esta máquina
            ExisteServicio = False
            DatosServicio = {}
            for servicio in servicios:
                if ParametrosIniciales['nombre_servicio'] in servicio['DisplayName']:
                    ExisteServicio = True
                    DatosServicio = servicio
                    logging.info(f"Encontrado el servicio corriendo cone el nombre {servicio['DisplayName']}")
            if not ExisteServicio:
                logging.warning(f"No he encontrado el servicio corriendo cone el nombre {ParametrosIniciales['nombre_servicio']} verifica el fichero config con el nombre a buscar")
            else:
                # El servicio existe
                EstadoActual = DatosServicio['Status']
                if EstadoActual == 4: # 4 en ejecución
                    if TiempoHaceUltimaConsulta > 60: #Hace más de un minutos que no ha consultas
                        # Debo de reiniciar le servicio
                        #Es necesario una consola con permisos de administrador y además Powershell para automatizar esto que se ejecute cada 5 minutos
                        resultado_reinicio = reiniciar_servicio_local(nombre_servicio=ParametrosIniciales['nombre_servicio']) 
                        # Guardo en un fichero de texto la hora de reinicio
                        add_fecha_archivo(nombre_fichero=ParametrosIniciales['FicheroReinicios'])
                        # Envío un correo electrónico
                        Asunto = ParametrosIniciales['AlertaCorreo']['asunto'].replace('%%NOMBRESERVICIO%%', ParametrosIniciales['nombre_servicio'])
                        Asunto = Asunto.replace('%%SERVIDORCLIENTE%%', DataLogInicial['parametros']['Sistema']['Host'])
                        Mensaje = ParametrosIniciales['AlertaCorreo']['cuerpo'] + str(DataLogInicial)
                        # Añado el contenido de un fichero de texto 
                        Mensaje = Mensaje + generar_tabla_html(ParametrosIniciales['FicheroReinicios'])
                        if ParametrosIniciales['EnviarCorreo']:
                            EnviarCorreoSSL(credenciales=Credenciales['CORREO'], destinatario=ParametrosIniciales['AlertaCorreo']['destinatario'],
                                            asunto=Asunto, mensaje=Mensaje, 
                                            archivo='log/' + FicheroLog)
                    else:
                        logging.info(f"El servicio con el nombre {ParametrosIniciales['nombre_servicio']} tiempo un timepo {TiempoHaceUltimaConsulta} y no hace falta hacer nada")    
                else:
                    logging.warning(f"El servicio con el nombre {ParametrosIniciales['nombre_servicio']} NO está corriendo y no pienso levantarlo")
        else:
            logging.error(f"Las credencicales {Credenciales['BBDD']} no son válidas. No puedo hacer el proceso.")
        HoraFinal = time()
        TiempoTranscurrido = HoraFinal - HoraInicial
        # Formatea el tiempo transcurrido en horas, minutos y segundos
        horas, segundos = divmod(int(TiempoTranscurrido), 3600)
        minutos, segundos = divmod(segundos, 60)
        # Crea una cadena formateada
        tiempo_formateado = f'{horas} horas, {minutos} minutos y {segundos} segundos'
        # Agrega la información al registro
        logging.info(f'Tiempo empleado: {tiempo_formateado}')        
        logging.shutdown()
        # Borro el log para no generar mierda
        if ParametrosIniciales['BorrarLog']:
            BorrarFichero(archivo='log/' + FicheroLog, log=False)
    else:
        print('Verifica la estructura de los ficheros de configuración, que hay problemas en cargarlos')
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))