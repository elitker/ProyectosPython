import imaplib
from email.parser import HeaderParser
from datetime import datetime
import re
from progressbar import ProgressBar

"""
    Con este script, se buscan correos con una hora igual o mayor a la especificada. Ademas se le configura al script
    que muestre solo los correos de un destinatario en concreto.

    Script: "Buscar correo en Gmail por hora especifica"
    Autor: Elitker
"""


# --------------------------- #
# Conexion al imap de google #
# --------------------------- #
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login('[usuario]', '[contraseña]')
mail.select("inbox")

# -------------------------- #
# Traemos todos los correos #
# -------------------------- #

result, data = mail.search(None, "ALL")

ids = data[0]  # Obtenemos los IDs de los correos.

# Obtenemos una lista de los IDs de los correos
# que llegan separados por espacio
id_list = ids.split()

# para saber cuantos correos tengo en mi inbox (variable que usaremos en la barra de progreso)
totalIDs = len(id_list)

# Con una barra de progreso que me muestre como va transcurriendo el proceso
with ProgressBar(max_value=totalIDs) as progress:
    # Por cada id en id_kist
    for id_mail in id_list:
        # Traemos el correo
        result, data = mail.fetch(id_mail, "(BODY[HEADER])")

        #Lo Parseamos
        header_data = data[0][1]

        parser = HeaderParser()
        msg = parser.parsestr(header_data.decode('utf-8'))  # Obtenemos la cabecera del mensaje.

        # Tomamos la hora en que se recibio el correo
        recibido = msg["Date"]

        mientras = None
        intentos = 0
        while mientras is None:
            try:
                """
                    Se pueden recibir (en este caso) dos tipos de correos. Unos con horas internacionales y otras con horas nacionales.
                    Por esa razon, dependiendo de la hora del correo que se reciba, es la conversion que se realiza.
                    No se controla el caso de que haya mas opciones.
                """
                if intentos == 0:
                    convertido = datetime.strptime(recibido, "%a, %d %b %Y %H:%M:%S %z")  # Para correos con horas nacionales
                elif intentos == 1:
                    convertido = datetime.strptime(recibido, "%a, %d %b %Y %H:%M:%S %z (%Z)")  # Para correos con horas internacionales
                mientras = 1
                break
            except:
                mientras = None
                intentos += 1

        if intentos > 0:
            continue

        # Se elige de ejemplo la hora 13. La fecha elegida es para completar espacios,
        # ya que en este script se le da solo importancia a la hora.
        tiempo_elegido = datetime.strptime('2016-12-28 13:00:00', '%Y-%m-%d %H:%M:%S')

        m = re.search('<(\S*)>', msg['From'])  # Buscamos el destinatario del correo con expresiones regulares.

        if m:
            sender = m.group(1)
        else:
            raise Exception("No hay destinatario")

        if convertido.time() >= tiempo_elegido.time() and sender == '[destinatario]':
            # Si se encuentra un correo con la hora especificada o mayor
            # y con el destinatario escogido, muestra el asunto del mensaje.
            print(msg["Subject"])

        progress.update(int(id_mail))  # Actualizamos el progreso de la barra.
