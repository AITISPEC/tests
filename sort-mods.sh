#!/usr/bin/env bash
# modsplit.sh — раскладывает моды по client-mods / server-mods / unknown-mods
# Запуск: bash modsplit.sh [папка_с_модами]
# По умолчанию: текущая папка.

set -euo pipefail
shopt -s nullglob nocasematch

MODS_DIR="${1:-.}"
CLIENT_DIR="$MODS_DIR/client-mods"
SERVER_DIR="$MODS_DIR/server-mods"
UNKNOWN_DIR="$MODS_DIR/unknown-mods"

mkdir -p "$CLIENT_DIR" "$SERVER_DIR" "$UNKNOWN_DIR"

# Только клиент
client_only=(
  "appleskin*"
  "better-clouds*"
  "better-compatability-checker*"
  "BetterF3*"
  "better-serverlist*"
  "chat_heads*"
  "cloth-config*"
  "entityculling*"
  "ImmediatelyFast*"
  "InventoryProfilesNext*"
  "iris*"
  "Jade*"
  "jei*"
  "launcher-companion*"
  "libIPN*"
  "modmenu*"
  "notenoughcrashes*"
  "sodium*"
  "sonar-skins*"
  "status-effect-bars*"
  "ukulib*"
  "ukus-armor-hud*"
  "visuality*"
  "xaerominimap*"
  "xaeroworldmap*"
  "yet_another_config_lib_v3*"
)

# Только сервер
server_only=(
  "dungeons-and-taverns*"
  "Explorify*"
  "FallingTree*"
  "lithostitched*"
  "oneblock*"
  "polymer-bundled*"
  "Structory*"
  "Terralith*"
)

# Нужны и клиенту, и серверу
both=(
  "architectury*"
  "balm*"
  "BCRefabricated*"
  "carryon*"
  "codxlib*"
  "CreativeCore*"
  "fabric-api*"
  "fabric-language-kotlin*"
  "ferritecore*"
  "friendsandfoes*"
  "fzzy_config*"
  "graves*"
  "lithium*"
  "mcw-bridges*"
  "mcw-furniture*"
  "mixson*"
  "naturalist*"
  "placeholder-api*"
  "RebornCore*"
  "ResourcefulLib*"
  "shogi*"
  "spark*"
  "TechReborn*"
  "waystones*"
)

classify() {
  local name="$1" pat
  for pat in "${client_only[@]}"; do [[ "$name" == $pat ]] && { echo client; return; }; done
  for pat in "${server_only[@]}"; do [[ "$name" == $pat ]] && { echo server; return; }; done
  for pat in "${both[@]}"; do [[ "$name" == $pat ]] && { echo both; return; }; done
  echo unknown
}

for f in "$MODS_DIR"/*.jar; do
  name="$(basename "$f")"
  case "$(classify "$name")" in
    client)
      cp -v "$f" "$CLIENT_DIR/"
      ;;
    server)
      cp -v "$f" "$SERVER_DIR/"
      ;;
    both)
      cp -v "$f" "$CLIENT_DIR/"
      cp -v "$f" "$SERVER_DIR/"
      ;;
    unknown)
      cp -v "$f" "$UNKNOWN_DIR/"
      ;;
  esac
done

echo
echo "Готово:"
echo "  client-mods:  $CLIENT_DIR"
echo "  server-mods:  $SERVER_DIR"
echo "  unknown-mods: $UNKNOWN_DIR  (проверь вручную)"
