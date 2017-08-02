#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import pandas as pd
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Gera as strings para os programas de Mestrado Profissional')
    parser.add_argument('-i', '--input', type=str, required=True, help='Planilha com os dados gerais')
    parser.add_argument('-p', '--programas', type=str, required=True, help='Arquivo com os códigos dos programas')
    parser.add_argument('-f', '--filtra', type=str, required=False, help='Filtra apenas os programas informados separados por vírgula')

    args = parser.parse_args()

    programas = pd.read_excel('codigo-programas.xlsx', 'Sheet1')

    if args.filtra is not None and len(args.filtra) != 0:
        filtraProgramas = args.filtra.split(',')
    else:
        filtraProgramas = programas['Sigla']
        print(filtraProgramas)
