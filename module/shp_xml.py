#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Librerías propias para operaciones con ficheros XML


import logging

import xml.etree.ElementTree as ET
import os

def EncontrarEnlaceXSD(xml_file_path):
    '''Dado un fichero XML intento encontrar el enlace 
    xsd declarado en el mismo y vacio si no encuentro lo que busco
    '''
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Encontrar el atributo "schemaLocation" en el espacio de nombres xsi
    xsi_namespace = 'http://www.w3.org/2001/XMLSchema-instance'
    schema_location = root.attrib.get('{%s}schemaLocation' % xsi_namespace)

    if schema_location:
        xsd_url = schema_location.split()[1]  # Obtener la segunda parte (URL)
        #print(f"URL del archivo XSD: {xsd_url}")
    else:
        #print("No se encontró ningún atributo 'schemaLocation' en el archivo XML.")
        xsd_url=""
    return xsd_url