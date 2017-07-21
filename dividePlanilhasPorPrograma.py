#!/usr/bin/python
# -*- coding: utf-8 -*-

# Divide cada arquivo de produção da CAPES em várias versões, uma por programa
# Mantém o título do arquivo e coloca na pasta referente ao código do programa

from __future__ import print_function
import argparse
import string
import csv
import codecs
import sys
import os

def ReadInputFile(nomeCSV):
    return list(csv.reader(open(nomeCSV), delimiter=';'))

def IdentificaProgramas(planilha, header, column):
    programas = {}
    for linha in planilha[header:]:
        if len(linha) >= 2:
            programas[linha[column]] = True

    return programas.keys()

def CriaDiretorios(programas):
    for programa in programas:
        if (not os.path.exists(programa)):
            os.makedirs(programa)

def ExtraiPrograma(programa, cabecalho, dados, column):
    dadosGravar = cabecalho[:]
    dadosPrograma = filter(lambda x: x[column] == programa, dados)
    dadosGravar.extend(dadosPrograma)

    return dadosGravar



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Divide os dados do programa do arquivo CSV de entrada por programa')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-n', '--header', type=int, required=True, help='Number of header lines')
    parser.add_argument('-c', '--column', type=int, required=True, help='Column to find the program ID')
    args = parser.parse_args()
    header = int(args.header)
    column = int(args.column)

    print('Lendo CSV de entrada...')
    planilha = ReadInputFile(args.input)

    programas = IdentificaProgramas(planilha, header, column)

    CriaDiretorios(programas)

    cabecalho = planilha[0:header]
    dados = planilha[header:]

    for programa in programas:
        print(programa, '...')
        dadosGravar = ExtraiPrograma(programa, cabecalho, dados, column)

        arquivoSaida = os.path.join(programa, args.input)
        saida = csv.writer(open(arquivoSaida, 'wt'), delimiter=';')
        saida.writerows(dadosGravar)



