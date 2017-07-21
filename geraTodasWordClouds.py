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

iRestrito = ['A1', 'A2', 'B1']

codigoProgCol = 1
siglaConfCol = 50
qualisConfCol = 51
siglaPerCol = 52
qualisPerCol = 53
siglaTotalCol = 54
qualisTotalCol = 55
autoresCol = 8

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
    text = ' '.join(wordList)

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


def ExcluiLinhas(tabela, valores):
    resposta = []

    for linha in tabela:
        if not linha in valores:
            resposta.append(linha)

    return resposta


def Top3(lista):
    d = {}

    # count elements
    for l in lista:
        d[l] = 1 + d.get(l, 0)

    if '' in d:
        d.pop('')

    resposta = sorted(d, key=d.get, reverse=True)

    if len(resposta) > 3:
        return resposta[0:3]
    else:
        while len(resposta) < 3:
            resposta.append('')
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

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Gera os Word Clouds para todos os programas')
    parser.add_argument('-i', '--input', type=str, required=True, help='Produção Completa de todos os programas')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter - default=;')
    parser.add_argument('-wcp', '--wordcloudproducao', action='store_true', required=False, help='Gera Word Cloud da produção científica')
    parser.add_argument('-hp', '--histogramaproducao', action='store_true', required=False, help='Gera Histograma da produção científica')
    parser.add_argument('-wca', '--wordcloudautores', action='store_true', required=False, help='Gera Word Cloud dos autores')
    parser.add_argument('-ha', '--histogramaautores', action='store_true', required=False, help='Gera Histograma dos autores')
    parser.add_argument('-r', '--recria', action='store_true', required=False, help='Recria arquivos já existentes')

    args = parser.parse_args()

    if args.delimiter != None:
        delimiter = args.delimiter
    else:
        delimiter = ';'

    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    programas = list(csv.reader(open(args.programas), delimiter=delimiter))

    for sigla, nome in programas:
        print('Programa:', nome, '...')
        prefixo = sigla + '-' + nome

        # Seleciona a produção do programa filtrando a coluna de código

        producaoPrograma = SelecionaLinhas(inputData, codigoProgCol, [sigla])

        # Depois sleciona tanto periódicos quanto conferências deste programa,
        # baseado no iRestrito
        producaoTotal = SelecionaLinhas(producaoPrograma, qualisTotalCol, iRestrito)
        producaoPeriodicos = SelecionaLinhas(producaoPrograma, qualisPerCol, iRestrito)
        producaoConferencias = SelecionaLinhas(producaoPrograma, qualisConfCol, iRestrito)
        limite = 3 * len(producaoPeriodicos)

        # O limite de conferências é 3 * periódicos no iRestrito
        # O if abaixo remove as últimas conferências se o limite for estourado
        # A planilha original tem que estar ordenada por Qualis decrescente

        if len(producaoConferencias) > limite:
            producaoConferencias = producaoConferencias[0:limite]
            print('Restringindo produção de conferências a', limite)

        # Extrai a coluna para fazer o word cloud

        wcTotal = SelecionaColuna(producaoTotal, siglaTotalCol)
        wcConferencias = SelecionaColuna(producaoConferencias, siglaConfCol)
        wcPeriodicos = SelecionaColuna(producaoPeriodicos, siglaPerCol)

        # Gera os word clouds e grava no arquivo
        if args.wordcloudproducao:
            CreateWordCloud(wcTotal, prefixo + '-wc-total-irestrito.png', args.recria)
            CreateWordCloud(wcConferencias, prefixo + '-wc-conf-irestrito.png', args.recria)
            CreateWordCloud(wcPeriodicos, prefixo + '-wc-per-irestrito.png', args.recria)

        # Cria um histograma com base nas palavras do word cloud para
        # facilitar visualização
        if args.histogramaproducao:
            CreateHistogram(wcTotal, prefixo + '-hist-total-irestrito.png', u'Produção Total (Irestrito)', args.recria)
            CreateHistogram(wcConferencias, prefixo + '-hist-conf-irestrito.png', u'Produção Conferências (Irestrito)', args.recria)
            CreateHistogram(wcPeriodicos, prefixo + '-hist-per-irestrito.png', u'Produção Periódicos (Irestrito)', args.recria)

        autoresTotal = SelecionaColuna(producaoTotal, autoresCol)
        discenteMestrado = FiltraAutores(autoresTotal, ['DISCENTE MESTRADO'])
        discenteDoutorado = FiltraAutores(autoresTotal, ['DISCENTE DOUTORADO'])
        docentePermanente = FiltraAutores(autoresTotal, ['DOCENTE PERMANTENTE'])
        docenteColaborador = FiltraAutores(autoresTotal, ['DOCENTE COLABORADOR'])
        egresso = FiltraAutores(autoresTotal, ['PARTEXT_EGRESSO_3_ANOS'])
        docentes = FiltraAutores(autoresTotal, ['DOCENTE PERMANENTE', 'DOCENTE COLABORADOR'])
        discentes = FiltraAutores(autoresTotal, ['DISCENTE MESTRADO', 'DISCENTE DOUTORADO', 'PARTEXT_EGRESSO_3_ANOS'])

        if args.wordcloudautores:
            #CreateWordCloud(discenteMestrado, prefixo + '-wc-autor-discente-mestrado.png', args.recria)
            #CreateWordCloud(discenteDoutorado, prefixo + '-wc-autor-discente-doutorado.png', args.recria)
            CreateWordCloud(docentePermanente, prefixo + '-wc-autor-docente-permanente.png', args.recria)
            #CreateWordCloud(docenteColaborador, prefixo + '-wc-autor-docente-colaborador.png', args.recria)
            #CreateWordCloud(egresso, prefixo + '-wc-autor-egresso.png', args.recria)
            CreateWordCloud(docentes, prefixo + '-wc-autor-docentes.png', args.recria)
            CreateWordCloud(discentes, prefixo + '-wc-autor-discentes.png', args.recria)

        if args.histogramaautores:
            #CreateHistogram(discenteMestrado, prefixo + '-hist-autor-discente-mestrado.png', u'Discente Mestrado', args.recria)
            #CreateHistogram(discenteDoutorado, prefixo + '-hist-autor-discente-doutorado.png', u'Discente Doutorado', args.recria)
            CreateHistogram(docentePermanente, prefixo + '-hist-autor-docente-permanente.png', u'Docente Permanente', args.recria)
            #CreateHistogram(docenteColaborador, prefixo + '-hist-autor-docente-colaborador.png', u'Docente Colaborador', args.recria)
            #CreateHistogram(egresso, prefixo + '-hist-autor-egresso.png', u'Egresso', args.recria)
            CreateHistogram(docentes, prefixo + '-hist-autor-docentes.png', u'Docentes (permanente + colaborador)', args.recria)
            CreateHistogram(discentes, prefixo + '-hist-autor-discentes.png', u'Discentes (mestrado+doutorado+egresso)', args.recria)

        # top3Programa = Top3(wcTotal)
        # top3Conferencias = Top3(wcConferencias)
        # top3Periodicos = Top3(wcPeriodicos)
        #
        # for i in range(1, 4):
        #     wcTotalTop = ExcluiLinhas(wcTotal, top3Programa[0:i])
        #     wcConferenciasTop = ExcluiLinhas(wcConferencias, top3Conferencias[0:i])
        #     wcPeriodicosTop = ExcluiLinhas(wcPeriodicos, top3Periodicos[0:i])
        #
        #     CreateWordCloud(wcTotalTop, prefixo + '-wc-total-irestrito-' + str(i) + '.png')
        #     CreateWordCloud(wcConferenciasTop, prefixo + '-wc-conf-irestrito-' + str(i) + '.png')
        #     CreateWordCloud(wcPeriodicosTop, prefixo + '-wc-per-irestrito-' + str(i) + '.png')
