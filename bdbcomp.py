#!/usr/bin/python
# -*- coding: utf-8 -*-

import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
import html2text
import csv
import codecs
import sys
import os
import pickle

def CreateBrowser():

    # Browser
    br = mechanize.Browser()

    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
#    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=10)

    # Want debugging messages?
#    br.set_debug_http(True)
#    br.set_debug_redirects(True)
#    br.set_debug_responses(True)

    # User-Agent (this is cheating, ok?)
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

    return br

def BuscaArtigos(br, eventos):
    artigos = []

    for ano, nome, link in eventos:
        print nome, '...',

        br.open('http://www.lbd.dcc.ufmg.br/bdbcomp/servlet/' + link)
        soup = BeautifulSoup(br.response().read(), convertEntities=BeautifulSoup.HTML_ENTITIES)
        ul = soup.body.fetch(name='ul')
        li = ul[1].fetch(name = 'li')
        for item in li:
            dados = item.fetch(name = 'a')
            if len(dados) != 0:
                titulo = dados[-1].text
                autores = [dados[i].text for i in range(0, len(dados) - 1)]
                artigo = [ano, nome, titulo]
                artigo.extend(autores)
                artigos.append(artigo)
        print len(li), 'artigos coletados.'

    return artigos

def BuscaEventos(br, anos):

    eventos = []
    for (ano, dados) in anos:
        eventosAno = dados.fetch(name = 'li')
        for evento in eventosAno:
            nome = evento.a.text
            link = evento.a['href']
            eventos.append([ano, nome, link])

    return eventos

def BuscaAnos(br):

    br.open('http://www.lbd.dcc.ufmg.br/bdbcomp/servlet/ListaEventos')
    soup = BeautifulSoup(br.response().read(),convertEntities=BeautifulSoup.HTML_ENTITIES)

    ul = soup.body.fetch(name='ul')

    eventos2016 = ul[3]
    eventos2015 = ul[4]
    eventos2014 = ul[5]
    eventos2013 = ul[6]

    return [[2013, eventos2013],
            [2014, eventos2014],
            [2015, eventos2015],
            [2016, eventos2016]]


def EncodeAll(lista):
    novaLista = []
    for item in lista:
        novaLista.append(map(lambda x: unicode(x).encode('utf-8'), item))

    return novaLista

br = CreateBrowser()

# artigos = EncodeAll(BuscaArtigos(br, [[2013, u'I Workshop de Transparência em Sistemas', 'Evento?id=723']]))
#
# saida = csv.writer(open('bdbcomp.csv', 'wt'), delimiter=';')
# saida.writerows(artigos)
#
# sys.exit(0)

anos = BuscaAnos(br)
eventos = BuscaEventos(br, anos)
artigos = EncodeAll(BuscaArtigos(br, eventos))

saida = csv.writer(open('bdbcomp.csv', 'wt'), delimiter=';')
saida.writerows(artigos)


