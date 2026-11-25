#!/bin/zsh
# Renderiza um SVG de arte (em mm) para PNG com o Chrome headless.
# Uso: previa_svg.sh arte.svg saida.png [largura_mm altura_mm] [escala]
# largura/altura = tamanho TOTAL do SVG (com sangria). Padrão: A5 + 3 mm = 154×216.
set -e
svg=${1:A}; png=${2:A}; L=${3:-154}; A=${4:-216}; E=${5:-2}
w=$(( L * 3.7795275591 )); h=$(( A * 3.7795275591 ))
perfil=$(mktemp -d)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
  --hide-scrollbars --user-data-dir="$perfil" --force-device-scale-factor=$E \
  --window-size=${w%.*},${h%.*} --screenshot="$png" "file://$svg" >/dev/null 2>&1
rm -rf "$perfil"
echo "$png"
