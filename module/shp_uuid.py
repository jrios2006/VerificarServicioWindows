#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Librerías propias para la gestión de uuid
# ObtengoIDInstanciaLog()
# ObtenerFechaCreacionUUID(uuid_string):

import uuid
import datetime

def ObtengoIDInstanciaLog():
    '''Obtengo un UUID único para la ejecución de la aplicación.
        Devuelvo algo del estilo: a86fe112-32fe-11ee-97ba-94de80d761c4
        Es una cadena de 36 bytes
    '''
    return str(uuid.uuid1())

def ObtenerFechaCreacionUUID(uuid_string):
    '''Dado un UUID de tipo 1 en formato string devuelvo la fecha en que se generó en formato fecha'''
    uuid_obj = uuid.UUID(uuid_string)
    timestamp = (uuid_obj.time - 0x01b21dd213814000) / 10000000  # Convert 100ns to seconds
    timestamp_datetime = datetime.datetime.fromtimestamp(timestamp)
    return timestamp_datetime

