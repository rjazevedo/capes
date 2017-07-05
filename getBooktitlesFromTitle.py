#!/usr/bin/python
# -*- coding: utf-8 -*-

# Arquivo CSV no formato
# Somente o titulo do artigo, um por linha

import argparse
import string
import xml.sax

inputData = {}

def CleanText(s):
    return filter(lambda x: x.isalnum(), s)


def ReadInputFile(filename):
#Open input file. So far, only one field per line containing the paper title
    answer = {}
    originalList = []
    counter = 0
    for l in open(filename, 'rU').readlines():
        l = l.replace('\n', '')
        text = CleanText(l.decode('utf-8').lower())
        line = [counter, text]
#        line.extend(map(lambda x: (x.decode('utf-8')).lower(), l.split(';')))
        answer[line[1]] = line
        originalList.append(list(line))
        counter += 1

    return (answer, originalList)


def PrepareOutput(data, originalList):
    answer = []
    for counter,name in originalList:
        line = list(data[name])
        line[0] = counter
        answer.append(line)

    return answer


def SaveOutputFile(filename, data):
#Unpack the data dictionary and write the CSV file output

    outFile = open(filename, 'wt')
    outFile.write('id;title;booktitle;year;pages;crossref;volume;doi;url;authors\n')
    for line in data:
        l = string.join(map(lambda x: '"' + unicode(x).encode('utf-8') + '"', line), ';') + '\n'
        outFile.write(l)
    outFile.close()

class DBLPHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.currentData = ''
        self.validKeys = ['title', 'booktitle', 'year', 'pages', 'crossref', 'number', 'ee', 'url']
        self.authors = []
        self.keys = {}
        self.count = 0
        self.skipArticles = 0
        self.skipInProceedings = 0
        self.npages = 0
        self.year = 0
        self.found = 0
        self.go = False

    def startElement(self, name, attrs):
        self.currentData = name
        if name == 'inproceedings':
            self.go = True
            self.keys = {}
            for i in self.validKeys:
                self.keys[i] = ''
            self.authors = []

    def endElement(self, name):
        if name == 'inproceedings':
            self.go = False
            if len(self.keys['title']) != 0:
                if self.keys['title'][-1] == '.':
                    self.keys['title'] = self.keys['title'][:-1]
            self.count += 1
            key = CleanText(self.keys['title'])
            if key in inputData:
                for validKey in self.validKeys:
                    if validKey != 'title':
                        if validKey == 'url':
                        # Add prefix to URL
                            inputData[key].append('http://dblp.uni-trier.de/' + self.keys.get(validKey, ''))
                        else:
                        # Add unmodified fields directly
                            inputData[key].append(self.keys.get(validKey, ''))

                inputData[key].append(','.join(self.authors))
                self.found += 1
                print '*** Found', self.keys['booktitle']
            else:
                if self.skipInProceedings == 10000:
                    print('Skipping Proceedings')
                    self.skipInProceedings = 0
                else:
                    self.skipInProceedings += 1
        if name == 'article':
            if self.skipArticles == 10000:
                print('Skipping Articles')
                self.skipArticles = 0
            else:
                self.skipArticles += 1

    def characters(self, content):
        if self.go:
            if self.currentData in self.validKeys:
                if self.currentData in self.keys:
                    self.keys[self.currentData] += content.replace('\n', '').lower()
                else:
                    self.keys[self.currentData] = content.replace('\n', '').lower()
            elif self.currentData == 'author':
                self.authors.append(content.replace('\n', ''))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get Booktitles from DBLP XML file based on paper titles')
    parser.add_argument('-d', '--dblp', type=str, required=True, help='Input DBLP XML file')
    parser.add_argument('-i', '--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output CSV file')
    args = parser.parse_args()

    print('Reading input file...')
    (inputData, originalList) = ReadInputFile(args.input)
    print(len(inputData), 'records read.')

    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # override the default ContextHandler
    Handler = DBLPHandler()
    parser.setContentHandler(Handler)

    print('Reading DBLP XML file ')
    parser.parse(args.dblp)

    print(Handler.count, 'records read.')

    print(Handler.found, 'records found.')

    outputData = PrepareOutput(inputData, originalList)

    SaveOutputFile(args.output, outputData)
