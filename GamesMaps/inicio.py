import eel
import screeninfo.screeninfo as si
import fFuncGM.funciones as FUNC


class Inicio:
    def __init__(self):
        eel.init('web')
        __func = FUNC.Funciones()
        __listaFunciones = __func.funciones_to_eel()

        for _f in __listaFunciones:
            eel.expose(_f)


if __name__ == "__main__":
    __i = Inicio()
    __screen = si.get_monitors()[0]
    # 1920 - 1080 // 960 - 540
    __width = (__screen.width * (5/8))
    __height = (__screen.height * (2/3))
    __x = (__screen.width / 8)
    __y = (__screen.height * (5/100))
    
    eel.start('Layout.html', size=(__width, __height), position=(__x, __y))