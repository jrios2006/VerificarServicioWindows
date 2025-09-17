#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Librerías propias para el registro 
# InicializoDatosLog()

from module.shp_uuid import ObtengoIDInstanciaLog
from module.shp_metadatos import ObtenerMetadatosIpConexion, ObtenerMetadatosPrograma, ObtenerMetadatosPlataforma 

def InicializoDatosLog():
    '''
    Inicializo un diccionario de datos para trazar el log con los datos básicos
     Datos de Ejecutable
     Datos del sistema operativo
     Datos de la conexión de red
     Instancia
     Tipo de mensaje
    Depende de como hayamos definido la tabla de Log (Log_Scripts)
    '''

    DatosLog = {
        "instancia" : ObtengoIDInstanciaLog(),
        "resultado" : "Ejecuntadose",
        "tipo_mensaje" : "INFO",
        "parametros" : {
            "Programa" : ObtenerMetadatosPrograma(),
            "Sistema" : ObtenerMetadatosPlataforma(),
            "Red" : ObtenerMetadatosIpConexion()
        },
        "nombre_script" : ObtenerMetadatosPrograma()['NombrePrograma']

    }
    return DatosLog

