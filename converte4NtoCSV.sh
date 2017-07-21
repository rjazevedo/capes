#!/bin/bash

for programa in *.xlsx
do
  pasta=${programa/.xlsx/}
  mkdir -p $pasta
  cd $pasta
  xlsx2csv --delimiter \; -a "../$programa" .
  cd ..
done

mkdir 4N
for a in *P? ; do mv $a/Produção.csv 4N/${a}-tudo.csv; done

for a in 4N/*-tudo.csv
do
  ../filtra4N.py -i $a -o ${a/-tudo.csv/-selecionado.csv}
done
