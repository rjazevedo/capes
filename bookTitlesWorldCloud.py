#!/usr/bin/env python

from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv
import string
import sys

def FiltraColuna2(lista):
    if len(lista) > 2:
        return string.replace(lista[2].strip(), ' ', '')
    else:
        return ''

booktitles = map(lambda x: FiltraColuna2(x), list(csv.reader(open('dados/producoes-2013-2016.csv'), delimiter=';')))

text = ' '.join(booktitles)

# Generate a word cloud image
wordcloud = WordCloud().generate(text)

# Display the generated image:
# the matplotlib way:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.savefig('wordcloud.png')
plt.show()
sys.exit(0)

# The pil way (if you don't have matplotlib)
# image = wordcloud.to_image()
# image.show()
