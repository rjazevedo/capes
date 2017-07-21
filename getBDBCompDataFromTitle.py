#!/usr/bin/python
# -*- coding: utf-8 -*-

# Arquivo CSV no formato
# Somente o titulo do artigo, um por linha

from __future__ import print_function
import argparse
import string
import sys
import csv
import unicodedata

inputData = {}

def CleanText(s):
    txt = ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))
    return filter(lambda x: x.isalnum(), txt)


def ReadInputFile(filename):
    # Open input file. So far, only one field per line containing the paper title
    originalList = []
    counter = 0
    for l in open(filename, 'rU').readlines():
        l = l.replace('\n', '')
        text = CleanText(l.decode('utf-8').lower())
        line = [counter, text]
        originalList.append(line)
        counter += 1

    return originalList


def ReadBDBComp(filename):
    # Open BDBComp file. BDBComp fields are: year, title, title without edition, shortname, paper name, authors...
    bdbcomp = list(csv.reader(open(filename), delimiter=';'))
    answer = {}
    for l in bdbcomp:
        item = map(lambda x: x.decode('utf-8'), l)
        answer[CleanText(item[4]).lower()] = item

    return (answer, bdbcomp)


def GetBDBCompData(titles, bdbcomp):

    answer = []
    counter = 0
    for line, title in titles:
        if title in bdbcomp:
            answer.append(bdbcomp[title])
            counter += 1
        else:
            answer.append([title])

    print(counter, 'records found.')
    return answer


def PrepareOutput(data, originalList):
    answer = []
    for counter, name in originalList:
        line = list(data[name])
        line[0] = counter
        answer.append(line)

    return answer


def SaveOutputFile(filename, data):
    # Unpack the data dictionary and write the CSV file output

    outFile = open(filename, 'wt')
    outFile.write('')
    for line in data:
        l = string.join(map(lambda x: '"' + unicode(x).encode('utf-8') + '"', line), ';') + '\n'
        outFile.write(l)
    outFile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get conference name from BDBComp file based on paper titles')
    parser.add_argument('-b', '--bdbcomp', type=str, required=True, help='Input BDBComp CSV file')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file containing paper titles')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV file')
    args = parser.parse_args()

    print('Reading input file...')
    titles = ReadInputFile(args.input)
    print(len(titles), 'records read.')

    print('Reading BDBComp CSV file ')
    (bdbcomp, originalBDBComp) = ReadBDBComp(args.bdbcomp)
    print(len(bdbcomp), 'records read from BDBComp.')

    outputData = GetBDBCompData(titles, bdbcomp)

    SaveOutputFile(args.output, outputData)

    # outputData = PrepareOutput(inputData, originalList)
    #
    # SaveOutputFile(args.output, outputData)
