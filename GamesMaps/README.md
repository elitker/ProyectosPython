# GamesMaps

GamesMaps es una app de escritorio hecha con Python + Eel + Leaflet para visualizar mapas de videojuegos, agregar marcadores y llevar progreso local.

## Funcionalidades actuales

- Biblioteca de juegos detectada desde `web/content/Juegos`.
- Selección de mapas por juego.
- Visor interactivo con zoom y desplazamiento sobre una imagen de mapa.
- Agregado de marcadores con clic derecho.
- Categorías basadas en iconos del juego.
- Búsqueda rápida por descripción, icono o coordenadas.
- Filtros por categoría/icono.
- Filtros por estado: pendiente o visitado.
- Progreso de marcadores visitados.
- Edición y eliminación de marcadores.
- Herramienta simple para medir distancia entre dos puntos del mapa.

> Nota: el objetivo es implementar flujos similares a sitios de mapas interactivos sin copiar sus assets, datos privados ni diseño exacto.

## Instalación

Desde la carpeta del proyecto:

```bash
cd GamesMaps
python -m pip install -r requirements.txt
```

## Ejecución

```bash
python inicio.py
```

También puede ejecutarse desde la raíz del repositorio:

```bash
python GamesMaps/inicio.py
```

## Estructura esperada de contenido

Cada juego debe vivir en una carpeta propia:

```text
web/content/Juegos/<Nombre_del_juego>/
├── Mapas/
│   └── mapa.png
└── Iconos/
    └── Categoria/
        └── icono.png
```

Formatos soportados:

- Mapas: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`
- Iconos: `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.svg`

Al abrir la app, usa **Sincronizar carpeta Juegos** para actualizar la base SQLite (`GamesMapsV2.db`) con los juegos, mapas e iconos disponibles.

## Base de datos

La app usa SQLite. Los marcadores se guardan en `TR_POINTS` asociados a:

- `JuegoID`
- `MapaID`
- `IconoID`
- coordenadas
- estado visitado/pendiente
- descripción

Versiones anteriores guardaban el ID del mapa dentro de `JuegoID`; el código actual migra esa información automáticamente agregando `MapaID` si falta.
