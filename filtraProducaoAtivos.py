#!/usr/bin/python
# -*- coding: utf-8 -*-

# Gera todas as WordClouds da Avaliação

from __future__ import print_function
import argparse
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv
import string
import sys
import numpy as np
import os

def ColunaToIndice(coluna):
    resposta = 0
    for letra in coluna:
        resposta = resposta * 26 + (ord(letra) - 64)

    return resposta - 1


iRestrito = ['A1', 'A2', 'B1']
iGeral = ['A1', 'A2', 'B1', 'B2', 'B3', 'B4', 'B5']
pesosQualis = [1.0, 0.85, 0.7, 0.5, 0.2, 0.1, 0.05]

codigoProgCol = ColunaToIndice('B')
siglaConfCol = ColunaToIndice('Y')
qualisConfCol = ColunaToIndice('W')
siglaPerCol = ColunaToIndice('BE')
qualisPerCol = ColunaToIndice('W')
siglaTotalCol = ColunaToIndice('BF')
qualisTotalCol = ColunaToIndice('W')
autoresCol = ColunaToIndice('O')
anoCol = ColunaToIndice('A')
subtipoCol = ColunaToIndice('Q')
idCol = ColunaToIndice('BC')
tiposDiscentes = ['DISCENTE MESTRADO', 'DISCENTE DOUTORADO', 'PARTEXT_EGRESSO_3_ANOS']
colAtivosSiglaPrograma = ColunaToIndice('A')
colAtivosNomeDocente = ColunaToIndice('B')
colAtivosAtivo = {'2013': ColunaToIndice('I'),
                  '2014': ColunaToIndice('P'),
                  '2015': ColunaToIndice('W'),
                  '2016': ColunaToIndice('AD')}
colPPSPPJ = {'2013': ColunaToIndice('D'),
             '2014': ColunaToIndice('K'),
             '2015': ColunaToIndice('R'),
             '2016': ColunaToIndice('Y')}
colCategoria = {'2013': ColunaToIndice('E'),
                '2014': ColunaToIndice('L'),
                '2015': ColunaToIndice('S'),
                '2016': ColunaToIndice('Z')}
colAula = {'2013': ColunaToIndice('F'),
           '2014': ColunaToIndice('M'),
           '2015': ColunaToIndice('T'),
           '2016': ColunaToIndice('AA')}
colOrientacao = {'2013': ColunaToIndice('G'),
                 '2014': ColunaToIndice('N'),
                 '2015': ColunaToIndice('U'),
                 '2016': ColunaToIndice('AB')}
colPublicacao = {'2013': ColunaToIndice('H'),
                 '2014': ColunaToIndice('O'),
                 '2015': ColunaToIndice('V'),
                 '2016': ColunaToIndice('AC')}
anos = ['2013', '2014', '2015', '2016']


def SelecionaColuna(tabela, coluna):
    resposta = []

    for linha in tabela:
        if len(linha) > coluna:
            resposta.append(linha[coluna].strip())

    return resposta


def CreateWordCloud(wordList, outFile, recria):
    if not recria and os.path.exists(outFile):
        return

    if len(wordList) == 0:
        return

    limpo = map(LimpaSigla, wordList)
    text = ' '.join(limpo)

    # Generate a word cloud image
    wordcloud = WordCloud(width=1920, height=1024).generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.figure(figsize=(16,9), facecolor='k')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=1)
    plt.savefig(outFile)
    plt.cla()
    plt.close()


def CreateHistogram(wordList, outFile, titulo, recria):
    if not recria and os.path.exists(outFile):
        return

    d = {}

    # count elements
    for l in wordList:
        d[l] = 1 + d.get(l, 0)

    if '' in d:
        d.pop('')

    producao = sorted(d.items(), key=lambda (x,y): y, reverse=True)

    N = len(producao)
    nomes = [unicode(x[0]) for x in producao]
    quantidades = [x[1] for x in producao]

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    plt.figure(figsize=(16,9), facecolor='k')
    fig, ax = plt.subplots(1, 1, figsize=(16,9))
    rects1 = ax.bar(ind, quantidades, width, color='r')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Quantidade')
    ax.set_title(titulo)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(nomes, rotation='vertical')
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8)


    # for rect in rects1:
    #     height = rect.get_height()
    #     ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
    #             '%d' % int(height),
    #             ha='center', va='bottom')
    plt.savefig(outFile)
    plt.cla()
    plt.close()


def SelecionaLinhas(tabela, coluna, valores):
    resposta = []

    for linha in tabela:
        if len(linha) > coluna:
            if linha[coluna] in valores:
                resposta.append(linha)

    return resposta


def SelecionaProducaoAutores(tabela, autores):
    resposta = []
    for linha in tabela:
        if len(linha) > autoresCol:
            for autor in autores:
                if autor in linha[autoresCol]:
                    resposta.append(linha)
                    break

    return resposta


def SelecionaPorCategoriaAutores(tabela, categorias):
    resposta = []

    for linha in tabela:
        if len(linha) > autoresCol:
            for c in categorias:
                if c in linha[autoresCol]:
                    resposta.append(linha)
                    break

    return resposta


def ExcluiLinhas(tabela, valores):
    resposta = []

    for linha in tabela:
        if not linha in valores:
            resposta.append(linha)

    return resposta


def Top3(lista, qualis):
    d = {}

    # count elements
    for l in lista:
        d[l] = 1 + d.get(l, 0)

    if '' in d:
        d.pop('')

    novo = {}
    for item in d.keys():
        novo[item] = '{:03d}'.format(d[item]) + qualis[item]

    # Se houver empate, estamos pegando sempre o menor Qualis
    resposta = sorted(novo, key=novo.get, reverse=True)

    # Considerando os dados atuais, nenhum programa tem menos de 3 entradas no IRestrito
    if len(resposta) >= 3:
        return resposta[0:3]
    else:
        while len(resposta) < 3:
            resposta.append('')
        return resposta


