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


def TotalizaAtivosQuadrienio(tabelaAtivos, codigoPrograma):
    dadosPrograma = SelecionaLinhas(tabelaAtivos, ColunaToIndice('A'), [codigoPrograma])

    return dadosPrograma[0][2:]


def CountNotZero(tabela, coluna):
    return len(filter(lambda x: x[coluna] != '0', tabela))

def CountNotEmpty(tabela, coluna):
    return len(filter(lambda x: x != '', tabela))

def ToInt(s):
    if len(str(s)) > 0:
        return int(s)
    else:
        return 0

colpdCodigoPrograma = ColunaToIndice('B')
colpdNomeDocente = ColunaToIndice('Q')
colpdAno = ColunaToIndice('A')
colpdTotalPeriodicos = ColunaToIndice('W')
colpdTotalConferencias = ColunaToIndice('AZ')

coldCodigoPrograma = ColunaToIndice('B')
coldNomeDocente = ColunaToIndice('R')
coldAno = ColunaToIndice('A')
coldDisciplinaResponsavel = ColunaToIndice('AS')
coldDisciplinaParticipante = ColunaToIndice('AU')
coldOrientacaoAndamento = ColunaToIndice('AZ')
coldOrientacaoConcluida = ColunaToIndice('BD')
coldCategoria = ColunaToIndice('AG')
coldPosDoutorado = ColunaToIndice('AA')
coldRegimeTrabalho = ColunaToIndice('AI')
coldPQ = ColunaToIndice('AJ')
coldDT = ColunaToIndice('AM')
coldProjetoResponsavel = ColunaToIndice('AP')
coldProjetoParticipante = ColunaToIndice('AQ')
coldProjetoFinanciamento = ColunaToIndice('AR')
coldAulaResponsavel = ColunaToIndice('AS')
coldAulaParticipante = ColunaToIndice('AU')
coldOrientacaoAndamentoMestrado = ColunaToIndice('AW')
coldOrientacaoAndamentoDoutorado = ColunaToIndice('AX')
coldOrientacaoConcluidaMestrado = ColunaToIndice('BA')
coldOrientacaoConcluidaDoutorado = ColunaToIndice('BB')
coldGraduacaoTutoria = ColunaToIndice('BH')
coldGraduacaoMonografia = ColunaToIndice('BI')
coldGraduacaoIniciacaoCientifica = ColunaToIndice('BJ')
coldGraduacaoDisciplinas = ColunaToIndice('BK')
coldOutrosPPGPermanente = ColunaToIndice('BM')
coldOutrosPPGColaborador = ColunaToIndice('BN')
coldOutrosPPGVisitante = ColunaToIndice('BO')


