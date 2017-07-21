#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import csv
import sys
import argparse
import string
import unicodedata

completo = ['IEEE', 'WSEAS', 'VLDB', 'SPRINGER', 'SIAM', 'SBC', 'USP',
            'TCMRJ', 'NCSL', 'JMIR', 'IET', 'IERI', 'IEICE', 'IEEE/ACM',
            'IADIS', 'ETRI', 'EPJ', 'EAD', 'BIT']
remove = ['TO', 'THE', 'ON', 'OF', 'DO', 'DA', 'DE', 'AND', 'AN', 'EM',
          'IN', 'NA', 'FOR']


def CleanText(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


def Abrevia(palavra):
    if palavra in remove:
        return ''
    elif palavra in completo:
        return palavra
    else:
        if len(palavra) <= 3:
            return palavra.title()
        else:
            return palavra[0]

def CriaSigla(longName):
    # Remove tudo após a abertura de parêntesis
    fullName = longName.split('(')[0]

    # Se não tem espaço, o nome é a sigla
    if not ' ' in fullName:
        return fullName.title()

    # Se é menor que 20, apenas remova os espaços
    if len(fullName) < 20:
        semEspaco = fullName.title().replace(' ', '')
        return semEspaco

    # Caso congrário, gere as siglas por palavras
    l = fullName.split(' ')
    answer = ''
    for item in l:
        answer += Abrevia(item)

    return answer


def CriaSiglas(inputFile, outputFile, column, delimiter):
    print('Reading input file:', inputFile, '...')
    inputData = list(csv.reader(open(inputFile), delimiter=delimiter))
    outputData = []

    print('Creating short names...')
    for line in inputData:
        if len(line) > column:
            line.append(CriaSigla(line[column]))
            outputData.append(line)

    print('Writing output file...')
    csv.writer(open(outputFile, 'wt'), delimiter=delimiter).writerows(outputData)

    return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate short names for journals')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-c', '--column', type=int, required=True, help='Column containing journal name')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV file')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter - default=;')

    args = parser.parse_args()
    column = int(args.column)

    if args.delimiter != None:
        delimiter = args.delimiter
    else:
        delimiter = ';'

    CriaSiglas(args.input, args.output, column, delimiter)