def CalculaEstrato(lista, qualis, estratos):
    d = {}

    # count elements
    for l in lista:
        d[l] = 1 + d.get(l, 0)

    if '' in d:
        d.pop('')

    contagem = {}
    for e in estratos:
        contagem[e] = 0

    for veiculo in d.keys():
        q = qualis[veiculo]
        n = d[veiculo]
        contagem[q] += n

    resposta = []
    for e in estratos:
        resposta.append(contagem[e])

    return resposta


def QualisUnificado(tabela):
    resposta = {}
    for linha in tabela:
        sigla = linha[siglaTotalCol]
        qualis = linha[qualisTotalCol]
        if len(sigla) != 0:
            if qualis in iGeral:
                if sigla in resposta:
                    if resposta[sigla] > qualis:
                        resposta[sigla] = qualis
                else:
                    resposta[sigla] = qualis

    return resposta


def Normaliza(s):
    return string.replace(s.title(), ' ', '')


def LimpaSigla(s):
    return filter(lambda x: x.isalnum(), string.replace(s, ' ', ''))


def FiltraAutores(lista, categoria):
    resultado = []
    for l in lista:
        autores = l.split('|')
        for autor in autores:
            quebrado = [x.strip() for x in autor.split('(')]
            nome = quebrado[0]
            if len(quebrado) > 1:
                if quebrado[1][:-1] in categoria:
                    resultado.append(Normaliza(nome))

    return resultado


def DoisDeTres(a, b, c):
    return (int(a) > 0 and int(b) > 0) or (int(a) > 0 and int(c) > 0) or (int(b) > 0 and int(c) > 0)

def AjustaPermanentes(tabela):
    resposta = []
    for linha in tabela:
        for ano in anos:
            if linha[colCategoria[ano]] == 'PERMANENTE':
                if DoisDeTres(linha[colAula[ano]], linha[colOrientacao[ano]], linha[colPublicacao[ano]]):
                    if len(linha[colPPSPPJ[ano]]) == 0:
                        linha[colAtivosAtivo[ano]] = 'ATIVO'
                else:
                    linha[colAtivosAtivo[ano]] = 'na'
        resposta.append(linha)

    return resposta


def ColetaAtivos(tabela, programa):
    resposta = {}
    docentesPrograma = SelecionaLinhas(tabela, colAtivosSiglaPrograma, [programa])
    for ano in anos:
        resposta[ano] = SelecionaColuna(SelecionaLinhas(docentesPrograma, colAtivosAtivo[ano], ['ATIVO']),
                                        colAtivosNomeDocente)
    return resposta


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gera os Word Clouds para todos os programas')
    parser.add_argument('-i', '--input', type=str, required=True, help='Produção Completa de todos os programas')
    parser.add_argument('-a', '--ativos', type=str, required=True, help='Planilha com Docentes ativos')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter - default=;')
    parser.add_argument('-f', '--filtra', type=str, required=False, help='Filtra apenas os programas informados separados por vírgula')

    args = parser.parse_args()

    if args.delimiter is not None:
        delimiter = args.delimiter
    else:
        delimiter = ';'

    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    programas = list(csv.reader(open(args.programas), delimiter=delimiter))
    tabelaAtivos = list(csv.reader(open(args.ativos), delimiter=delimiter))

    if args.filtra is not None and len(args.filtra) != 0:
        filtraProgramas = args.filtra.split(',')
    else:
        filtraProgramas = [x[1] for x in programas]

    qualis = QualisUnificado(inputData)

    dadosProgramas = {}
    idsProducoesAtivos = []
    ativosSaida = []
    ativosConsolidado = []

    tabelaAtivos = AjustaPermanentes(tabelaAtivos)

    for codigoPrograma, siglaPrograma in programas:
        if not siglaPrograma in filtraProgramas:
            continue

        print('Programa:', siglaPrograma, '...')
        prefixo = codigoPrograma + '-' + siglaPrograma
        dadosProgramas[siglaPrograma] = {'sigla': siglaPrograma, 'codigo': codigoPrograma}

        # Monta a listagem de docentes ativos
        ativosPrograma = ColetaAtivos(tabelaAtivos, siglaPrograma)

        # Seleciona a produção do programa filtrando a coluna de código

        producaoPrograma = SelecionaLinhas(inputData, codigoProgCol, [codigoPrograma])

        for ano in anos:
            producaoAno = SelecionaLinhas(producaoPrograma, anoCol, [ano])
            prodAtivos = SelecionaProducaoAutores(producaoAno, ativosPrograma[ano])
            idsProducoesAtivos.extend(SelecionaColuna(prodAtivos, idCol))

        linha = [codigoPrograma, siglaPrograma]
        for ano in anos:
            for docente in ativosPrograma[ano]:
                ativosSaida.append([codigoPrograma, siglaPrograma, ano, docente])
            linha.append(len(ativosPrograma[ano]))

        ativosConsolidado.append(linha)

    csv.writer(open('idProducoesAtivos.csv', 'wt'), delimiter=delimiter).writerows([[x] for x in idsProducoesAtivos])
    csv.writer(open('ativos-detalhado.csv', 'wt'), delimiter=delimiter).writerows(ativosSaida)
    csv.writer(open('ativos-consolidado.csv', 'wt'), delimiter=delimiter).writerows(ativosConsolidado)
