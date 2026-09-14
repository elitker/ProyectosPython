from pathlib import Path
from sqlite3.dbapi2 import Connection


class Iniciar:
    """Acciones del visor de mapas expuestas a JavaScript por Eel."""

    def __init__(self, __conSQLite: Connection, web_dir=None):
        self.__con = __conSQLite
        self.__mapID = 0
        self.__JuegoID = 0
        self.web_dir = Path(web_dir) if web_dir else Path(__file__).resolve().parents[1] / "web"

    @staticmethod
    def __normalizar_path(ruta):
        return str(ruta or "").replace("\\", "/").strip("/")

    @staticmethod
    def __parse_dimensiones(dimensiones):
        try:
            ancho, alto = str(dimensiones or "30,30").split(",")[:2]
            return [int(ancho), int(alto)]
        except (TypeError, ValueError):
            return [30, 30]

    @staticmethod
    def __parse_coords(coords):
        lat, lng = str(coords).split("|")[:2]
        return [float(lat), float(lng)]

    def __icono_url(self, ruta_icono, nombre_icono):
        ruta = self.__normalizar_path(ruta_icono)
        nombre = self.__normalizar_path(nombre_icono)
        return f"{ruta}/{nombre}" if ruta else nombre

    def __icono_nombre_visible(self, ruta_icono, nombre_icono):
        ruta = self.__normalizar_path(ruta_icono)
        carpeta = ruta.split("/")[-1] if ruta else ""
        if carpeta and carpeta.lower() != "iconos":
            return f"{carpeta}/{nombre_icono}"
        return str(nombre_icono)

    def juego_seleccionado(self, _juego):
        try:
            juego_id = int(_juego)
        except (TypeError, ValueError):
            return {"ok": False, "message": "ID de juego inválido"}

        __cur = self.__con.cursor()
        existe = __cur.execute("SELECT 1 FROM TBL_JUEGOS WHERE ID = ?;", (juego_id,)).fetchone()
        if existe is None:
            return {"ok": False, "message": "El juego seleccionado no existe"}

        self.__JuegoID = juego_id
        self.__mapID = 0
        print("Juego seleccionado:", juego_id)
        return {"ok": True}

    def mapa_seleccionado(self, _map):
        try:
            mapa_id = int(_map)
        except (TypeError, ValueError):
            return {"ok": False, "message": "ID de mapa inválido"}

        __cur = self.__con.cursor()
        mapa = __cur.execute(
            "SELECT ID, JuegoID FROM TBL_MAPS WHERE ID = ?;",
            (mapa_id,),
        ).fetchone()
        if mapa is None:
            return {"ok": False, "message": "El mapa seleccionado no existe"}

        self.__mapID = mapa_id
        self.__JuegoID = int(mapa["JuegoID"])
        print("Mapa seleccionado:", mapa_id)
        return {"ok": True}

    def cargar_mapas(self):
        __listaR = []
        if self.__JuegoID <= 0:
            return __listaR

        __cur = self.__con.cursor()
        __cur.execute(
            "SELECT * FROM TBL_MAPS WHERE JuegoID = ? ORDER BY NOMBRE_MAPA;",
            (self.__JuegoID,),
        )
        __registros = __cur.fetchall()

        for _r in __registros:
            __listaR.append([
                _r["ID"],
                _r["NOMBRE_MAPA"],
            ])

        return __listaR

    def ruta_mapa(self):
        if self.__mapID <= 0:
            return ""

        __cur = self.__con.cursor()
        row = __cur.execute(
            "SELECT RUTA_MAPA FROM TBL_MAPS WHERE ID = ?;",
            (self.__mapID,),
        ).fetchone()
        if row is None:
            return ""

        return self.__normalizar_path(row["RUTA_MAPA"])

    def get_iconos(self):
        __listaR = [{"id": 0, "name": "Seleccionar...", "image": ""}]
        if self.__JuegoID <= 0:
            return __listaR

        __cur = self.__con.cursor()
        __cur.execute(
            "SELECT * FROM TBL_ICONS WHERE JuegoID = ? ORDER BY RUTA_ICONO, NOMBRE_ICONO;",
            (self.__JuegoID,),
        )
        __iconos_cargados = __cur.fetchall()

        for _i in __iconos_cargados:
            __listaR.append({
                "id": _i["ID"],
                "name": self.__icono_nombre_visible(_i["RUTA_ICONO"], _i["NOMBRE_ICONO"]),
                "image": self.__icono_url(_i["RUTA_ICONO"], _i["NOMBRE_ICONO"]),
                "dimensions": self.__parse_dimensiones(_i["DIMENSIONES"]),
            })

        return __listaR

    def guardar_marcador(self, _lista):
        if self.__JuegoID <= 0 or self.__mapID <= 0:
            return {"ok": False, "message": "Primero selecciona un juego y un mapa"}

        try:
            __iconoID = int(_lista.get("icono", 0))
            __coords = str(_lista.get("coords", "")).strip()
            self.__parse_coords(__coords)
        except (AttributeError, TypeError, ValueError):
            return {"ok": False, "message": "Datos del marcador inválidos"}

        if __iconoID <= 0:
            return {"ok": False, "message": "Selecciona un icono para el marcador"}

        __descri = str(_lista.get("descri", "")).strip()
        __cur = self.__con.cursor()
        icono = __cur.execute(
            "SELECT 1 FROM TBL_ICONS WHERE ID = ? AND JuegoID = ?;",
            (__iconoID, self.__JuegoID),
        ).fetchone()
        if icono is None:
            return {"ok": False, "message": "El icono seleccionado no pertenece al juego actual"}

        __cur.execute(
            "INSERT INTO TR_POINTS (JuegoID, MapaID, IconoID, Coords, Descripcion) "
            "VALUES (?, ?, ?, ?, ?);",
            (self.__JuegoID, self.__mapID, __iconoID, __coords, __descri),
        )
        self.__con.commit()
        return {"ok": True, "message": "OK", "id": __cur.lastrowid}

    def get_marcadores(self):
        if self.__JuegoID <= 0 or self.__mapID <= 0:
            return []

        __cur = self.__con.cursor()
        __cons = (
            "SELECT "
            "p.ID, p.JuegoID, p.MapaID, p.IconoID, p.Coords, p.VISITED, p.Descripcion, "
            "i.NOMBRE_ICONO, i.DIMENSIONES, i.RUTA_ICONO "
            "FROM TR_POINTS p "
            "JOIN TBL_ICONS i ON i.ID = p.IconoID "
            "WHERE p.JuegoID = ? "
            "AND (p.MapaID = ? OR p.MapaID IS NULL) "
            "ORDER BY p.ID;"
        )
        __cur.execute(__cons, (self.__JuegoID, self.__mapID))
        __marcadores = __cur.fetchall()

        lista = []
        for _m in __marcadores:
            try:
                coords = self.__parse_coords(_m["Coords"])
            except (TypeError, ValueError):
                continue

            lista.append({
                "id": _m["ID"],
                "juego_id": _m["JuegoID"],
                "mapa_id": _m["MapaID"],
                "icon_id": _m["IconoID"],
                "coords": coords,
                "coords_text": _m["Coords"],
                "visited": int(_m["VISITED"] or 0),
                "description": _m["Descripcion"] or "",
                "icon_name": self.__icono_nombre_visible(_m["RUTA_ICONO"], _m["NOMBRE_ICONO"]),
                "icon_url": self.__icono_url(_m["RUTA_ICONO"], _m["NOMBRE_ICONO"]),
                "dimensions": self.__parse_dimensiones(_m["DIMENSIONES"]),
            })

        return lista

    def marcar_visitado(self, _id_point, _visited=1):
        try:
            __id = int(_id_point)
            __visited = 1 if bool(_visited) else 0
        except (TypeError, ValueError):
            return {"ok": False, "message": "ID de marcador inválido"}

        __cur = self.__con.cursor()
        __cur.execute(
            "UPDATE TR_POINTS SET VISITED = ? "
            "WHERE ID = ? AND JuegoID = ? AND (MapaID = ? OR MapaID IS NULL);",
            (__visited, __id, self.__JuegoID, self.__mapID),
        )
        self.__con.commit()

        if __cur.rowcount <= 0:
            return {"ok": False, "message": "No se encontró el marcador"}

        print("Actualizado punto:", __id, "visitado=", __visited)
        return {"ok": True, "visited": __visited}

    def eliminar_marcador(self, _id_point):
        try:
            __id = int(_id_point)
        except (TypeError, ValueError):
            return {"ok": False, "message": "ID de marcador inválido"}

        __cur = self.__con.cursor()
        __cur.execute(
            "DELETE FROM TR_POINTS "
            "WHERE ID = ? AND JuegoID = ? AND (MapaID = ? OR MapaID IS NULL);",
            (__id, self.__JuegoID, self.__mapID),
        )
        self.__con.commit()

        if __cur.rowcount <= 0:
            return {"ok": False, "message": "No se encontró el marcador"}
        return {"ok": True}

    def actualizar_marcador(self, _id_point, _datos):
        try:
            __id = int(_id_point)
            __descri = str(_datos.get("descri", "")).strip()
        except (AttributeError, TypeError, ValueError):
            return {"ok": False, "message": "Datos del marcador inválidos"}

        __cur = self.__con.cursor()
        __cur.execute(
            "UPDATE TR_POINTS SET Descripcion = ? "
            "WHERE ID = ? AND JuegoID = ? AND (MapaID = ? OR MapaID IS NULL);",
            (__descri, __id, self.__JuegoID, self.__mapID),
        )
        self.__con.commit()

        if __cur.rowcount <= 0:
            return {"ok": False, "message": "No se encontró el marcador"}
        return {"ok": True}

    def resumen_progreso(self):
        if self.__JuegoID <= 0 or self.__mapID <= 0:
            return {"total": 0, "visited": 0, "pending": 0, "percent": 0}

        __cur = self.__con.cursor()
        row = __cur.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(CASE WHEN VISITED = 1 THEN 1 ELSE 0 END), 0) AS visited "
            "FROM TR_POINTS WHERE JuegoID = ? AND (MapaID = ? OR MapaID IS NULL);",
            (self.__JuegoID, self.__mapID),
        ).fetchone()
        total = int(row["total"] or 0)
        visited = int(row["visited"] or 0)
        pending = max(total - visited, 0)
        percent = round((visited / total) * 100, 2) if total else 0
        return {"total": total, "visited": visited, "pending": pending, "percent": percent}
