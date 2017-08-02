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

tituloArtigoCol = ColunaToIndice('N')
codigoProgCol = 1
siglaConfCol = 50
qualisConfCol = 51
siglaPerCol = 52
qualisPerCol = 53
siglaTotalCol = ColunaToIndice('BF')
qualisTotalCol = 55
autoresCol = ColunaToIndice('O')
colSubtipoProducao = ColunaToIndice('Q') # 'TRABALHO EM ANAIS'
anoCol = 0
tiposDiscentes = ['DISCENTE MESTRADO', 'DISCENTE DOUTORADO', 'PARTEXT_EGRESSO_3_ANOS']
tiposDocentes = ['DOCENTE PERMANENTE', 'DOCENTE COLABORADOR', 'DOCENTE VISITANTE']
anos = ['2013', '2014', '2015', '2016']


def SelecionaColuna(tabela, coluna):
    resposta = []

    for linha in tabela:
        if len(linha) > coluna:
            resposta.append(linha[coluna].strip())

    return resposta


def LimpaSigla(s):
    return filter(lambda x: x.isalnum(), string.replace(s, ' ', ''))


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


def GraficoBarras(tabela, outFile, titulo, recria):
    if not recria and os.path.exists(outFile):
        return

    producao = sorted(tabela, key=lambda x: x[1], reverse=True)

    N = len(producao)
    nomes = [unicode(x[0]) for x in producao]
    quantidades = [x[1] for x in producao]

    ind = np.arange(N)  # the x locations for the groups
    width = 0.35       # the width of the bars

    plt.figure(figsize=(16,9), facecolor='k')
    fig, ax = plt.subplots(1, 1, figsize=(16,9))
    rects1 = ax.bar(ind, quantidades, width, color='r')

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Porcentagem')
    ax.set_title(titulo)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(nomes, rotation='vertical')
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(8)

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


col4Nx = ColunaToIndice('A')
col4NAno = ColunaToIndice('B')
col4NNome = ColunaToIndice('C')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Gera os Word Clouds para todos os programas')
    parser.add_argument('-i', '--input', type=str, required=True, help='Produção Completa de todos os programas')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-f', '--filtra', type=str, required=False, help='Filtra apenas os programas informados separados por vírgula')
    parser.add_argument('-r', '--recria', action='store_true', required=False, help='Recria arquivos já existentes')
    parser.add_argument('-rs', '--recriasumario', action='store_true', required=False, help='Recria arquivos de sumario')


    args = parser.parse_args()

    delimiter = ';'

    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    programas = list(csv.reader(open(args.programas), delimiter=delimiter))

    if args.filtra != None and len(args.filtra) != 0:
        filtraProgramas = args.filtra.split(',')
    else:
        filtraProgramas = [x[1] for x in programas]

    totalVeiculos = []
    totalEgressos = []
    participacaoDiscente = []

    for codigoPrograma, siglaPrograma in programas:
        if not siglaPrograma in filtraProgramas:
            continue

        print('Programa:', siglaPrograma, codigoPrograma, '...')
        prefixo = codigoPrograma + '-' + siglaPrograma

        dadosPrograma = SelecionaLinhas(inputData, codigoProgCol, codigoPrograma)

        nomeArquivo = codigoPrograma + '-4N.csv'
        if os.path.isfile(nomeArquivo):
            print('... arquivo 4N encontrado.')
            dados4N = list(csv.reader(open(nomeArquivo), delimiter=delimiter))
            titulos = SelecionaColuna(dados4N[1:], col4NNome)

            selecionados = SelecionaLinhas(dadosPrograma, tituloArtigoCol, titulos)
            print(len(titulos) - 1, len(selecionados))

            siglas = SelecionaColuna(selecionados, siglaTotalCol)
            CreateWordCloud(siglas, prefixo + '-wc-veiculo.png', args.recria)
            CreateHistogram(siglas, prefixo + '-hist-veiculos.png', u'Produção Total (veículos)', args.recria)
            totalVeiculos.extend(siglas)

            discentes = SelecionaPorCategoriaAutores(selecionados, tiposDiscentes)
            siglas2 = SelecionaColuna(discentes, siglaTotalCol)
            CreateWordCloud(siglas2, prefixo + '-wc-discentes+egressos.png', args.recria)
            CreateHistogram(siglas2, prefixo + '-hist-discentes+egressos.png', u'Produção Total (discente + egressos)', args.recria)
            totalEgressos.extend(siglas2)

            anais = SelecionaLinhas(selecionados, colSubtipoProducao, ['TRABALHO EM ANAIS'])
            participacaoDiscente.append([siglaPrograma, 100.0 * len(siglas2) / len(siglas), len(siglas), len(anais)])


    print(participacaoDiscente)
    CreateWordCloud(totalVeiculos, 'total-wc-veiculo.png', args.recria or args.recriasumario)
    CreateHistogram(totalEgressos, 'total-hist-veiculos.png', u'Produção Total (veículos)', args.recria or args.recriasumario)
    GraficoBarras(participacaoDiscente, 'total-hist-part-discente.png', u'Participação Discente na produção 4N', args.recria or args.recriasumario)
    csv.writer(open('participacao-discente.csv', 'wt'), delimiter=delimiter).writerows(participacaoDiscente)
