#!/usr/bin/python
# -*- coding: utf-8 -*-

# Filter lines of a CSV file that does not contain a specified column value

from __future__ import print_function
import argparse
import string
import csv
import sys

def ReadInputFile(CSVfile, delimiter):
    return list(csv.reader(open(CSVfile), delimiter=delimiter))

def FilterRows(data, column, value):
    answer = []

    for line in data:
        if len(line) > column:
            if line[column] != value:
                answer.append(line)

    return answer

def FilterOutCSVFile(inputFile, outputFile, headerRows, column, value, delimiter):
    print('Reading input CSV:', inputFile, '...')
    inputData = ReadInputFile(inputFile, delimiter)

    header = inputData[0:headerRows]
    data = inputData[headerRows:]

    print('Filtering data...')
    filteredData = FilterRows(data, column, value)

    if len(filteredData) == 0:
        print('No data available. Exiting.')
        return

    print('Writing output file:', outputFile, '...')
    outputData = header
    outputData.extend(filteredData)
    csv.writer(open(outputFile, 'wt'), delimiter=delimiter).writerows(outputData)
    return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Exclude rows of CSV file based on one column value, keeping file header')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-n', '--header', type=int, required=True, help='Number of header lines')
    parser.add_argument('-c', '--column', type=int, required=True, help='Column to select')
    parser.add_argument('-v', '--value', type=str, required=True, help='Value to exclude')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file')
    parser.add_argument('-d', '--delimiter', type=str, required=False, help='CSV delimiter - default=;')

    args = parser.parse_args()
    header = int(args.header)
    column = int(args.column)

    if args.delimiter != None:
        delimiter = args.delimiter
    else:
        delimiter = ';'

    FilterOutCSVFile(args.input, args.output, header, column, args.value, delimiter)
