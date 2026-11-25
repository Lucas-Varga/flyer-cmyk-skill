"""EXEMPLO: flyer A5 frente e verso de uma empresa FICTÍCIA ("Oficina Exemplo").

Serve de ponto de partida para o `montar.py` de um trabalho real:
1. copie esta pasta (montar.py + marca/) para a pasta do trabalho;
2. copie para ela também ../../scripts/impressao.py e ../../scripts/pdf_cmyk.py;
3. troque DADOS, PALETA, FONTES e as coordenadas pelo que o agente de design especificar.

Todas as coordenadas abaixo são em mm a partir do canto de CORTE (os métodos da classe
Face somam a sangria). Texto: y = linha de base.

    python montar.py --guias      # SVG com guias de corte e margem de segurança
    python montar.py --pdf        # SVG finais + PDF/X-1a CMYK para a gráfica

Fontes: o exemplo usa a Arial do macOS só para rodar sem nada a instalar. Num trabalho
real, use as fontes da marca (pasta fontes/).
"""
import sys
from pathlib import Path

import impressao
from impressao import Arte, Cmyk, Fonte, _ICONES, quebrar

PASTA = Path(__file__).resolve().parent
impressao.usar_pasta(PASTA)

# ── conteúdo (FICTÍCIO: num trabalho real, vem do usuário e do agente de marketing) ──
DADOS = {
    'empresa': 'Oficina Exemplo',
    'rotulo_topo': 'Programa de indicação',
    'titulo': ['Indique um amigo.', 'Vocês dois ganham.'],
    'amigo_ganha': 'Higienização do ar-condicionado',
    'amigo_cond': 'no primeiro serviço. Só para quem ainda não é cliente.',
    'voce_ganha': 'Um brinde a cada amigo',
    'voce_cond': 'que fizer o primeiro serviço com o seu nome.',
    'passos': [
        ('Passe o seu nome para um amigo.', 'Ou mande o link do site pelo WhatsApp.'),
        ('Ele diz o seu nome no balcão.', 'Sem cadastro. Ninguém vai ligar pra ele.'),
        ('Ele faz o 1º serviço e vocês ganham.', 'Seu brinde fica separado no balcão.'),
    ],
    'cta': 'Veja as regras no site',
    'cta_nota': ['Os 4 brindes estão', 'no verso.'],
    'url_site': 'https://example.com/indique',
    'qr_legenda': 'Abrir o site',
    'titulo_verso': 'Seus brindes, um a cada amigo',
    'brindes': ['Kit de limpeza automotiva', 'Alinhamento e balanceamento',
                'Revisão de freios', 'Lavagem completa'],
    'ciclo': 'Depois do 4º, a lista recomeça. Sem limite de indicações.',
    'como_retirar': 'Avise no balcão que você indicou alguém. O brinde não tem prazo '
                    'e pode ser retirado por quem você mandar.',
    'quem_participa': 'Clientes da oficina indicam. O amigo indicado precisa ser '
                      'cliente novo. Um brinde por amigo.',
    'endereco': ['Rua Exemplo, 123', 'Centro, Cidade – UF'],
    'horario': 'Segunda a sexta, 8h às 18h',
    'whatsapp': 'WhatsApp: (00) 00000-0000',
    'url_whatsapp': 'https://wa.me/5500000000000',
    'url_mapa': 'https://maps.google.com/?q=Rua+Exemplo+123',
    'confianca': 'Sem cadastro. Ninguém vai te ligar.',
    'legal': 'Programa de indicação da Oficina Exemplo. Participam clientes da oficina; '
             'pode ser indicado só quem nunca fez serviço nela. A indicação vale quando o '
             'amigo faz e paga o primeiro serviço. Cada novo cliente gera um brinde, uma '
             'vez só. Brinde sem prazo, não vale como dinheiro. Válido até 31/12/2027. '
             'Regras completas: example.com/indique',
}

