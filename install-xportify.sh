#!/usr/bin/env bash
APP_SRC="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
DEST="$HOME/.local/share/xportify"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/256x256/apps"

echo "==> Instalando Xportify"
echo "Origen: $APP_SRC"
echo "Destino: $DEST"
echo ""

mkdir -p "$DEST" "$APPS" "$ICONS"

echo "[1/4] Copiando archivos..."
cp -r "$APP_SRC"/. "$DEST/" 2>/dev/null

echo "[2/4] Ajustando permisos..."
chmod +x "$DEST/Xportify" "$DEST/xportify" 2>/dev/null
chmod +x "$DEST/install-xportify.sh" 2>/dev/null

echo "[3/4] Instalando icono y acceso directo..."
if [ -f "$DEST/assets/xportify.png" ]; then
  cp "$DEST/assets/xportify.png" "$ICONS/xportify.png"
elif [ -f "$DEST/xportify.png" ]; then
  cp "$DEST/xportify.png" "$ICONS/xportify.png"
fi

cat > "$APPS/xportify.desktop" << DESK
[Desktop Entry]
Version=1.0
Type=Application
Name=Xportify
GenericName=Music Downloader
Comment=Convierte tus listas de Spotify, YouTube Music y más a MP3
Exec=$DEST/Xportify
Icon=xportify
Terminal=false
Categories=AudioVideo;Audio;Utility;
StartupNotify=true
StartupWMClass=Xportify
MimeType=audio/mpeg;
DESK

chmod +x "$APPS/xportify.desktop"

echo "[4/4] Actualizando caché..."
update-desktop-database "$APPS" 2>/dev/null
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null

echo ""
echo "=================================="
echo "  Xportify instalado correctamente"
echo "=================================="
echo ""
echo "Ya puedes buscar 'Xportify' en el menú de aplicaciones"
echo "o ejecutar desde terminal: $DEST/Xportify"
echo ""
