# Librería para gestionar servicios, listarlo, pararlos arrancarlos , ...

import subprocess
import json
import logging

def servicio_existe(nombre_servicio):
    '''Verifica si un servicio con el nombre especificado existe en la lista de servicios locales'''
    servicios = listar_servicios_locales()
    for servicio in servicios:
        if servicio.get('DisplayName') == nombre_servicio:
            return True
    return False

def listar_servicios_locales():
    '''Dado una máquina windows local, devolvemos la lista de servicios que se ejecutan en dicha máquina
    Vacío si hay error, Ejemplo el usuario no tiene acceso. Es necesario poder ejecutar powershell
    La estructura que devulevo será de este estilo
    {
        'DisplayName': 'Servicio de protocolo de t£nel de sockets seguros', 
        'Status': 4, 
        'StartType': 3, 
        'ServiceType': 48, 
        'DependentServices': ['System.ServiceProcess.ServiceController', 'System.ServiceProcess.ServiceController']
    }

    Para interpretar los códigos de Status, StartType y ServiceType en la salida de los servicios listados en Windows, puedes usar las siguientes tablas de referencia:
    Status (Estado del servicio):
        1: Stopped (El servicio está detenido. No está en ejecución).
        2: StartPending (El sistema está en proceso de iniciar el servicio).
        3: StopPending (El sistema está en proceso de detener el servicio).
        4: Running (El servicio está en ejecución. Está activo y funcionando).
        5: ContinuePending (El sistema está en proceso de continuar un servicio que se ha pausado).
        6: PausePending (El sistema está en proceso de pausar un servicio que está en ejecución).
        7: Paused (El servicio está en pausa).

    StartType (Tipo de inicio del servicio):
    2: Automatic (El servicio se inicia automáticamente al arrancar el sistema operativo).
    3: Manual (El servicio no se inicia automáticamente al arrancar, pero puede iniciarse manualmente).
    4: Disabled (El servicio está deshabilitado y no se iniciará automáticamente ni manualmente).

    ServiceType (Tipo de servicio):

    1: SERVICE_KERNEL_DRIVER (El servicio es un controlador de kernel).
    2: SERVICE_FILE_SYSTEM_DRIVER (El servicio es un controlador de sistema de archivos).
    16: SERVICE_WIN32_OWN_PROCESS (El servicio se ejecuta en su propio proceso. Cada servicio que tenga este bit establecido es un proceso independiente).
    32: SERVICE_WIN32_SHARE_PROCESS (El servicio comparte un proceso con otros servicios).
    256: SERVICE_INTERACTIVE_PROCESS (El servicio puede interactuar con el escritorio, lo que significa que puede mostrar una interfaz de usuario).
    272: SERVICE_WIN32_OWN_PROCESS + SERVICE_INTERACTIVE_PROCESS (El servicio es un proceso independiente y puede interactuar con el escritorio).
    288: SERVICE_WIN32_SHARE_PROCESS + SERVICE_INTERACTIVE_PROCESS (El servicio comparte un proceso con otros servicios y puede interactuar con el escritorio).    
    '''
    try:
        # Comando de PowerShell para obtener información sobre servicios y convertir a JSON
        comando_powershell = '''
        Get-Service | Select-Object DisplayName, Status, StartType, ServiceType, DependentServices | ConvertTo-Json -Compress
        '''
        # Ejecutar el comando en la máquina local
        resultado = subprocess.run(["powershell", "-Command", comando_powershell], capture_output=True, text=True)
        if resultado.returncode != 0:
            raise Exception(f"Error en el comando de PowerShell: {resultado.stderr}")
        # Cargar la salida JSON
        servicios = json.loads(resultado.stdout)
        return servicios
    except Exception as e:
        logging.error(f"Error al obtener servicios locales: {e}")
        return []

def reiniciar_servicio_local(nombre_servicio):
    '''Dado un nombre de servicio obtenemos su reinicio. Devolvemos true si lo reiniciamos, false en otro caso'''
    Aux = False
    try:
        # Comando de PowerShell para reiniciar un servicio
        comando_powershell = f'Restart-Service -Name "{nombre_servicio}"'
        # Ejecutar el comando en la máquina local
        resultado = subprocess.run(["powershell", "-Command", comando_powershell], capture_output=True, text=True)
        Aux = True
        if resultado.returncode != 0:
            raise Exception(f"Error en el comando de PowerShell: {resultado.stderr}")
        logging.info(f"Servicio {nombre_servicio} reiniciado correctamente.")
    except Exception as e:
        logging.error(f"Error al reiniciar el servicio: {e}")
    return Aux

def filtrar_y_ordenar_servicios(servicios, estado_servicio = 4):
    '''
    Dada una lista de servicios devuelvo otra lista con los que quiera por defecto en el campo Status
    Estado del servicio tiene estos valores
        1: Stopped (El servicio está detenido. No está en ejecución).
        2: StartPending (El sistema está en proceso de iniciar el servicio).
        3: StopPending (El sistema está en proceso de detener el servicio).
        4: Running (El servicio está en ejecución. Está activo y funcionando).
        5: ContinuePending (El sistema está en proceso de continuar un servicio que se ha pausado).
        6: PausePending (El sistema está en proceso de pausar un servicio que está en ejecución).
        7: Paused (El servicio está en pausa).    
    '''
    # Filtrar servicios que están corriendo (Status: 4)
    servicios_corriendo = [servicio for servicio in servicios if servicio['Status'] == estado_servicio]
    
    # Ordenar la lista de servicios corriendo por el nombre para una mejor legibilidad
    servicios_corriendo_ordenados = sorted(servicios_corriendo, key=lambda x: x['DisplayName'])
    
    return servicios_corriendo_ordenados

def estado_servicio(nombre_servicio):
    '''Devuelve el estado del servicio con el nombre especificado, o 0 si no existe'''
    servicios = listar_servicios_locales()
    for servicio in servicios:
        if servicio.get('DisplayName') == nombre_servicio:
            return servicio.get('Status', 0)
    return 0