colrpAno = ColunaToIndice('A')
colrpCodigoPPG = ColunaToIndice('B')
colrpAreaConcentracao = ColunaToIndice('V')
colrpLinhasPesquisa = ColunaToIndice('W')
colrpTurmasMestrado = ColunaToIndice('X')
colrpTurmasDoutorado = ColunaToIndice('Y')
colrpTurmasMD = ColunaToIndice('Z')
colrpDissertacoesConcluidas = ColunaToIndice('AE')
colrpTesesConcluidas = ColunaToIndice('AG')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Gera os Word Clouds para todos os programas')
    parser.add_argument('-i', '--input', type=str, required=True, help='Produção Completa de todos os programas')
    parser.add_argument('-pd', '--producoesdocentes', type=str, required=True, help='Arquivo com a aba producoes_docente')
    parser.add_argument('-d', '--docentes', type=str, required=True, help='Arquivo com a aba docentes')
    parser.add_argument('-rp', '--resumoprograma', type=str, required=True, help='Arquivo com a aba programa')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-a', '--ativos', type=str, required=True, help='arquivo com os docentes ativos por programa')
    parser.add_argument('-r', '--recria', action='store_true', required=False, help='Recria arquivos já existentes')
    parser.add_argument('-f', '--filtra', type=str, required=False, help='Filtra apenas os programas informados separados por vírgula')

    args = parser.parse_args()

    delimiter = ';'

    inputData = list(csv.reader(open(args.input), delimiter=delimiter))
    producoesDocentesTotal = list(csv.reader(open(args.producoesdocentes), delimiter=delimiter))
    docentesTotal = list(csv.reader(open(args.docentes), delimiter=delimiter))
    programas = list(csv.reader(open(args.programas), delimiter=delimiter))
    ativos = list(csv.reader(open(args.ativos), delimiter=delimiter))
    resumoPrograma = list(csv.reader(open(args.resumoprograma), delimiter=delimiter))

    if args.filtra != None and len(args.filtra) != 0:
        filtraProgramas = args.filtra.split(',')
    else:
        filtraProgramas = [x[1] for x in programas]

    qualis = QualisUnificado(inputData)
    dadosProgramas = {}

    resultados = [['Programa', 'Docente', 'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito',
                  'Ano', 'Categoria', 'Aula', 'Orientou', 'Publicou', 'Veredito']]
    consolidado = [['Programa', '2013', '2014', '2015', '2016', 'Olhar AdHoc']]

    for codigoPrograma, siglaPrograma in programas:
        if not siglaPrograma in filtraProgramas:
            continue

        print('*** Programa:', siglaPrograma, '***')
        prefixo = codigoPrograma + '-' + siglaPrograma

        dadosProgramas[siglaPrograma] = {'sigla': siglaPrograma, 'codigo': codigoPrograma}

        rpDados = SelecionaLinhas(resumoPrograma, colrpCodigoPPG, [codigoPrograma])
        rpDados2016 = SelecionaLinhas(rpDados, colrpAno, ['2016'])[0]

        dadosProgramas[siglaPrograma]['areasConcentracao'] = rpDados2016[colrpAreaConcentracao]
        dadosProgramas[siglaPrograma]['linhasPesquisa'] = rpDados2016[colrpLinhasPesquisa]

        print('O programa está organizado em', dadosProgramas[siglaPrograma]['areasConcentracao'],
              'área de concentração e', dadosProgramas[siglaPrograma]['linhasPesquisa'],
              'linhas de pesquisa.')

        todosDocentes = SelecionaLinhas(docentesTotal, coldCodigoPrograma, [codigoPrograma])
        docentesPermanentes = SelecionaLinhas(todosDocentes, coldCategoria, ['PERMANENTE'])
        docentesColaboradores = SelecionaLinhas(todosDocentes, coldCategoria, ['COLABORADOR'])

        dadosProgramas[siglaPrograma]['mediaPermanentes'] = len(docentesPermanentes) / 4.0
        dadosProgramas[siglaPrograma]['mediaColaboradores'] = len(docentesColaboradores) / 4.0

        print('Em média, durante o quadriênio, o corpo docente do programa foi formado por',
              dadosProgramas[siglaPrograma]['mediaPermanentes'], 'docentes permanentes e',
              dadosProgramas[siglaPrograma]['mediaColaboradores'], 'docentes colaboradores.')

        dadosProgramas[siglaPrograma]['ativos'] = TotalizaAtivosQuadrienio(ativos, codigoPrograma)
        dadosProgramas[siglaPrograma]['mediaAtivos'] = reduce(lambda x, y: int(x) + int(y),  dadosProgramas[siglaPrograma]['ativos']) / 4.0
        print('Foram considerados', dadosProgramas[siglaPrograma]['mediaAtivos'], 'professores ativos, em média, no quadriênio.')

        dadosProgramas[siglaPrograma]['pq'] = len(SelecionaLinhas(SelecionaLinhas(docentesPermanentes, coldAno, ['2016']), coldPQ, ['1A', '1B', '1C', '1D', '2']))
        dadosProgramas[siglaPrograma]['pq1'] = len(SelecionaLinhas(SelecionaLinhas(docentesPermanentes, coldAno, ['2016']), coldPQ, ['1A', '1B', '1C', '1D']))
        dadosProgramas[siglaPrograma]['dt'] = len(SelecionaLinhas(SelecionaLinhas(docentesPermanentes, coldAno, ['2016']), coldDT, ['1A', '1B', '1C', '1D', '2']))

        print('No ano de 2016, dentre os docentes permanentes,', dadosProgramas[siglaPrograma]['pq'],
              'possuíam bolsa de Produtividade em Pesquisa do CNPq, sendo', dadosProgramas[siglaPrograma]['pq1'] , 'de nível 1. Além disso',
              dadosProgramas[siglaPrograma]['dt'], 'possuíam bolsa DT.')

        listaNomeDocentes = list(set(SelecionaColuna(docentesPermanentes, coldNomeDocente)))

        projetosFinanciamento = 0
        projetosResponsavel = 0
        for docente in listaNomeDocentes:
            soDocente = SelecionaLinhas(docentesPermanentes, coldNomeDocente, [docente])
            if CountNotZero(soDocente, coldProjetoFinanciamento) > 0:
                projetosFinanciamento += 1
            if CountNotZero(soDocente, coldProjetoResponsavel) > 0:
                projetosResponsavel += 1

        print(projetosFinanciamento, 'docentes permanentes tiveram projetos com financiamento e', projetosResponsavel,
              'docentes permanentes foram responsáveis por projetos no quadriênio.')

        dadosProgramas[siglaPrograma]['docentesProjetosFinanciamento'] = projetosFinanciamento
        dadosProgramas[siglaPrograma]['docentesProjetosResponsavel'] = projetosResponsavel

        docentesDisciplinas = 0
        for docente in listaNomeDocentes:
            soDocente = SelecionaLinhas(docentesPermanentes, coldNomeDocente, [docente])
            if CountNotZero(soDocente, coldDisciplinaParticipante) + CountNotZero(soDocente, coldDisciplinaResponsavel) > 0:
                docentesDisciplinas += 1

        dadosProgramas[siglaPrograma]['docentesDisciplinas'] = docentesDisciplinas

        print('Durante o quadriênio,', docentesDisciplinas, 'docentes permanentes distintos ministraram disciplinas no programa.')

        turmasDisciplinas = reduce(lambda x, y: ToInt(x) + ToInt(y), SelecionaColuna(rpDados, colrpTurmasDoutorado)) + \
                            reduce(lambda x, y: ToInt(x) + ToInt(y), SelecionaColuna(rpDados, colrpTurmasMestrado)) + \
                            reduce(lambda x, y: ToInt(x) + ToInt(y), SelecionaColuna(rpDados, colrpTurmasMD))

        print('Foram oferecidas', turmasDisciplinas, 'turmas de disciplinas durante o quadriênio.')
        dadosProgramas[siglaPrograma]['turmasDisciplinas'] = turmasDisciplinas

        tesesDefendidas = reduce(lambda x, y: ToInt(x) + ToInt(y), SelecionaColuna(rpDados, colrpTesesConcluidas))
        dissertacoesDefendidas = reduce(lambda x, y: ToInt(x) + ToInt(y), SelecionaColuna(rpDados, colrpDissertacoesConcluidas))
        dadosProgramas[siglaPrograma]['tesesDefendidas'] = tesesDefendidas
        dadosProgramas[siglaPrograma]['dissertacoesDefendidas'] = dissertacoesDefendidas

        mediaTeses = ToInt(tesesDefendidas) / dadosProgramas[siglaPrograma]['mediaAtivos'] / 4.0
        mediaDissertacoes = ToInt(dissertacoesDefendidas) / dadosProgramas[siglaPrograma]['mediaAtivos'] / 4.0

        print('No quadriênio, foram defendidas', tesesDefendidas, 'teses de doutorado e', dissertacoesDefendidas,
              'dissertações de mestrado, numa média de', '{:.1f}'.format(mediaTeses), 'teses e',
              '{:.1f}'.format(mediaDissertacoes), 'dissertações por docente ativo por ano.')

        mediaTeses = ToInt(tesesDefendidas) / dadosProgramas[siglaPrograma]['mediaPermanentes'] / 4.0
        mediaDissertacoes = ToInt(dissertacoesDefendidas) / dadosProgramas[siglaPrograma]['mediaPermanentes'] / 4.0

        print('No quadriênio, foram defendidas', tesesDefendidas, 'teses de doutorado e', dissertacoesDefendidas,
              'dissertações de mestrado, numa média de', '{:.1f}'.format(mediaTeses), 'teses e',
              '{:.1f}'.format(mediaDissertacoes), 'dissertações por docente permanente por ano.')

        mediaTeses = ToInt(tesesDefendidas) / (dadosProgramas[siglaPrograma]['mediaPermanentes'] + dadosProgramas[siglaPrograma]['mediaColaboradores']) / 4.0
        mediaDissertacoes = ToInt(dissertacoesDefendidas) / (dadosProgramas[siglaPrograma]['mediaPermanentes'] + dadosProgramas[siglaPrograma]['mediaColaboradores']) / 4.0

        print('No quadriênio, foram defendidas', tesesDefendidas, 'teses de doutorado e', dissertacoesDefendidas,
              'dissertações de mestrado, numa média de', '{:.1f}'.format(mediaTeses), 'teses e',
              '{:.1f}'.format(mediaDissertacoes), 'dissertações por docente (permanente + colaborador) por ano.')
