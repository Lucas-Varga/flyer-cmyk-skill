"""Flyer A5 — inauguração da Ápice Academia (empresa e dados FICTÍCIOS).
Implementação literal de 03-design.md. Coordenadas da especificação = canto de CORTE;
a classe Face soma a sangria (+3) em tudo, inclusive paths e degradês.

    python montar.py --guias     # SVG com guias de corte e margem
    python montar.py --pdf       # SVG finais + PDF/X-1a + máscara de verniz
"""
import re
import sys
from pathlib import Path

import impressao
from impressao import Arte, Cmyk, Degrade, Fonte, formato

PASTA = Path(__file__).resolve().parent
impressao.usar_pasta(PASTA)
S = 3.0

# ── paleta (03-design §2) ──
NOITE = Cmyk('Noite', 60, 0, 0, 100)
LARANJA = Cmyk('Laranja Ápice', 0, 75, 95, 0)
AMBAR = Cmyk('Âmbar', 0, 45, 95, 0)
BRANCO = Cmyk('Branco', 0, 0, 0, 0, '#ffffff')
PRETO = Cmyk('Preto texto', 0, 0, 0, 100)
FIO = Cmyk('Cinza fio', 0, 0, 0, 40)


def g(paradas, inicio, fim):  # degradê em coordenadas de corte
    return Degrade(paradas, inicio=(inicio[0] + S, inicio[1] + S), fim=(fim[0] + S, fim[1] + S))


G1 = g([(0, LARANJA), (1, AMBAR)], (-3, 122), (151, 88))
G1V = g([(0, LARANJA), (1, AMBAR)], (-3, 107.5), (151, 98))
G2 = g([(0, AMBAR), (1, LARANJA)], (0, 36.0), (0, 60.0))

# ── fontes (03-design §3) ──
FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
AVENIR = '/System/Library/Fonts/Avenir Next.ttc'
AVENIR_C = '/System/Library/Fonts/Avenir Next Condensed.ttc'
E1 = Fonte(FUTURA, 4)       # Futura Condensed ExtraBold
E2 = Fonte(AVENIR, 8)       # Avenir Next Heavy
E3 = Fonte(AVENIR, 2)       # Avenir Next Demi Bold
E4 = Fonte(AVENIR, 0)       # Avenir Next Bold
E5 = Fonte(AVENIR, 5)       # Avenir Next Medium (corpo e legal)
E6 = Fonte(AVENIR_C, 0)     # Avenir Next Condensed Bold
E7 = Fonte(AVENIR_C, 2)     # Avenir Next Condensed Demi Bold

LOGO_CORES = {'#FF5A1F': LARANJA, '#FFFFFF': BRANCO}


def desloca(d: str) -> str:
    """Soma a sangria a todos os pares x,y de um path só com M/L/Z absolutos."""
    nums = iter(re.findall(r'-?\d+(?:\.\d+)?', d))
    return re.sub(r'(-?\d+(?:\.\d+)?)[ ,]+(-?\d+(?:\.\d+)?)',
                  lambda m: f'{float(m.group(1)) + S:.3f} {float(m.group(2)) + S:.3f}', d)


class Face(Arte):
    def t(self, f, pt, txt, x, y, cor, ancora='inicio', rastreio=0.0, caixa=False):
        return self.texto(f, txt, x + S, y + S, pt, cor, ancora, rastreio, caixa)

    def r(self, x, y, w, h, cor=None, **kw):
        self.ret(x + S, y + S, w, h, cor, **kw)

    def c(self, cx, cy, r, cor=None, **kw):
        self.circulo(cx + S, cy + S, r, cor, **kw)

    def ic(self, nome, x, y, tam, cor):
        self.icone(nome, x + S, y + S, tam, cor)

    def q(self, url, x, y, lado):
        self.qr(url, x + S, y + S, lado, PRETO, BRANCO)

    def f(self, d, cor):
        self.forma(desloca(d), cor)


