import sqlite3 as sq3
from pathlib import Path

try:
    from . import func_mapa as FM
except ImportError:  # Permite ejecutar inicio.py directamente desde la carpeta GamesMaps
    import fFuncGM.func_mapa as FM


class Funciones:
    """Funciones expuestas a Eel para descubrir juegos, mapas e iconos.

    La app se apoya en una estructura de carpetas dentro de ``web/content/Juegos``:

    web/content/Juegos/<Juego>/Mapas/<mapa.png>
    web/content/Juegos/<Juego>/Iconos/<categoria>/<icono.png>

    Los paths se guardan en la base como rutas relativas a ``web`` y siempre con
    barras normales (/), para que funcionen igual en Windows, Linux y el navegador.
    """

    EXTENSIONES_MAPAS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    EXTENSIONES_ICONOS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parents[1]
        self.web_dir = self.base_dir / "web"
        self.juegos_dir = self.web_dir / "content" / "Juegos"
        self.db_path = self.base_dir / "GamesMapsV2.db"

        __con = sq3.connect(str(self.db_path))
        __con.row_factory = sq3.Row
        __con.execute("PRAGMA foreign_keys = ON;")
        self.__con = __con

        self.__crear_tablas()
        self.__migrar_tablas()
        self.__crear_indices()

    def __crear_tablas(self):
        __cur = self.__con.cursor()

        __cur.execute(
            "CREATE TABLE IF NOT EXISTS TBL_JUEGOS "
            "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
            "NOMBRE_JUEGO TEXT NOT NULL, "
            "RUTA TEXT NOT NULL, "
            "RUTA_ICONOS TEXT NULL "
            ");"
        )

        __cur.execute(
            "CREATE TABLE IF NOT EXISTS TBL_ICONS "
            "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
            "NOMBRE_ICONO TEXT NOT NULL, "
            "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID), "
            "RUTA_ICONO TEXT NOT NULL, "
            "DIMENSIONES TEXT NOT NULL DEFAULT ('30,30') "
            ");"
        )

        __cur.execute(
            "CREATE TABLE IF NOT EXISTS TR_POINTS "
            "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
            "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID), "
            "MapaID INTEGER REFERENCES TBL_MAPS (ID), "
            "IconoID INTEGER REFERENCES TBL_ICONS (ID), "
            "Coords TEXT NOT NULL, "
            "VISITED INTEGER NOT NULL DEFAULT (0), "
            "Descripcion TEXT NULL"
            ");"
        )

        __cur.execute(
            "CREATE TABLE IF NOT EXISTS TBL_MAPS "
            "(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
            "NOMBRE_MAPA TEXT NOT NULL, "
            "RUTA_MAPA TEXT NOT NULL, "
            "JuegoID INTEGER REFERENCES TBL_JUEGOS (ID) "
            ");"
        )

        self.__con.commit()

    def __crear_indices(self):
        __cur = self.__con.cursor()
        __cur.execute("CREATE INDEX IF NOT EXISTS IDX_MAPS_JUEGOID ON TBL_MAPS (JuegoID);")
        __cur.execute("CREATE INDEX IF NOT EXISTS IDX_ICONS_JUEGOID ON TBL_ICONS (JuegoID);")
        __cur.execute("CREATE INDEX IF NOT EXISTS IDX_POINTS_JUEGO_MAPA ON TR_POINTS (JuegoID, MapaID);")
        self.__con.commit()

    def __migrar_tablas(self):
        """Aplica cambios compatibles con bases existentes.

        Versiones anteriores guardaban el ID del mapa dentro de TR_POINTS.JuegoID.
        Ahora separamos JuegoID y MapaID para que cada marcador pertenezca al mapa
        correcto y no aparezca mezclado en otros mapas del mismo juego.
        """
        __cur = self.__con.cursor()
        __columnas = {row[1].lower() for row in __cur.execute("PRAGMA table_info(TR_POINTS);")}

        if "mapaid" not in __columnas:
            __cur.execute("ALTER TABLE TR_POINTS ADD COLUMN MapaID INTEGER REFERENCES TBL_MAPS (ID);")
            # Migración best-effort: en la versión previa JuegoID contenía el ID de mapa.
            __cur.execute(
                "UPDATE TR_POINTS "
                "SET MapaID = JuegoID "
                "WHERE MapaID IS NULL "
                "AND EXISTS (SELECT 1 FROM TBL_MAPS m WHERE m.ID = TR_POINTS.JuegoID);"
            )
            __cur.execute(
                "UPDATE TR_POINTS "
                "SET JuegoID = (SELECT m.JuegoID FROM TBL_MAPS m WHERE m.ID = TR_POINTS.MapaID) "
                "WHERE MapaID IS NOT NULL "
                "AND EXISTS (SELECT 1 FROM TBL_MAPS m WHERE m.ID = TR_POINTS.MapaID);"
            )

        self.__normalizar_rutas_guardadas()
        self.__con.commit()

    def __normalizar_rutas_guardadas(self):
        __cur = self.__con.cursor()
        for tabla, columna in (
            ("TBL_JUEGOS", "RUTA"),
            ("TBL_MAPS", "RUTA_MAPA"),
            ("TBL_ICONS", "RUTA_ICONO"),
        ):
            for row in __cur.execute(f"SELECT ID, {columna} FROM {tabla};").fetchall():
                ruta = row[columna]
                if ruta and "\\" in ruta:
                    __cur.execute(
                        f"UPDATE {tabla} SET {columna} = ? WHERE ID = ?;",
                        (self.__normalizar_path(ruta), row["ID"]),
                    )

    @staticmethod
    def __normalizar_path(ruta):
        return str(ruta).replace("\\", "/").strip("/")

    def __relativo_a_web(self, ruta: Path):
        return ruta.relative_to(self.web_dir).as_posix()

    def funciones_to_eel(self):
        _fm = FM.Iniciar(self.__con, self.web_dir)

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
            _fm.marcar_visitado,
            _fm.eliminar_marcador,
            _fm.actualizar_marcador,
            _fm.resumen_progreso,
        ]

    def cargar_juegos(self):
        """Escanea el contenido local y sincroniza juegos, mapas e iconos."""
        if not self.juegos_dir.exists():
            return {
                "ok": False,
                "message": f"No existe la carpeta de juegos: {self.juegos_dir}",
                "juegos": 0,
            }

        __cur = self.__con.cursor()
        cantidad_juegos = 0

        for carpeta_juego in sorted(self.juegos_dir.iterdir(), key=lambda p: p.name.lower()):
            if not carpeta_juego.is_dir():
                continue

            nombre_juego = carpeta_juego.name.strip()
            ruta_juego = self.__relativo_a_web(carpeta_juego)
            row_juego = __cur.execute(
                "SELECT ID FROM TBL_JUEGOS WHERE NOMBRE_JUEGO = ?;",
                (nombre_juego,),
            ).fetchone()

            if row_juego is None:
                __cur.execute(
                    "INSERT INTO TBL_JUEGOS (NOMBRE_JUEGO, RUTA) VALUES (?, ?);",
                    (nombre_juego, ruta_juego),
                )
                juego_id = __cur.lastrowid
            else:
                juego_id = row_juego["ID"]
                __cur.execute(
                    "UPDATE TBL_JUEGOS SET RUTA = ? WHERE ID = ?;",
                    (ruta_juego, juego_id),
                )

            self.cargar_mapas_juego(juego_id, carpeta_juego)
            self.cargar_iconos_juego(juego_id, carpeta_juego)
            cantidad_juegos += 1

        self.__con.commit()
        return {"ok": True, "message": "Juegos sincronizados", "juegos": cantidad_juegos}

    def cargar_mapas_juego(self, juego_id, carpeta_juego: Path):
        __cur = self.__con.cursor()
        mapas_path = carpeta_juego / "Mapas"
        if not mapas_path.exists():
            return

        for archivo_mapa in sorted(mapas_path.iterdir(), key=lambda p: p.name.lower()):
            if not archivo_mapa.is_file() or archivo_mapa.suffix.lower() not in self.EXTENSIONES_MAPAS:
                continue

            nombre_mapa = archivo_mapa.name.strip()
            ruta_mapa = self.__relativo_a_web(archivo_mapa)
            row_mapa = __cur.execute(
                "SELECT ID FROM TBL_MAPS WHERE JuegoID = ? AND NOMBRE_MAPA = ?;",
                (juego_id, nombre_mapa),
            ).fetchone()

            if row_mapa is None:
                __cur.execute(
                    "INSERT INTO TBL_MAPS (NOMBRE_MAPA, RUTA_MAPA, JuegoID) VALUES (?, ?, ?);",
                    (nombre_mapa, ruta_mapa, juego_id),
                )
            else:
                __cur.execute(
                    "UPDATE TBL_MAPS SET RUTA_MAPA = ? WHERE ID = ?;",
                    (ruta_mapa, row_mapa["ID"]),
                )

    def cargar_iconos_juego(self, juego_id, carpeta_juego: Path):
        __cur = self.__con.cursor()
        iconos_path = carpeta_juego / "Iconos"
        if not iconos_path.exists():
            return

        for archivo_icono in sorted(iconos_path.rglob("*"), key=lambda p: p.as_posix().lower()):
            if not archivo_icono.is_file() or archivo_icono.suffix.lower() not in self.EXTENSIONES_ICONOS:
                continue

            nombre_icono = archivo_icono.name.strip()
            ruta_icono = self.__relativo_a_web(archivo_icono.parent)
            row_icono = __cur.execute(
                "SELECT ID FROM TBL_ICONS WHERE JuegoID = ? AND NOMBRE_ICONO = ? AND RUTA_ICONO = ?;",
                (juego_id, nombre_icono, ruta_icono),
            ).fetchone()

            if row_icono is None:
                __cur.execute(
                    "INSERT INTO TBL_ICONS (NOMBRE_ICONO, JuegoID, RUTA_ICONO) VALUES (?, ?, ?);",
                    (nombre_icono, juego_id, ruta_icono),
                )

    def obtener_juegos(self):
        __listaR = []
        __cur = self.__con.cursor()
        __cur.execute("SELECT * FROM TBL_JUEGOS ORDER BY NOMBRE_JUEGO;")
        __registros = __cur.fetchall()

        for _r in __registros:
            __listaR.append([
                _r["ID"],
                _r["NOMBRE_JUEGO"].replace("_", " "),
                self.__normalizar_path(_r["RUTA"]),
            ])

        return __listaR
