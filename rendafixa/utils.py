import numpy as np

def tempo2dia(tempo, unidade):
    if unidade == 'dia':
        return int(np.ceil(tempo))
    elif unidade == 'mes':
        return int(np.ceil(tempo * 30))
    elif unidade == 'ano':
        return int(np.ceil(tempo * 360))
    else:
        raise ValueError('Unidade de tempo inválida.')
    
def tempo2ano(tempo, unidade):
    if unidade == 'dia':
        return tempo / 360
    elif unidade == 'mes':
        return tempo / 12
    elif unidade == 'ano':
        return tempo
    else:
        raise ValueError('Unidade de tempo inválida.')

def rendimentos(valor_inicial, taxas, tempo, unidade='dia'):
    tempo = tempo2ano(tempo, unidade)
    if isinstance(taxas, (list, tuple)):
        return valor_inicial * np.prod([1 + taxa for taxa in taxas]) ** tempo - valor_inicial
    else:
        return valor_inicial * (1 + taxas) ** tempo - valor_inicial

def round_taxa(taxa):
    if isinstance(taxa, (list, tuple)):
        return [round(t, 4) for t in taxa]
    else:
        return round(taxa, 4)

def irpf(rendimento, tempo, unidade='dia'):
    tempo = tempo2dia(tempo, unidade)
    if tempo <= 180:
        return rendimento * 0.225
    elif tempo <= 360:
        return rendimento * 0.2
    elif tempo <= 720:
        return rendimento * 0.175
    else:
        return rendimento * 0.15
    
def iof(rendimento, tempo, unidade='dia'):
    tabela_iof = [0.96, 0.93, 0.9, 0.86, 0.83, 0.8, 0.76, 0.73, 0.7, 0.66, 0.63, 
                  0.6, 0.56, 0.53, 0.5, 0.46, 0.43, 0.4, 0.36, 0.33, 0.3, 0.26, 
                  0.23, 0.2, 0.16, 0.13, 0.1, 0.06, 0.03, 0]
    tempo = tempo2dia(tempo, unidade)
    if tempo < 30:
        return rendimento * tabela_iof[tempo - 1]
    else:
        return 0
    
def cdi2taxa(taxa, di):
    return (((di/100 + 1) **(1/252) - 1) * (taxa/100) + 1)**252 - 1

def rendimento_real(valor, ipca, tempo, unidade='dia'):
    return valor * (1 + ipca/100)**(tempo2ano(tempo, unidade)) - valor