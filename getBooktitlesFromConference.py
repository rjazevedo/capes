#!/usr/bin/python

# Template file header
# URL (DBLP), Sigla (DBLP), Nome (DBLP)

import argparse
import csv
import requests
import sys
import time
import BeautifulSoup
import string
import os
import codecs
import string
import unicodedata

def ReadInputFile(filename):
    answer = []
    for l in open(filename, 'rU').readlines():
        print l
        line = map(lambda x : x.decode('utf-8'), l.split(';'))
        answer.append(line)

    # with codecs.open(filename, 'rU', 'utf-8') as csvfile:
    #     dialect = csv.Sniffer().sniff(csvfile.read(), delimiters=';,')
    #     csvfile.seek(0)
    #     content = list(csv.reader(csvfile, dialect = dialect))
    #     return content, dialect

    return answer


def SaveOutputFile(filename, data):

    outFile = open(filename, 'wt')
    for line in data:
        l = string.join(map(lambda x : '"' + x.encode('utf-8') + '"', line), ';') + '\n'
        outFile.write(l)
    outFile.close()

    # csvfile = csv.writer(codecs.open(filename, 'wt', 'utf-8'), dialect = dialect)
    # for line in data:
    #     print line[3], line[4]
    #     line[3] = codecs.encode(line[3], 'utf-8', 'ignore')
    #     line[4] = codecs.encode(line[4], 'utf-8', 'ignore')
    #     csvfile.writerow(line)
    return


def ToString(field):
    if field != None:
        return field.text
    else:
        return ''


def GetXMLConferenceData(url):
    try:
        xml = requests.get(url)
    except requests.exceptions.RequestException as e:
        print e
        return ['', '', '', '', '', '', '']

    parsed = BeautifulSoup.BeautifulSoup(xml.text)
    year = ToString(parsed.year)
    title = ToString(parsed.title)
    booktitle = ToString(parsed.booktitle)
    publisher = ToString(parsed.publisher)
    series = ToString(parsed.series)
    isbn = ToString(parsed.isbn)
    ee = ToString(parsed.ee)

    print year, booktitle

    return [year, booktitle, title, publisher, series, isbn, ee]


def DBLPCrawler(url):
    # Receives the DBLP URL to crawl and returns the short name and full name as a tuple

    print 'Crawling DBLP:', url, '->',

    # download url content
    try:
        if url[-1] == '/':
            url = url[:-1]

        if url[0:4] != 'http':
            url = 'http://' + url

        page = requests.get(url)
    except requests.exceptions.RequestException as e:
        print e
        return ('', '')

    # parse file
    parsed = BeautifulSoup.BeautifulSoup(page.text)

    # get the first H1 that contains the expanded name
    h1 = parsed.findAll('h1')
    if (len(h1) > 0):
        fullName = h1[0].text
    else:
        fullName = ''

    # short name is the last token of the URL
    shortName = string.upper(url.split('/')[-1])

    print shortName, '|', fullName
    answer = []

    for link in parsed.findAll('a', href=True):
        if link.text == 'XML':
            conference = GetXMLConferenceData(link['href'])
            line = [url, shortName, fullName]
            line.extend(conference)
            answer.append(line)

    return answer


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Update Conference Information file')
    parser.add_argument('-n', '--name', action='store_true', help='Fetch DBLP Canonical name')
    parser.add_argument('-b', '--booktitle', action='store_true', help='Fetch DBLP Booktitles')
    parser.add_argument('-s', '--sleep', type=int, help='Sleep time in seconds between web queries (default: 20)')
    parser.add_argument('source', type=str, help='Source CSV file')
    parser.add_argument('destination', type=str, help='Destination CSV file')
    args = parser.parse_args()

    inputData = ReadInputFile(args.source)

    if not args.name and not args.booktitle:
        print('At least one option should be selected (-n or -b). Use --help for help.')
        sys.exit(1)

    outputData = []
    if args.sleep != None:
        sleepTime = args.sleep
    else:
        sleepTime = 120

    firstLine = inputData[0]
    firstLine.extend(['Year', 'BookTitle', 'Title', 'Publisher', 'Series', 'ISBN', 'EE'])
    outputData.append(firstLine)

    if args.booktitle:
        for line in inputData[1:]:
            # Columns description on top of this code
            if line[0] != '':
                answer = DBLPCrawler(line[0])
                outputData.extend(answer)
                time.sleep(sleepTime)

    SaveOutputFile(args.destination, outputData)
