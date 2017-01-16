import subprocess as sp

"""
Se utiliza este script para cambiar rapidamente entre configuraciones IP de la
placa de red Ethernet.
"""

# -------------------------------- #
# Primeramente declaramos las variables que voy a usar
# mas adelante.

ip = ""
subnetmask = ""
gateway = ""
dns = ""
numero = 0  # Variable util para retener el id de configuracion elegido

# --------------------------------- #
# --------------------------------- #
# Creo un diccionario en el donde definire las configuraciones
# que tengo. A medida que se vaya necesitando, se le agrega un
# nuevo par de valores (key, value) al diccionario.

Configuracion = {
    0: 'Automatico',
    1: 'Trabajo'
}

# --------------------------------- #
# --------------------------------- #
# Mostramos las configuraciones de las cuales disponemos.

print()
print("Configuraciones disponibles:")

for config, valor in Configuracion.items():
    print(config, valor)

# --------------------------------- #
# --------------------------------- #
# Le solicito al usuario del script, que ingrese el id
# de la configuracion que se desea implementar

print()
while True:
    try:
        elegido = input("Seleccione la configuracion deseada: ")
        elegido = int(elegido)
        numero = elegido
        break
    except:
        print("Valor incorrecto.")
        print()
for config, valor in Configuracion.items():
    if config == elegido:
        elegido = valor

# --------------------------------- #
# --------------------------------- #
# Declaro en un diccionario las configuraciones que poseeo

dConfiguraciones = {
    'Automatico': {
        'IP': '',
        'Subnetmask': '',
        'Gateway': '',
        'DNS': ''
    },
    'Trabajo': {
        'IP': '192.168.XXX.XXX',
        'Subnetmask': 'XXX.XXX.XXX.XXX',
        'Gateway': '192.168.XXX.XXX',
        'DNS': 'XXX.XXX.XXX.XXX'
    }
}

# --------------------------------- #
# --------------------------------- #
# Retorno el diccionario segun el id de configuracion
# elegido por el usuario del script.
# Le asigno a las variables declaradas al principio, cada uno de
# los valores que llevaran para configurar la placa de red.

elegido = dConfiguraciones[elegido]

ip = elegido['IP']
subnetmask = elegido['Subnetmask']
gateway = elegido['Gateway']
dns = elegido['DNS']

# --------------------------------- #
# --------------------------------- #
# Con todos los datos a disposicion ejecutamos los comandos necesarios para
# realizar la configuracion de la placa segun la configuracion elegida.

if numero == 0:
    comandoIP = 'netsh interface ipv4 set address name="Conexión de área local" source=dhcp'
    comandoDNS = 'netsh interface ipv4 set dnsservers "Conexión de área local" dhcp'
    proceso1 = sp.Popen(comandoIP)
    resultado1 = proceso1.wait()
    proceso2 = sp.Popen(comandoDNS)
    resultado2 = proceso2.wait()
else:
    comandoIP = 'netsh interface ipv4 set address name="Conexión de área local" static {ip} {sub} {gate}'.format(
        ip=ip,
        sub=subnetmask,
        gate=gateway
    )
    comandoDNS = 'netsh interface ipv4 set dnsservers "Conexión de área local" static {dns} primary'.format(
        dns=dns
    )
    proceso1 = sp.Popen(comandoIP)
    resultado1 = proceso1.wait()
    proceso2 = sp.Popen(comandoDNS)
    resultado2 = proceso2.wait()

print("Fin")

"""
Script: Configuracion IP de la placa de red Ethernet.
Autor: Elitker
"""
