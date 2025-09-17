#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	Librerí­a para enví­o de correo
#   ValidarSintaxisEmail(email)
#	EnviarCorreo(credenciales, destinatario, archivo, asunto, mensaje)

import logging # para guardar un log
def ValidarSintaxisEmail(email):
    '''
        Validamos sintácticamente el mail, si es válida devolve True
        Si no es correcta devolvemos false
    '''
    import re
    Aux = False
    addressToVerify ='info@emailhippo.com'
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', \
                     email)
    if match == None:
	    #print('Bad Syntax: ' + email )
        A = 0
    else:
        Aux = True
    return Aux

def EnviarCorreoSSL(credenciales, destinatario, asunto, mensaje, archivo, CopiaOculta=True):
    '''
        Envío un correo electrónico con las credenciales de un usuario
        usando un servicio SMTP que le paso en la variable credenciales, a un destinatario
        con un asunto y un mensaje. Si existe el fichero archivo en el sistema lo adjunta.
        Devuelvo si lo he conseguido enviar o no.
        Si le paso el parámetro CopiaOculta a la función enviará con copia oculta al remitente 
        una copia del mensaje
        Ojo que parece que alguno servidores no atienden a enciar con copia y a enviar con copia oculta
    '''

    import smtplib
    import ssl
    import os

    # importamos librerias  para construir el mensaje
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    #importamos librerias para adjuntar
    #from email.MIMEBase import MIMEBase
    from email.mime.base import MIMEBase
    from email import encoders 
    from email.encoders import encode_base64    

    Aux = False # Variable que contiene el estado del enví­o
    Errores = {}
    # Obtenemos las credenciales de envío del correo
    # [remitente, smtp_server, smtp_port, smtp_user, smtp_pass]
    remitente = credenciales[0]
    smtp_server = credenciales[1]
    smtp_port = credenciales[2]
    smtp_user = credenciales[3]
    smtp_pass = credenciales[4]
    
    context = ssl.create_default_context()
    Conectado = False
    Cadena = ''
    #Generamos el objeto del mensaje
    header = MIMEMultipart()
    header['Subject'] = asunto
    header['From'] = remitente
    header['To'] = destinatario
    if CopiaOculta:
        header['Bcc'] = remitente
    # Componemos el mensaje
    mensaje = MIMEText(mensaje, 'html') #Content-type:text/html
    header.attach(mensaje)
    if (os.path.isfile(archivo)):
        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(open(archivo, "rb").read())
        encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(archivo))
        header.attach(adjunto)    
    #Intentamos hacer la conexión con el servidor de correo
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as servidor_correo:
            servidor_correo.login(smtp_user, smtp_pass)
            #servidor_correo.set_debuglevel(2)  # Habilitar el nivel de depuración  
            servidor_correo.sendmail(remitente, destinatario, header.as_string())
        Aux = True
    except smtplib.SMTPAuthenticationError:
        Cadena = 'La contraseña del usuario de correo ' + smtp_user + ' no es correcta en el servidor ' + smtp_server
    except smtplib.SMTPException as e:
        Cadena = 'Ha ocurrido una exepción con el usuario de correo ' + smtp_user + ' y el servidor ' + smtp_server
        logging.error(e)
    except smtplib.SMTPSenderRefused:
        Cadena = 'El remitente de correo ' + remitente + ' no puede enviar un mail con el usuario ' + smtp_user + ' y el servidor ' + smtp_server
    except smtplib.SMTPDataError:
        Cadena = 'Se ha producido un error con el usuario ' + smtp_user + ' y el servidor ' + smtp_server + '. No se puede enviar el mail'
    except smtplib.SMTPRecipientsRefused:
        Cadena = 'No es posible enviar un correo al destinatario del correo ' + destinatario + ' a través del servidor ' + smtp_server + ' con el usuario ' + smtp_user
    if (Cadena != ''):
        Errores['Error'] = Cadena
        logging.error(Cadena)
        Cadena = ''
    else:
        Cadena = 'Correo enviado a ' + destinatario + ' a través del servidor ' + smtp_server + ' con asunto ' + asunto
        logging.info(Cadena)
        Errores['Mensaje'] = Cadena          
    return Aux, Errores

