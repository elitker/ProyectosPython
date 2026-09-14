from pathlib import Path

import eel

try:
    import screeninfo.screeninfo as si
except ImportError:
    si = None

try:
    import fFuncGM.funciones as FUNC
except ImportError:  # Permite ejecutar con: python -m GamesMaps.inicio
    from .fFuncGM import funciones as FUNC


class Inicio:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        eel.init(str(self.base_dir / "web"))
        __func = FUNC.Funciones()
        __listaFunciones = __func.funciones_to_eel()

        for _f in __listaFunciones:
            eel.expose(_f)


def obtener_tamano_ventana():
    """Calcula una ventana cómoda y usa valores seguros si no hay monitor disponible."""
    ancho_default = 1200
    alto_default = 800
    x_default = 80
    y_default = 40

    if si is None:
        return (ancho_default, alto_default), (x_default, y_default)

    try:
        monitores = si.get_monitors()
    except Exception:
        monitores = []

    if not monitores:
        return (ancho_default, alto_default), (x_default, y_default)

    pantalla = monitores[0]
    width = int(pantalla.width * (5 / 8))
    height = int(pantalla.height * (2 / 3))
    x = int(pantalla.width / 8)
    y = int(pantalla.height * (5 / 100))
    return (width, height), (x, y)


if __name__ == "__main__":
    __i = Inicio()
    __size, __position = obtener_tamano_ventana()
    eel.start("Layout.html", size=__size, position=__position)