def frente():
    L, A = formato('A5')
    a = Face(L, A, titulo='Ápice Academia — flyer A5 — FRENTE', papel='couche')
    a.ret(0, 0, a.L, a.A, NOITE)                                               # F01
    a.imagem('img1-bike-editada.png', 0, 0, 154, 121,                          # F02 (janelas → parede, editada com IA)
             efeitos=[('escurecer', NOITE, 0.20), ('fade', 'baixo', NOITE, 0.50, 0.90)])
    a.logo('logo-escuro.svg', 9 + S, 9 + S, 34, LOGO_CORES)                    # F03
    faixa = 'M -3 94 L 151 88 L 151 116 L -3 122 Z'
    a.f(faixa, G1)                                                             # F04
    a.t(E1, 50, 'INAUGURAÇÃO', 74, 109.5, NOITE, 'meio', 0.01)                 # F05
    a.t(E1, 24, 'SÁBADO, 6 DE MARÇO', 9, 134.0, BRANCO, rastreio=0.01)         # F06
    a.t(E1, 24, '· 8H ÀS 18H', 94.17, 134.0, AMBAR, rastreio=0.01)             # F07
    a.t(E2, 18, 'Aulas experimentais', 9, 147.0, BRANCO)                       # F08
    a.t(E2, 18, 'grátis o dia todo', 9, 154.5, BRANCO)                         # F09
    a.t(E5, 10, 'Musculação, treino funcional, bike indoor', 9, 163.0, BRANCO)  # F10
    a.t(E5, 10, 'e ritmos.', 9, 167.6, BRANCO)                                 # F11
    a.t(E3, 10, 'Sem compromisso.', 23.80, 167.6, BRANCO)                      # F12
    a.c(120, 158.5, 20, None, traco=BRANCO, traco_mm=0.8)                      # F13
    a.t(E7, 8.5, 'MATRÍCULA ISENTA', 120, 149.0, BRANCO, 'meio', 0.04)         # F14
    a.t(E7, 8.5, '+ 1º MÊS', 120, 154.0, BRANCO, 'meio', 0.04)                 # F15
    a.t(E1, 11, 'R$', 104.30, 162.05, AMBAR)                                   # F16
    a.t(E1, 24, '49,90', 110.14, 165.5, AMBAR)                                 # F17
    a.t(E1, 11, '*', 133.36, 165.5, AMBAR)                                     # F18
    a.t(E5, 7, '*Condições no verso.', 120, 172.0, BRANCO, 'meio')             # F19
    a.ic('pino', 9, 189.0, 5, BRANCO)                                          # F20
    a.t(E3, 10, 'Av. Exemplo, 1000 – Centro', 15.5, 192.75, BRANCO)            # F21
    a.r(72.78, 186.0, 66.22, 11, BRANCO, r=5.5)                                # F22
    a.t(E4, 15, 'VENHA CONHECER', 105.89, 193.43, PRETO, 'meio', 0.06)         # F23
    a.t(E5, 7, 'Imagens meramente ilustrativas.', 9, 203.0, BRANCO)            # F24

    with a.acabamento('verniz-uv'):                                            # §5 frente
        a.f('M 9 23.245 L 14.759 11.122 L 20.517 23.245 L 17.244 23.245 '
            'L 14.759 17.668 L 12.273 23.245 Z', PRETO)                        # pico do logo
        a.t(E1, 50, 'INAUGURAÇÃO', 74, 109.5, PRETO, 'meio', 0.01)
        a.t(E1, 24, 'SÁBADO, 6 DE MARÇO', 9, 134.0, PRETO, rastreio=0.01)
        a.t(E1, 24, '· 8H ÀS 18H', 94.17, 134.0, PRETO, rastreio=0.01)
    return a


