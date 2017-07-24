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

codigoProgCol = 1
siglaConfCol = 50
qualisConfCol = 51
siglaPerCol = 52
qualisPerCol = 53
siglaTotalCol = 54
qualisTotalCol = 55
autoresCol = 8
anoCol = 0
tiposDiscentes = ['DISCENTE MESTRADO', 'DISCENTE DOUTORADO', 'PARTEXT_EGRESSO_3_ANOS']
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Gera os Word Clouds para todos os programas')
    parser.add_argument('-i', '--input', type=str, required=True, help='Produção Completa de todos os programas')
    parser.add_argument('-pd', '--producoesdocentes', type=str, required=True, help='Arquivo com a aba producoes_docente')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-d', '--docentes', type=str, required=True, help='arquivo com a aba docentes')
    parser.add_argument('-r', '--recria', action='store_true', required=False, help='Recria arquivos já existentes')
    parser.add_argument('-f', '--filtra', type=str, required=False, help='Filtra apenas os programas informados separados por vírgula')

    args = parser.parse_args()

    delimiter = ';'

    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    producoesDocentesTotal = list(csv.reader(open(args.producoesdocentes), delimiter=delimiter))
    docentesTotal = list(csv.reader(open(args.docentes), delimiter=delimiter))
    programas = list(csv.reader(open(args.programas), delimiter=delimiter))

    if args.filtra != None and len(args.filtra) != 0:
        filtraProgramas = args.filtra.split(',')
    else:
        filtraProgramas = [x[1] for x in programas]

    qualis = QualisUnificado(inputData)

    resultados = [['Programa', 'Docente', 'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito']]
    consolidado = [['Programa', '2013', '2014', '2015', '2016', 'Olhar AdHoc']]

    for sigla, nome in programas:
        if not nome in filtraProgramas:
            continue

        print('Programa:', nome, '...')
        prefixo = sigla + '-' + nome

        producoesDocentes = SelecionaLinhas(producoesDocentesTotal, ColunaToIndice('B'), [sigla])
        docentes = SelecionaLinhas(docentesTotal, ColunaToIndice('B'), [sigla])

        nomeDocentes = list(set(SelecionaColuna(docentes, ColunaToIndice('R'))))
        ativosNoAno = {}
        olharAdHoc = 'nao'
        for ano in anos:
            ativosNoAno[ano] = 0

        for doutor in nomeDocentes:
            linha = [nome, doutor]
            soDocente = SelecionaLinhas(docentes, ColunaToIndice('R'), [doutor])
            publicacoes = SelecionaLinhas(producoesDocentes, ColunaToIndice('Q'), [doutor])
            for ano in anos:
                linha.append(ano)
                anoSelecionado = SelecionaLinhas(soDocente, ColunaToIndice('A'), [ano])
                if len(anoSelecionado) == 1:
                    deuAula = int(anoSelecionado[0][ColunaToIndice('AS')]) + int(anoSelecionado[0][ColunaToIndice('AU')])
                    orientou = int(anoSelecionado[0][ColunaToIndice('AZ')]) + int(anoSelecionado[0][ColunaToIndice('BD')])
                    categoria = anoSelecionado[0][ColunaToIndice('AG')]
                else:
                    deuAula = 0
                    orientou = 0
                    categoria = ''

                anoSelecionado = SelecionaLinhas(publicacoes, ColunaToIndice('A'), ano)
                if len(anoSelecionado) == 1:
                    publicou = int(anoSelecionado[0][ColunaToIndice('W')]) + int(anoSelecionado[0][ColunaToIndice('AZ')])
                else:
                    publicou = 0

                veredito = 'na'
                if categoria == 'PERMANENTE':
                    veredito = 'ATIVO'
                elif categoria == 'COLABORADOR':
                    if (deuAula > 0 and orientou > 0) or (deuAula > 0 and publicou > 0) or (orientou > 0 and publicou > 0):
                        veredito = 'ATIVO'
                elif categoria == 'VISITANTE':
                    if (deuAula > 0 and orientou > 0) or (deuAula > 0 and publicou > 0) or (orientou > 0 and publicou > 0):
                        veredito = 'AD-HOC'

                if veredito == 'ATIVO':
                    ativosNoAno[ano] += 1

                if veredito == 'AD-HOC':
                    olharAdHoc = 'SIM'


                linha.extend([categoria, deuAula, orientou, publicou, veredito])

            resultados.append(linha)

        linha = [nome]
        for ano in anos:
            linha.append(ativosNoAno[ano])
        linha.append(olharAdHoc)
        consolidado.append(linha)

    csv.writer(open('ativos_detalhado.csv', 'wt'), delimiter=delimiter).writerows(resultados)
    csv.writer(open('ativos.csv', 'wt'), delimiter=delimiter).writerows(consolidado)
