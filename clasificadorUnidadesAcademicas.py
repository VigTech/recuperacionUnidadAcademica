__author__ = 'vigtech'
# -*- coding: utf-8 -*-
from manejadorArchivos import leer_archivo
from corpus import Corpus
from clasificador import NaiveBayes
import copy
import json


class ClasificadorUnidadesAcademicas:
    NOMBRE_EISC = 'eisc'
    NOMBRE_INDUSTRIAL ='dua'

    def __init__(self, unidad_academica):
        self.unidad_academica = unidad_academica
        self.directorio = 'csvs/%s/'%(unidad_academica)




    def procesar_json_entrada(self, json_entrada):
        conjuntos = json.loads(json_entrada)
        self.clasificar = map(str, conjuntos['clasificar'])
        self.conjunto_a = map(str, conjuntos['a'])
        self.conjunto_s = map(str, conjuntos['s'])
        self.conjunto_j= map(str, conjuntos['j'])
        self.conjunto_o= map(str, conjuntos['o'])
        return  conjuntos

    def clasificar_docs(self):
        c = Corpus()


        clasificacion_ficticia = ['1']*len(self.clasificar)
        #clasificados = leer_archivo(open(directorio+'validacion.csv', 'r'),eliminar_primero=True)
        nombre_entrenamiento = self.unidad_academica+'CorpusTraining.csv'
        nombre_prueba = self.unidad_academica+'CorpusTest.csv'
        prueba = c.construir_corpus(nombre_prueba, self.clasificar, self.conjunto_a, self.conjunto_s, self.conjunto_j, self.conjunto_o,
                                    clasificacion_ficticia)

        nv = NaiveBayes(open(nombre_entrenamiento), open(nombre_prueba))
        nv.medidas()
        print nv.clasificadosNB
        return nv.clasificadosNB


def prueba():
    c = ClasificadorUnidadesAcademicas(ClasificadorUnidadesAcademicas.NOMBRE_EISC)
    print 'hola'
    c.procesar_json_entrada(open('jsonTesisCesar.json'))
#prueba()






