# Xportify

Convierte tus listas de Spotify, YouTube Music o archivos CSV/Excel a MP3 desde una app de escritorio limpia y directa.

## Características

- **Multi-entrada**: Sube CSV/Excel exportado con [Exportify](https://watsonbox.github.io/exportify/), pega una URL de Spotify/YouTube Music o pega texto `Artista - Canción`.
- **Liked Songs sin rodeos**: Usa Exportify/Playlistation para obtener tus "Me gusta" rápidamente con enlaces directos integrados.
- **Búsqueda híbrida**: Prioriza YouTube Music para mayor precisión y cae a YouTube como fallback.
- **Interfaz limpia**: Diseño oscuro minimalista siguiendo las directrices de Impeccable, sin aspecto genérico IA.
- **Descargas con hilos**: Interfaz no se bloquea durante la descarga.
- **Metadatos**: Añade título, artista y álbum al MP3.
- **Detección FFmpeg**: Te avisa si no lo tienes instalado.
- **Reanudable**: Omite archivos ya existentes.

## Requisitos

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) instalado en el sistema
- Linux, Windows o macOS

## Instalación

```bash
git clone https://github.com/TU_USUARIO/xportify.git
cd xportify
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

O con el entrypoint:

```bash
pip install -e .
xportify
```

## Obtener listas desde Exportify

Si no tienes un CSV:

1. Abre [watsonbox.github.io/exportify](https://watsonbox.github.io/exportify/) (recomendado)
2. Inicia sesión con Spotify
3. Exporta `Liked Songs` o la playlist que quieras como CSV
4. Ábrelo desde Xportify

También tienes [exportify.net](https://exportify.net/) y [playlistation.com](https://playlistation.com/).

## Licencia

MIT
