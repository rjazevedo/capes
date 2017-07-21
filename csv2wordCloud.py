#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv
import string
import sys

def FilterData(l, column, value):
    answer = []
    for line in l:
        if len(line) > column:
            if line[column] == value:
                answer.append(line)

    return answer

def SelectColumn(l, column):
    if len(l) > column:
        return string.replace(l[column].strip(), ' ', '')
    else:
        return ''

def CreateWorldCloud(wordList, outFile):
    text = ' '.join(wordList)

    # Generate a word cloud image
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(outFile)
    sys.exit(0)


def CreateWordCloud(inputFile, outputFile, column, filter, value, delimiter):
    print('Reading input file:', inputFile, '...')
    inputData = list(csv.reader(open(inputFile), delimiter=delimiter))
    print(len(inputData), 'lines read.')

    if (filter != None) and (value != None):
        print('Filtering data...')
        filteredData = FilterData(inputData, filter, value)
        print(len(filteredData), 'lines remaining.')
    else:
        filteredData = inputData

    data = map(lambda x: SelectColumn(x, int(column)), filteredData)

    if len(data) == 0:
        print('No data remaining. Exiting...')
        sys.exit(0)

    print('Creating cloud...')
    CreateWorldCloud(data, outputFile)
    print('Saving file:', outputFile)

    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create Word Cloud from one colum of CSV file')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output PNG file')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter')
    parser.add_argument('-c', '--column', type=int, required=True, help='CSV column to create World Cloud')
    parser.add_argument('-f', '--filter', type=int, required=False, help='CSV column to filter')
    parser.add_argument('-v', '--value', type=str, required=False, help='CSV value to filter')

    args = parser.parse_args()

    delimiter = ';'
    if (args.delimiter != None):
        delimiter = args.delimiter

    CreateWordCloud(args.input, args.output, args.column,
                    args.filter, args.value, delimiter)
