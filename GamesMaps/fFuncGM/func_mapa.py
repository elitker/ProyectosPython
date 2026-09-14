from sqlite3.dbapi2 import Connection
import os

class Iniciar:
    def __init__(self, __conSQLite: Connection):
        self.__con = __conSQLite
        self.__mapID = 0
        self.__JuegoID = 0

    def juego_seleccionado(self, _juego):
        self.__JuegoID = _juego
        print("Juego seleccionado:", _juego)

    def mapa_seleccionado(self, _map):
        self.__mapID = _map
        print("Mapa seleccionado:", _map)

    def cargar_mapas(self):
        __juegoID = self.__JuegoID

        __listaR = []
        __con = self.__con
        __cur = __con.cursor()

        __cur.execute(f"SELECT * FROM TBL_MAPS WHERE JuegoID = {__juegoID} ORDER BY ID;")

        __registros = __cur.fetchall()

        if len(__registros) == 0:
             print('no hay registros')
        else:
            for _r in __registros:
                __id = _r["ID"]
                __nom = _r["NOMBRE_MAPA"]
                __listaR.append([
                     __id, 
                     __nom])

        return __listaR   


    def ruta_mapa(self):
        __mapID = self.__mapID
        print('el mapa seleccionado es ID:', __mapID)
        __con = self.__con
        __cur = __con.cursor()

        __cur.execute(f"SELECT RUTA_MAPA FROM TBL_MAPS WHERE ID = {__mapID} ORDER BY ID;")
        __ruta = __cur.fetchone()["RUTA_MAPA"]

        return __ruta
    
    def get_iconos(self):
        # __d = (
        #     {"id": "1", "name": "Principal"},
        #     {"id": "2", "name": "Secundario"},
        #     {"id": "3", "name": "Terceario"}
        # )
        __con = self.__con
        __cur = __con.cursor()
        __juegoID = self.__JuegoID

        __listaR = []
        __dicty = {"id": 0, "name": "Seleccionar...", "image": ""}
        __listaR.append(__dicty)

        __cur.execute(f"SELECT * FROM TBL_ICONS WHERE JuegoID = {__juegoID} ORDER BY ID;")
        __iconos_cargados = __cur.fetchall()

        for _i in __iconos_cargados:
            _id = _i["ID"]
            __nom = _i["NOMBRE_ICONO"]
            __ruta = os.path.join(_i["RUTA_ICONO"],__nom)

            __dicty = {
                "id": _id, "name": __nom, "image": __ruta
            }
            __listaR.append(__dicty)
        
        return __listaR
    
    def guardar_marcador(self, _lista):
        print(_lista)
        __con = self.__con
        __cur = __con.cursor()
        __iconoID = _lista['icono']
        __coords = _lista['coords']
        __descri = _lista['descri']
        __cur.execute(f"INSERT INTO TR_POINTS (juegoid, iconoid,coords,descripcion) values ({self.__mapID}, {__iconoID}, '{__coords}', '{__descri}')")
        __con.commit()
        return "OK"
    
    def get_marcadores(self):
        __con = self.__con
        __cur = __con.cursor()
        __cons = (
            "select \n"
                "p.juegoID || '-' || p.ID || '-' || p.iconoID as ID, \n"
                "p.Coords, \n"
                "i.NOMBRE_ICONO, \n"
                "p.VISITED, \n"
                "i.DIMENSIONES, \n"
                "i.RUTA_ICONO \n"
            "from tr_points p join tbl_icons i on i.ID = p.IconoID \n"
            f"where i.JuegoID = '{self.__JuegoID}'"
        )
        __cur.execute(__cons)
        _listaR = list()
        _lista2 = list()

        __marcadores = __cur.fetchall()

        for _m in __marcadores:
            __dimensiones = _m["DIMENSIONES"].split(",")
            __dimensiones = [int(x) for x in __dimensiones]
            _listaR.append(_m["RUTA_ICONO"])
            _listaR.append(str(_m["Coords"]).split('|'))
            _listaR.append(_m["VISITED"])
            __ruta = os.path.join(_m["RUTA_ICONO"], _m["NOMBRE_ICONO"])
            # _lista2.append(_listaR)
            _lista2.append([__ruta, (str(_m["Coords"]).split('|')), _m["VISITED"], _m["ID"], __dimensiones])

        return (_lista2)
    
    def marcar_visitado(self, _id_point):
        __aux = str(_id_point).split('-')
        __id = int(__aux[0])
        __juegoID = int(__aux[1])
        __iconoID = int(__aux[2])
        __con = self.__con
        __cur = __con.cursor()
        __cur.execute(f"UPDATE TR_POINTS SET VISITED = 1 WHERE ID = {__id} AND JuegoID = {__juegoID} AND IconoID = {__iconoID}")
        __con.commit()

        print("Actualizado punto:", _id_point)