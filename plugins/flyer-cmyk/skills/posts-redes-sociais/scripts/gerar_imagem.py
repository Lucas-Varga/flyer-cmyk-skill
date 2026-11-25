"""Imagens para a arte: gerar com IA, editar uma imagem do usuário com IA, ou melhorar a
qualidade (local, sem IA, ou com IA).

A chave fica num arquivo .env (nunca no código nem no chat):
    OPENAI_API_KEY=...        provedor openai     (modelo: o melhor disponível na conta)
    GEMINI_API_KEY=...        provedor google     (gemini-2.5-flash-image)
    STABILITY_API_KEY=...     provedor stability  (Stable Image Core; só gerar)
O .env é procurado na pasta atual e nas acima; sem ele, vale a variável de ambiente de
mesmo nome. A chave nunca é impressa.

Modos:
  gerar     imagem nova a partir de um prompt
            gerar_imagem.py gerar --prompt "..." --mm 154x216 --saida fotos/fundo.png
  editar    altera/recria uma ou mais imagens do usuário seguindo uma instrução
            (a 1ª imagem é a base; as demais são referências)
            gerar_imagem.py editar --imagem materiais/foto.jpg --prompt "troque o fundo por..."
                                   --mm 100x80 --saida fotos/foto-editada.png
  melhorar  aumenta a resolução para o tamanho de impressão e dá nitidez
            --local (padrão): sem IA, não muda o conteúdo (Lanczos + nitidez + redução de ruído)
            --ia: com IA, recupera detalhe, mas pode alterar pequenos detalhes; confira
            gerar_imagem.py melhorar --imagem materiais/foto.jpg --mm 100x80 --saida fotos/foto.png

Tamanho: --mm LxA (impressão, com --dpi) ou --px LxA (redes sociais, pixels finais).
Opções comuns: --provedor openai|google|stability, --modelo auto|<id>, --qualidade high,
--dpi 300, --permitir-texto (por padrão a IA é instruída a não pôr texto nem logos).

Ao lado de cada saída fica um .json com modo, provedor, modelo, prompt, origem e data.
Testado: openai (gerar, editar, melhorar). google e stability seguem a documentação pública.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

CHAVES = {'openai': 'OPENAI_API_KEY', 'google': 'GEMINI_API_KEY', 'stability': 'STABILITY_API_KEY'}
MODELO_PADRAO = {'openai': 'auto', 'google': 'gemini-2.5-flash-image',
                 'stability': 'stable-image-core'}
SEM_TEXTO = (' Absolutely no text, letters, numbers, words, signage, logos, brand names or '
             'watermarks anywhere in the image.')
MELHORAR_IA = ('Enhance this exact image for high-quality print: increase sharpness and fine '
               'detail, remove noise, blur and compression artifacts, improve lighting '
               'naturally. Keep the composition, framing, people, faces, objects, text, colors '
               'and proportions exactly the same. Do not add or remove anything.')
PROPORCOES = {
    '1:1': 1, '2:3': 2 / 3, '3:2': 3 / 2, '3:4': 3 / 4, '4:3': 4 / 3, '4:5': 4 / 5,
    '5:4': 5 / 4, '9:16': 9 / 16, '16:9': 16 / 9, '21:9': 21 / 9, '9:21': 9 / 21,
}


# ── chave e modelo ───────────────────────────────────────────────────────────
def ler_chave(provedor: str, env: str | None = None) -> str:
    nome = CHAVES[provedor]
    alias = {nome, 'GOOGLE_API_KEY'} if provedor == 'google' else {nome}
    candidatos = [Path(env)] if env else [p / '.env' for p in [Path.cwd(), *Path.cwd().parents]]
    for arq in candidatos:
        if arq.is_file():
            for linha in arq.read_text().splitlines():
                linha = linha.strip()
                if not linha or linha.startswith('#') or '=' not in linha:
                    continue
                k, v = linha.split('=', 1)
                k = k.strip().removeprefix('export ').strip()
                if k in alias and v.strip():
                    return v.strip().strip('"').strip("'")
    for k in alias:
        if os.environ.get(k):
            return os.environ[k]
    sys.exit(f'Chave não encontrada. Crie um arquivo .env na pasta do trabalho com a linha\n'
             f'  {nome}=sua-chave\n(e mantenha o .env fora do git).')


def melhor_modelo_openai(cli) -> str:
    """Escolhe o melhor modelo de imagem da conta: a versão mais alta de gpt-image-*;
    entre variantes da mesma versão, 'sunburst' (qualidade) > base > 'flare' (rapidez);
    ignora 'mini' e snapshots datados."""
    ids = [m.id for m in cli.models.list() if m.id.startswith('gpt-image-')]
    melhores = []
    for i in ids:
        m = re.fullmatch(r'gpt-image-(\d+(?:\.\d+)?)(?:-([a-z]+))?', i)
        if not m or m.group(2) == 'mini':
            continue
        variante = {'sunburst': 2, None: 1, 'flare': 0}.get(m.group(2), 0)
        melhores.append((float(m.group(1)), variante, i))
    if not melhores:
        return 'gpt-image-1'
    return max(melhores)[2]


# ── tamanhos ────────────────────────────────────────────────────────────────
def _px(mm, dpi, multiplo=16, max_lado=3840):
    w, h = (round(v / 25.4 * dpi / multiplo) * multiplo for v in mm)
    k = min(1.0, max_lado / max(w, h))
    return (max(multiplo, int(w * k) // multiplo * multiplo),
            max(multiplo, int(h * k) // multiplo * multiplo))


def _proporcao(mm) -> str:
    r = mm[0] / mm[1]
    return min(PROPORCOES, key=lambda k: abs(PROPORCOES[k] - r))


def _tentativas(mm, dpi, px=None):
    r = mm[0] / mm[1]
    base = '1024x1536' if r < 0.85 else '1536x1024' if r > 1.18 else '1024x1024'
    vistos, out = set(), []
    primeiros = [_px(mm, dpi), _px(mm, dpi, max_lado=2560), _px(mm, dpi, max_lado=2048)]
    if px:  # alvo em pixels (redes sociais): arredonda PARA CIMA em múltiplos de 16
        teto = lambda v: -(-int(v) // 16) * 16
        primeiros = [(teto(px[0]), teto(px[1]))] + primeiros
    for t in (*primeiros, base):
        tam = t if isinstance(t, str) else f'{t[0]}x{t[1]}'
        if tam not in vistos:
            vistos.add(tam)
            out.append(tam)
    return out


# ── provedores ──────────────────────────────────────────────────────────────
def openai_imagem(chave, prompt, mm, dpi, modelo, qualidade, imagens=None, px=None):
    from openai import BadRequestError, OpenAI
    cli = OpenAI(api_key=chave)
    if modelo == 'auto':
        modelo = melhor_modelo_openai(cli)
    ultimo = None
    extra = {'input_fidelity': 'high'}  # modelos mais novos já preservam e recusam o parâmetro
    for tam in _tentativas(mm, dpi, px):
        try:
            if imagens:
                arqs = [open(p, 'rb') for p in imagens]
                try:
                    try:
                        resp = cli.images.edit(model=modelo, image=arqs, prompt=prompt, size=tam,
                                               quality=qualidade, n=1, **extra)
                    except BadRequestError as e:
                        if 'input_fidelity' not in str(e) or not extra:
                            raise
                        extra = {}
                        for f in arqs:
                            f.seek(0)
                        resp = cli.images.edit(model=modelo, image=arqs, prompt=prompt, size=tam,
                                               quality=qualidade, n=1)
                finally:
                    for f in arqs:
                        f.close()
            else:
                resp = cli.images.generate(model=modelo, prompt=prompt, size=tam, n=1,
                                           quality=qualidade)
            d = resp.data[0]
            return base64.b64decode(d.b64_json), modelo, {
                'tamanho_pedido': tam, 'prompt_revisado': getattr(d, 'revised_prompt', None)}
        except BadRequestError as e:
            ultimo = e
            msg = str(e).lower()
            if 'size' not in msg and 'pixel' not in msg and 'dimension' not in msg:
                raise
            print(f'  {tam} não aceito; tentando menor…', file=sys.stderr)
    raise ultimo


def google_imagem(chave, prompt, mm, dpi, modelo, qualidade, imagens=None, px=None):
    import httpx
    prop = _proporcao(mm)
    partes = [{'text': prompt}]
    for p in imagens or []:
        mime = 'image/png' if str(p).lower().endswith('.png') else 'image/jpeg'
        partes.append({'inline_data': {'mime_type': mime,
                                       'data': base64.b64encode(Path(p).read_bytes()).decode()}})
    corpo = {'contents': [{'parts': partes}],
             'generationConfig': {'responseModalities': ['IMAGE'],
                                  'imageConfig': {'aspectRatio': prop}}}
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent'
    r = httpx.post(url, json=corpo, headers={'x-goog-api-key': chave}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f'Google {r.status_code}: {r.text[:500]}')
    for parte in r.json()['candidates'][0]['content']['parts']:
        dados = parte.get('inlineData') or parte.get('inline_data')
        if dados:
            return base64.b64decode(dados['data']), modelo, {'proporcao': prop}
    raise RuntimeError('Google não devolveu imagem (verifique o modelo e a política de conteúdo)')


def stability_imagem(chave, prompt, mm, dpi, modelo, qualidade, imagens=None, px=None):
    import httpx
    if imagens:
        raise RuntimeError('editar/melhorar com IA: use --provedor openai ou google')
    prop = _proporcao(mm)
    r = httpx.post('https://api.stability.ai/v2beta/stable-image/generate/core',
                   headers={'Authorization': f'Bearer {chave}', 'Accept': 'image/*'},
                   files={'none': ''},
                   data={'prompt': prompt, 'aspect_ratio': prop, 'output_format': 'png'},
                   timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f'Stability {r.status_code}: {r.text[:500]}')
    return r.content, modelo, {'proporcao': prop}


PROVEDORES = {'openai': openai_imagem, 'google': google_imagem, 'stability': stability_imagem}


# ── melhorar sem IA ─────────────────────────────────────────────────────────
def melhorar_local(origem: Path, mm, dpi) -> bytes:
    """Amplia até o tamanho de impressão (Lanczos), reduz ruído leve e aplica nitidez.
    Não inventa detalhe: uma foto muito pequena continua com pouca informação."""
    import io
    from PIL import Image, ImageFilter
    im = Image.open(origem).convert('RGB')
    alvo = mm[0] / mm[1]
    W, H = im.size
    if W / H > alvo:  # corta (cover) na proporção do quadro
        nw = round(H * alvo)
        im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
    else:
        nh = round(W / alvo)
        im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    px_w = round(mm[0] / 25.4 * dpi)
    if im.size[0] < px_w:
        im = im.filter(ImageFilter.MedianFilter(3)) if im.size[0] < px_w / 2 else im
        im = im.resize((px_w, round(px_w / alvo)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
    buf = io.BytesIO()
    im.save(buf, 'PNG')
    return buf.getvalue()


# ── principal ───────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('modo', nargs='?', default='gerar', choices=['gerar', 'editar', 'melhorar'])
    ap.add_argument('--prompt', default='')
    ap.add_argument('--imagem', nargs='*', default=[], help='imagem(ns) do usuário (editar/melhorar)')
    ap.add_argument('--saida', required=True)
    ap.add_argument('--mm', default=None, help='tamanho de uso na arte impressa, ex.: 154x216')
    ap.add_argument('--px', default=None,
                    help='tamanho final em pixels (redes sociais), ex.: 1080x1350; gera no múltiplo '
                         'de 16 logo acima (recorte final com finalizar_post.py)')
    ap.add_argument('--escala', type=float, default=1.0,
                    help='com --px: gera maior (ex.: 1.5) para texto mais nítido após reduzir')
    ap.add_argument('--provedor', default='openai', choices=list(PROVEDORES))
    ap.add_argument('--modelo', default=None, help='auto (padrão no openai) ou um id')
    ap.add_argument('--qualidade', default='high', help='openai: low|medium|high')
    ap.add_argument('--dpi', type=int, default=300)
    ap.add_argument('--env', default=None, help='caminho do .env (padrão: procura)')
    ap.add_argument('--ia', action='store_true', help='melhorar: usar IA em vez do método local')
    ap.add_argument('--permitir-texto', action='store_true',
                    help='não pedir "sem texto" (a IA erra letras; deixe o texto na arte)')
    a = ap.parse_args()

    px = None
    if a.px:
        px = tuple(float(v) * a.escala for v in a.px.lower().split('x'))
        mm = tuple(v * 25.4 / 300 for v in px)  # equivalente a 300 dpi
        a.dpi = 300
    elif a.mm:
        mm = tuple(float(v) for v in a.mm.lower().split('x'))
    else:
        sys.exit('informe --mm (impressão) ou --px (redes sociais)')
    if a.modo in ('editar', 'melhorar') and not a.imagem:
        sys.exit('informe --imagem')
    if a.modo == 'gerar' and not a.prompt:
        sys.exit('informe --prompt')
    for p in a.imagem:
        if not Path(p).is_file():
            sys.exit(f'imagem não encontrada: {p}')

    meta, modelo, prov = {}, None, None
    if a.modo == 'melhorar' and not a.ia:
        print(f'Melhorando localmente (sem IA) para {mm[0]:g}×{mm[1]:g} mm a {a.dpi} dpi…')
        dados = melhorar_local(Path(a.imagem[0]), mm, a.dpi)
        prompt = None
    else:
        prov = a.provedor
        modelo = a.modelo or MODELO_PADRAO[prov]
        if a.modo == 'melhorar':
            prompt = MELHORAR_IA
        else:
            # em edições, o usuário pode querer manter texto existente na foto
            prompt = a.prompt + ('' if a.permitir_texto or a.modo == 'editar' else SEM_TEXTO)
        chave = ler_chave(prov, a.env)
        print(f'{a.modo.capitalize()} com {prov}/{modelo} para {mm[0]:g}×{mm[1]:g} mm…')
        dados, modelo, meta = PROVEDORES[prov](chave, prompt, mm, a.dpi, modelo, a.qualidade,
                                               a.imagem if a.modo != 'gerar' else None, px)

    saida = Path(a.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(dados)
    from PIL import Image
    with Image.open(saida) as im:
        w, h = im.size
    ppi = min(w / (mm[0] / 25.4), h / (mm[1] / 25.4))
    info = {'modo': a.modo, 'provedor': prov or 'local', 'modelo': modelo, 'prompt': prompt,
            'origem': a.imagem, 'pixels': [w, h], 'uso_mm': list(mm), 'ppi_no_uso': round(ppi),
            'gerado_em': dt.datetime.now().isoformat(), **meta}
    saida.with_suffix('.json').write_text(json.dumps(info, ensure_ascii=False, indent=2))
    if px:
        print(f'OK: {saida} ({w}×{h} px para {a.px}' + (f'; modelo {modelo}' if modelo else '') + ')')
        return
    print(f'OK: {saida} ({w}×{h} px, {ppi:.0f} ppi em {mm[0]:g}×{mm[1]:g} mm'
          + (f'; modelo {modelo}' if modelo else '') + ')')
    if ppi < 200:
        print('Atenção: abaixo de 200 ppi pode sair borrado; use a imagem menor na arte, '
              'use "melhorar" ou gere de novo maior.')


if __name__ == '__main__':
    main()