def verso():
    L, A = formato('A5')
    a = Face(L, A, titulo='Ápice Academia — flyer A5 — VERSO', papel='couche')
    a.ret(0, 0, a.L, a.A, BRANCO)                                              # V01
    a.f('M -3 -3 L 151 -3 L 151 98 L -3 104 Z', NOITE)                         # V02
    a.f('M -3 104 L 151 98 L 151 101.5 L -3 107.5 Z', G1V)                     # V03
    a.logo('logo-escuro.svg', 113 + S, 9 + S, 26, LOGO_CORES)                  # V04
    a.t(E3, 12, 'OFERTA DE INAUGURAÇÃO', 9, 17.0, BRANCO, rastreio=0.06)        # V05
    a.t(E3, 10, 'PLANO MENSAL · 1º MÊS', 9, 31.0, BRANCO, rastreio=0.08)        # V06
    a.t(E1, 30, 'R$', 9.00, 44.04, G2)                                         # V07
    a.t(E1, 90, '49', 22.95, 60.0, G2)                                         # V08
    a.t(E1, 45, ',90', 61.75, 48.25, G2)                                       # V09
    a.t(E3, 12, 'Depois, R$ 119,90/mês.', 9, 68.0, BRANCO)                     # V10
    a.t(E5, 9, 'Novas matrículas de 06/03 a 31/03/2027.', 9, 74.0, BRANCO)     # V11
    a.c(116.5, 50.5, 22, AMBAR)                                                # V12
    a.t(E1, 18, 'MATRÍCULA', 116.5, 45.5, PRETO, 'meio', 0.01)                 # V13
    a.t(E1, 28, 'ISENTA', 116.5, 55.5, PRETO, 'meio', 0.01)                    # V14
    a.t(E3, 8.5, 'valor normal: R$ 80,00', 116.5, 62.5, PRETO, 'meio')         # V15
    a.linha(9 + S, 80 + S, 139 + S, 80 + S, BRANCO, 0.25)                      # V16
    a.t(E3, 10, 'PLANO ANUAL', 9, 88.5, BRANCO, rastreio=0.06)                 # V17
    a.t(E5, 9.5, 'R$ 99,90/mês em 12x no cartão, com matrícula isenta.', 38.2, 88.5, BRANCO)  # V18

    a.t(E4, 13, 'Comece no seu ritmo', 9, 115.0, PRETO)                        # V19
    for txt, y in zip(['Avaliação física e plano de treino',
                       'montado por profissional de educação',
                       'física, inclusos em todos os planos.'], [120.5, 124.8, 129.1]):
        a.t(E5, 9.5, txt, 9, y, PRETO)                                         # V20
    a.t(E3, 8.5, 'ESTRUTURA', 9, 139.5, PRETO, rastreio=0.10)                  # V21
    for txt, y in [('1.200 m² em 2 andares', 145.5), ('Estacionamento com 40 vagas', 151.0),
                   ('Ar-condicionado', 156.5), ('Equipamentos novos', 162.0)]:  # V22–V25
        a.ic('check', 9, y - 2.94, 4, PRETO)
        a.t(E5, 9.5, txt, 14.5, y, PRETO)
    a.ic('pino', 9, 169.3, 4, PRETO)                                           # V26
    a.t(E5, 8.5, 'Av. Exemplo, 1000 – Centro', 14.5, 172.3, PRETO)
    a.t(E5, 8.5, 'Cidade Exemplo – UF', 14.5, 176.1, PRETO)
    a.ic('site', 9, 179.2, 4, PRETO)                                           # V27
    a.t(E5, 8.5, 'example.com/apice', 14.5, 182.2, PRETO)
    a.ic('instagram', 9, 185.2, 4, PRETO)                                      # V28
    a.t(E5, 8.5, '@academia.exemplo', 14.5, 188.2, PRETO)

    a.ic('relogio', 80, 109.4, 5, PRETO)                                       # V29
    a.t(E3, 8.5, 'HORÁRIOS A PARTIR DE 08/03', 87, 113.5, PRETO, rastreio=0.06)  # V30
    a.t(E3, 10, 'Seg. a sex.: 5h30 às 23h', 87, 119.3, PRETO)                  # V31
    a.t(E5, 9, 'Sábado: 8h às 14h', 87, 123.8, PRETO)                          # V32
    a.t(E5, 9, 'Domingo e feriados: 8h às 12h', 87, 128.2, PRETO)              # V33
    a.t(E3, 9, 'Garanta sua matrícula isenta até 31/03.', 80, 137.5, PRETO)   # V34
    a.r(80, 141.0, 59, 10, LARANJA, r=5)                                       # V35
    a.t(E6, 14, 'CHAME NO WHATSAPP', 109.5, 147.8, BRANCO, 'meio', 0.04)       # V36
    a.q('https://wa.me/5500000000000', 80, 155, 26)                            # V37
    a.q('https://maps.google.com/?q=Av.+Exemplo+1000', 113, 155, 26)           # V38
    a.t(E3, 8.5, 'WhatsApp', 93, 184.6, PRETO, 'meio')                         # V39
    a.t(E5, 8.5, '(00) 00000-0000', 93, 188.2, PRETO, 'meio')                  # V40
    a.t(E3, 8.5, 'Como chegar', 126, 184.6, PRETO, 'meio')                     # V41
    a.linha(9 + S, 191.5 + S, 139 + S, 191.5 + S, FIO, 0.2)                    # V42
    for txt, y in zip([                                                        # V43
        '*Oferta válida para novas matrículas de 06/03/2027 a 31/03/2027. Valor de R$ 49,90 apenas no 1º mês',
        'do plano mensal; demais meses R$ 119,90. Aulas experimentais sujeitas à lotação de cada turma.',
        'Imagens meramente ilustrativas.'], [195.5, 198.6, 201.7]):
        a.t(E5, 7, txt, 9, y, PRETO)

    with a.acabamento('verniz-uv'):                                            # §5 verso
        a.t(E1, 30, 'R$', 9.00, 44.04, PRETO)
        a.t(E1, 90, '49', 22.95, 60.0, PRETO)
        a.t(E1, 45, ',90', 61.75, 48.25, PRETO)
        a.c(116.5, 50.5, 22, PRETO)
    return a


if __name__ == '__main__':
    guias = '--guias' in sys.argv
    out = PASTA / 'saida'
    out.mkdir(exist_ok=True)
    fr, ve = frente(), verso()
    for nome, arte in (('frente', fr), ('verso', ve)):
        (out / f'flyer-{nome}.svg').write_text(arte.svg(guias))
        (out / f'flyer-{nome}-simulacao.svg').write_text(arte.svg(simular_acabamentos=True))
        for av in arte.avisos:
            print(f'AVISO {nome}: {av}')
    if '--pdf' in sys.argv:
        from pdf_cmyk import gerar_pdf
        r = gerar_pdf([fr, ve], out / 'flyer-grafica.pdf',
                      'Ápice Academia — flyer A5 inauguração (frente e verso)',
                      ['FRENTE', 'VERSO (cabeça com cabeça)'], E5, autor='Ápice Academia (fictícia)')
        print(r)
    print('ok')
