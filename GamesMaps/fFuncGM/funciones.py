import sqlite3 as sq3
import fFuncGM.func_mapa as FM

class Funciones:
    def __init__(self):
        __pathDBlite = r'GamesMapsV2.db'
        __con = sq3.connect(__pathDBlite)
        __con.row_factory = sq3.Row

        self.__con = __con

        __cur = __con.cursor()

        __cur.execute("CREATE TABLE IF NOT EXISTS TBL_JUEGOS "
                        "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "NOMBRE_JUEGO TEXT NOT NULL, "
                        "RUTA TEXT NOT NULL, "
                        "RUTA_ICONOS TEXT NULL "
                        ");")

        __cur.execute("CREATE TABLE IF NOT EXISTS TBL_ICONS "
                        "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "NOMBRE_ICONO TEXT NOT NULL, "
                        "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID), "
                        "RUTA_ICONO TEXT NOT NULL, "
                        "DIMENSIONES TEXT NOT NULL DEFAULT ('30,30') "
                        ");")

        __cur.execute("CREATE TABLE IF NOT EXISTS TR_POINTS "
                        "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID), "
                        "IconoID INTEGER REFERENCES TBL_ICONS (ID), "
                        "Coords TEXT NOT NULL, "
                        "VISITED INTEGER NOT NULL DEFAULT (0), "
                        "Descripcion TEXT NULL"
                        ");")
        
        __cur.execute("CREATE TABLE IF NOT EXISTS TBL_MAPS "
                        "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                        "NOMBRE_MAPA TEXT NOT NULL, "
                        "RUTA_MAPA TEXT NOT NULL, "
                        "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID) "
                        ");")

        __con.commit()

    def funciones_to_eel(self):
            _fm = FM.Iniciar(self.__con)

            return [
                 self.obtener_juegos,
                 self.cargar_juegos,
                 _fm.juego_seleccionado,
                 _fm.mapa_seleccionado,
                 _fm.cargar_mapas,
                 _fm.ruta_mapa,
                 _fm.get_iconos,
                 _fm.guardar_marcador,
                 _fm.get_marcadores,
                 _fm.marcar_visitado
            ]
    
    def cargar_juegos(self):
        import os
        __con = self.__con
        __cur = __con.cursor()
        
        # __juegos_path = os.path.join(os.getcwd(), 'Juegos')
        __juegos_path = "web/content/Juegos/"
        __carpetas = [(f.name, f.path) for f in os.scandir(__juegos_path) if f.is_dir()]

        for _c, _pc in __carpetas:
            _relPath = os.path.relpath(_pc, 'web')
            __cons = f"SELECT COUNT(*) CANT FROM TBL_JUEGOS WHERE NOMBRE_JUEGO = '{str(_c).strip()}'"
            __cur.execute(__cons)
            __cantidad = __cur.fetchone()["CANT"]

            if __cantidad <= 0:
                __nombre_juego = _c
                # __ruta_juego = _relPath

                # __ruta_iconos = os.path.join(__ruta_juego, 'Iconos')

                __ins = "INSERT INTO TBL_JUEGOS (NOMBRE_JUEGO, RUTA) " + \
                f"VALUES ('{__nombre_juego}', '{_relPath}')"

                __cur.execute(__ins)
                __con.commit()
            else:
                    print(_c, '- El juego ya existe en la base')

            self.cargar_mapas_juego(_c, _pc)
            self.cargar_iconos_juego(_c, _pc)

    def cargar_mapas_juego(self, _c, _pc):
        import os
        __con = self.__con
        __cur = __con.cursor()

        __mapas_path = os.path.join(_pc, 'Mapas')
        __cons = f"SELECT ID FROM TBL_JUEGOS WHERE NOMBRE_JUEGO = '{str(_c).strip()}'"
        __cur.execute(__cons)
        __juegoID = __cur.fetchone()["ID"]
        __archivos = [(f.name, f.path) for f in os.scandir(__mapas_path) if f.is_file()]

        for _a, _da in __archivos:
            __cons = f"SELECT COUNT(*) CANT FROM TBL_MAPS WHERE NOMBRE_MAPA = '{str(_a).strip()}'"
            __cur.execute(__cons)
            __cantidad = __cur.fetchone()["CANT"]

            if __cantidad <= 0:
                __nombre_mapa = _a
                __ruta_mapa = _da
                _relPath = os.path.relpath(_da, 'web')

                __ins = "INSERT INTO TBL_MAPS (NOMBRE_MAPA, RUTA_MAPA, JuegoID) " + \
                f"VALUES ('{__nombre_mapa}', '{_relPath}', {__juegoID})"

                __cur.execute(__ins)
                __con.commit()
            else:
                 print(_c, '- El mapa ya existe en la base')

    
    def cargar_iconos_juego(self, _c, _pc):
        import os
        __con = self.__con
        __cur = __con.cursor()

        __iconos_path = os.path.join(_pc, 'Iconos')
        __cons = f"SELECT ID FROM TBL_JUEGOS WHERE NOMBRE_JUEGO = '{str(_c).strip()}'"
        __cur.execute(__cons)
        __juegoID = __cur.fetchone()["ID"]

        __cons = f"SELECT COUNT(*) CANT FROM TBL_ICONS WHERE JuegoID = {__juegoID}"
        __cur.execute(__cons)
        __cantidad = __cur.fetchone()["CANT"]

        if __cantidad <= 0:
            __iconos = [(_file, _root) for _root, dirs, files in os.walk(__iconos_path) for _file in files if _file.endswith(".png")]

            for _i, _di in __iconos:
                _rdi = os.path.relpath(_di, 'web')
                __cons = "INSERT INTO TBL_ICONS (NOMBRE_ICONO, JuegoID, RUTA_ICONO) " + \
                        f"VALUES ('{_i}', {__juegoID}, '{_rdi}')"
                __cur.execute(__cons)
            __con.commit()
        else:
             print("Los iconos para el mapa ya están cargados")

         
    
    def obtener_juegos(self):
        __listaR = []
        __con = self.__con
        __cur = __con.cursor()

        __cur.execute("SELECT * FROM TBL_JUEGOS ORDER BY ID;")

        __registros = __cur.fetchall()

        if len(__registros) == 0:
             print('no hay registros')
        else:
            for _r in __registros:
                __id = _r["ID"]
                __nom = _r["NOMBRE_JUEGO"]
                __ruta = _r["RUTA"]
                __listaR.append([
                     __id, 
                     __nom, __ruta])

        # print('devolviendo', __listaR)
        return __listaR