# ── paleta CMYK (Coated FOGRA39) + cor de tela para prévia ──
NOITE = Cmyk('Noite', 60, 0, 0, 100, '#0B0D10')       # fundo escuro grande (160%)
VERM = Cmyk('Vermelho', 0, 95, 85, 0, '#D62828')      # só CTA e marca
PRETO = Cmyk('Preto', 0, 0, 0, 100, '#1E1F21')        # texto sobre claro
GRAF = Cmyk('Grafite', 0, 0, 0, 75, '#4B4F56')        # rótulos, legal
LINHA = Cmyk('Linha', 0, 0, 0, 25, '#C4C7CC')
ESTUDIO = Cmyk('Estudio', 0, 0, 0, 4, '#F3F4F5')      # fundo claro
PAPEL = Cmyk('Papel', 0, 0, 0, 0, '#FFFFFF')
PAPEL_T = Cmyk('Papel (texto)', 0, 0, 0, 0, '#F3F2EF')

# ── fontes e estilos: (fonte, pt, rastreio_em, caixa_alta) ──
BOLD = Fonte('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
REG = Fonte('/System/Library/Fonts/Supplemental/Arial.ttf')
TIT1 = (BOLD, 28, -0.01, False)
TIT2 = (BOLD, 15, 0, False)
TIT3 = (BOLD, 13, 0, False)
DEST = (BOLD, 12, 0, False)
CORPO = (REG, 11, 0, False)
ROT = (BOLD, 9, 0.08, True)
LEG = (REG, 9, 0, False)
LEGAL = (REG, 8, 0, False)

_ICONES['ciclo'] = ('<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3" fill="none" stroke-linecap="round" '
                    'stroke-width="2.2"/><path d="M18.6 2.8l.2 4.6-4.6.2" fill="none" '
                    'stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2"/>')
S = 3.0  # sangria (mm)


class Face(Arte):
    """Arte com atalhos em coordenadas de CORTE (somam a sangria)."""

    def t(self, est, txt, x, y, cor, ancora='inicio'):
        f, pt, r, cx = est
        return self.texto(f, txt, x + S, y + S, pt, cor, ancora, r, cx)

    def p(self, est, txt, x, y, cor, largura, entrelinha=1.3, max_linhas=None):
        """Parágrafo com quebra automática; devolve o y da próxima linha."""
        f, pt, r, _ = est
        linhas = quebrar(f, txt, pt, largura, r)
        if max_linhas and len(linhas) > max_linhas:
            raise ValueError(f'texto passa de {max_linhas} linhas: {txt!r}')
        passo = pt * impressao.PT * entrelinha
        for i, ln in enumerate(linhas):
            self.texto(f, ln, x + S, y + S + i * passo, pt, cor, 'inicio', r)
        return y + len(linhas) * passo

    def r(self, x, y, w, h, cor=None, **kw):
        self.ret(x + S, y + S, w, h, cor, **kw)

    def ic(self, nome, x, y, tam, cor):
        self.icone(nome, x + S, y + S, tam, cor)

    def q(self, url, x, y, lado):
        self.qr(url, x + S, y + S, lado, PRETO, PAPEL)


def frente():
    D = DADOS
    a = Face(148, 210, titulo=f'{D["empresa"]}: flyer A5, frente')
    a.ret(0, 0, a.L, a.A, NOITE)
    a.logo('logo-escuro.svg', 10 + S, 9 + S, 40, {'#FFFFFF': PAPEL, '#D62828': VERM})
    a.t(ROT, D['rotulo_topo'], 138, 16, PAPEL_T, 'fim')
    a.t(TIT1, D['titulo'][0], 10, 40, PAPEL_T)
    a.t(TIT1, D['titulo'][1], 10, 51, PAPEL_T)

    a.t(ROT, 'Seu amigo ganha', 10, 66, PAPEL_T)
    a.t(TIT2, D['amigo_ganha'], 10, 73, PAPEL_T)
    a.p(CORPO, D['amigo_cond'], 10, 79, PAPEL_T, 128, max_linhas=1)
    a.t(ROT, 'Você ganha', 10, 90, PAPEL_T)
    a.t(TIT2, D['voce_ganha'], 10, 97, PAPEL_T)
    a.p(CORPO, D['voce_cond'], 10, 103, PAPEL_T, 128, max_linhas=1)

    a.t(ROT, 'Como funciona', 10, 116, PAPEL_T)
    for i, (frase, sub) in enumerate(D['passos']):
        c = 123 + 12.5 * i
        a.circulo(13.25 + S, c + S, 3.25, None, PAPEL_T, 0.35)
        a.t(TIT3, str(i + 1), 13.25, c + 1.6, PAPEL_T, 'meio')
        a.t(DEST, frase, 20, c + 1.5, PAPEL_T)
        a.t(CORPO, sub, 20, c + 6.6, PAPEL_T)

    # CTA (pílula vermelha) + QR do site
    a.r(10, 170, 82, 12, VERM, r=6)
    a.t(DEST, D['cta'], 51, 177.9, PAPEL_T, 'meio')
    a.t(CORPO, D['cta_nota'][0], 10, 193, PAPEL_T)
    a.t(CORPO, D['cta_nota'][1], 10, 198.2, PAPEL_T)
    a.q(D['url_site'], 112, 166, 26)
    a.t(LEG, D['qr_legenda'], 125, 197, PAPEL_T, 'meio')
    return a


def verso():
    D = DADOS
    a = Face(148, 210, titulo=f'{D["empresa"]}: flyer A5, verso')
    a.ret(0, 0, a.L, a.A, ESTUDIO)
    a.t(TIT2, D['titulo_verso'], 10, 15, PRETO)
    a.logo('logo-claro.svg', 106 + S, 8.5 + S, 32,
           {'#1E1F21': PRETO, '#FFFFFF': PAPEL, '#D62828': VERM})

    for i, nome in enumerate(D['brindes']):
        qx, qy = (10, 76)[i % 2], (22, 45)[i // 2]
        a.r(qx, qy, 62, 20, PAPEL, r=2.5, traco=LINHA, traco_mm=0.3)
        a.t(ROT, f'{i + 1}º amigo', qx + 4, qy + 6, GRAF)
        a.p(DEST, nome, qx + 4, qy + 12, PRETO, 54, entrelinha=1.15, max_linhas=2)
    a.ic('ciclo', 10, 68, 4.5, GRAF)
    a.t(CORPO, D['ciclo'], 16.5, 71.6, PRETO)

    a.t(TIT3, 'Como retirar', 10, 84, PRETO)
    a.p(CORPO, D['como_retirar'], 10, 90, PRETO, 62, max_linhas=5)
    a.t(TIT3, 'Quem participa', 78, 84, PRETO)
    a.p(CORPO, D['quem_participa'], 78, 90, PRETO, 60, max_linhas=5)

    # Como chegar (+ foto real, se existir fotos/fachada.jpg)
    y0 = 114
    x_txt = 10
    foto = PASTA / 'fotos' / 'fachada.jpg'
    if foto.exists():
        a.imagem(foto, 10 + S, y0 + S, 30, 25, r=1.5)
        x_txt = 44
    a.t(TIT3, 'Como chegar', x_txt, y0 + 4.5, PRETO)
    yy = y0 + 10.5
    for ln in D['endereco'] + [D['horario'], D['whatsapp']]:
        a.t(CORPO, ln, x_txt, yy, PRETO)
        yy += 5.2
    a.q(D['url_whatsapp'], 100, y0, 18)
    a.q(D['url_mapa'], 120, y0, 18)
    a.t(LEG, 'WhatsApp', 109, y0 + 22, PRETO, 'meio')
    a.t(LEG, 'Mapa', 129, y0 + 22, PRETO, 'meio')

    a.ic('check', 10, 150.4, 4.5, GRAF)
    a.t(DEST, D['confianca'], 16.5, 154, PRETO)
    a.p(LEGAL, D['legal'], 10, 172, GRAF, 128, entrelinha=1.25, max_linhas=7)
    return a


if __name__ == '__main__':
    guias = '--guias' in sys.argv
    out = PASTA / 'saida'
    out.mkdir(exist_ok=True)
    (out / 'flyer-frente.svg').write_text(frente().svg(guias))
    (out / 'flyer-verso.svg').write_text(verso().svg(guias))
    if '--pdf' in sys.argv:
        from pdf_cmyk import gerar_pdf
        slug = 'Flyer A5 148×210 mm · sangria 3 mm · CMYK FOGRA39 · '
        gerar_pdf([frente(), verso()], out / 'flyer-grafica.pdf',
                  f'{DADOS["empresa"]}: flyer A5 (frente e verso)',
                  [slug + 'FRENTE', slug + 'VERSO (cabeça com cabeça)'], REG,
                  autor=DADOS['empresa'])
    print('ok')
