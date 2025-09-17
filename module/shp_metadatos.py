#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Librerías para la gestión de metadatos propias 
# ObtenerMetadatosPrograma()
# ObtenerMetadatosPlataforma
# ObtenerMetadatosIpConexion()

import sys
import os 
import platform
import socket
import getpass
import netifaces as ni

# Datos del Programa, Nombre y directorio donde está
def ObtenerMetadatosPrograma():
    '''Devuelvo un diccionario de datos con el nombre del script que ejecuto 
    y sus parámetros'''
    nombre_programa = sys.argv[0]
    parametros = sys.argv[1:]
    ruta_programa = os.path.abspath(os.path.dirname(__file__)) # Esto no es lo que busco
    ruta_programa = os.getcwd()
    Nombre = {
        "RutaPrograma" : ruta_programa,
        "NombrePrograma" : nombre_programa,
        "ParametrosPrograma" : parametros
    }
    return Nombre

# Datos de la plataforma donde se ejecuta el programa    
def ObtenerNombreEquipo():
    '''
        Devuelvo el nombre del equipo donde se ejecuta
    '''
    nombre_equipo = socket.gethostname()
    return nombre_equipo

def ObtenerSistemaOperativo():
    '''Devuelvo el sistema operativo anitrión
    Windows, Darwin (para MAC), Linux
    '''
    return platform.system()

def ObtenerVersionSistemaOperativo():
    '''Devuelvo el nucleo de la version del sistema operativo
    Windows version, Darwin su nucleo, Linux su nucleo
    '''
    return platform.release()

def ObtenerUsuarioActual():
    sistema_operativo = platform.system()

    if sistema_operativo == "Windows":
        return getpass.getuser()
    elif sistema_operativo == "Darwin" or sistema_operativo == "Linux":
        return os.getenv('USER')
    else:
        return "Desconocido"

def ObtenerMetadatosPlataforma():
    '''Devuelvo un json con los datos donde ejecuto el programa'''
    MetadatosPrograma = {
        "SO" : ObtenerSistemaOperativo(),
        "Versión" : ObtenerVersionSistemaOperativo(),
        "Host" : ObtenerNombreEquipo(),
        "Usuario" : ObtenerUsuarioActual()
    }
    return MetadatosPrograma

# Datos de la configuración de red del equipo

def ObtenerDireccionIpLocal():
    ''' Obtengo la dirección local del equipo donde estoy ejecutando.
    Devuelvo una dirección Ip o nulo'''
    try:
        # Crea un socket para obtener la dirección IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Conecta a un servidor externo (en este caso, el servidor DNS de Google)
        direccion_ip_local = s.getsockname()[0]  # Obtiene la dirección IP local del socket
        s.close()
        return direccion_ip_local
    except socket.error as e:
        #print("Error al obtener la dirección IP local:", e)
        return None

def ObtencionGetMacAddress(interface):
    '''Dada una interfaz de red devuelvo si es posible la dirección MAC de la tarjeta
    '''
    try:
        addresses = ni.ifaddresses(interface)
        mac_address = addresses[ni.AF_LINK][0]['addr']
        return mac_address
    except ValueError:
        return None
    
def ObtencionGateway(interface):
    '''Dada una interfaz de red devuelvo si es posible la dirección puerta de enlace
    '''
    try:
        gateways = ni.gateways()
        return gateways['default'][ni.AF_INET][0]
    except KeyError:
        return None

def ObtenerMetadatosIpConexion():
    '''Obtengo la configuración de la interfaz que uso para la conexión.
    Devuelvo un diccionario con los datos relevantes de la configuración 
    Devuelvo un attributo error si he encontrado un error en el diccionario'''
    DireccionIP = ObtenerDireccionIpLocal()
    ConfiguracionIPLocal = {}    
    if DireccionIP is not None:
        try:
            interfaces = ni.interfaces()
            for interface in interfaces:
                if interface != 'lo':  # Excluimos la interfaz loopback (lo) que no es relevante para conexiones externas
                    addrs = ni.ifaddresses(interface)
                    if ni.AF_INET in addrs:
                        ip_info = addrs[ni.AF_INET][0]
                        if DireccionIP == ip_info['addr']:
                            ConfiguracionIPLocal['interface'] = interface
                            ConfiguracionIPLocal['MAC'] = ObtencionGetMacAddress(interface)
                            ConfiguracionIPLocal['direccion_ip'] = ip_info['addr']
                            ConfiguracionIPLocal['mascara_subred'] = ip_info['netmask']
                            ConfiguracionIPLocal['broadcast'] = ip_info.get('broadcast', 'No definido')
                            ConfiguracionIPLocal['gateway'] = ObtencionGateway(interface)
        except Exception as e:
            #print("Error al obtener la configuración IP de la conexión:", e)
            ConfiguracionIPLocal['error'] = e
    return ConfiguracionIPLocal
    
