#!/bin/zsh
# Gera dist/flyer-cmyk.plugin (zip do conteúdo de plugins/flyer-cmyk) para enviar ao app
# do Claude (aba Plugins da conta). Uso: scripts/empacotar-plugin.sh
set -e
raiz=${0:A:h:h}
mkdir -p "$raiz/dist"
saida="$raiz/dist/flyer-cmyk.plugin"
rm -f "$saida"
cd "$raiz/plugins/flyer-cmyk"
zip -qr "$saida" . -x "*.DS_Store" -x "*__pycache__*" -x "*.pyc"
echo "$saida ($(du -h "$saida" | cut -f1))"
