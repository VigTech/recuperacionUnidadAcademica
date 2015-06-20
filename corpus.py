# -*- coding: utf-8 -*-
#import igraph
from sklearn.cross_validation import cross_val_score, LeaveOneOut
from sklearn.naive_bayes import MultinomialNB
import numpy
from manejadorArchivos import leer_archivo, obtener_autores, dicci_to_list
from red import Red
from os.path import basename




class Corpus:
    '''La clase representa un corpus cuyas instancias son papers representados en un vector binario cada una.

    Se separa el corpus siguiendo el estandar de scikit-learn en el que existe un atributo 'data' para la información de todas
    las instancias y un atributo 'target' para sus respectivas clases.

    '''

    data = []
    #Todas las instancias del corpus (Lista de listas)
    target = []
    #Las clases de las instancias (Lista)
    DIRECTORIO_CVS = 'CVSs/EISC/'
    DIRECTORIO_REDES = 'redes/'
    #DIRECTORIO_EISC = 'EISC/'
    DIRECTORIO_INGENIERIA = 'CVSs/Ingenieria/'
    DIRECTORIO_INDUSTRIAL = 'CVSs/Industrial/'
    DIRECTORIO_PITTS = 'CVSs/Pitts/'
    EXP_BASE = 'Base'
    EXP_BASE_WEIGHTS = 'BaseWeights'
    EXP_TODAS_MEDIDAS = 'TodasMedidas'
    EXP_ADCCAPLAS = 'ADCCAPLAS'
    EXP_CCAPLAS = 'CCAPLAS'

    def construir_corpus(self, nombre, busqueda_inicial, conjunto_a, conjunto_s, conjunto_j, conjunto_o, clasificados, conjuntos_red = None, diccionario_todos_autores = None):
        '''Construye el corpus del modelo base a partir de la búsqueda incial y los conjuntos de atributos'''
        #Booleano que indica si estamos construyendo un corpus con redes
        corpus_red = conjuntos_red != None
        #Booleano que indica si estamos construyendo un corpus con redes recibiendo un diccionario
        corpus_red_diccionario = type(conjuntos_red) is dict
        corpus = open(nombre, 'w')
        ##corpus.write('nom,nom,nom,nom\n')
        #corpus.write('a'+'\n')
        if corpus_red:
            if self.EXP_BASE_WEIGHTS in nombre:
                corpus.write('nom,nom,nom,nom,num\n')
                corpus.write('A,S,J,O,AS,R\n')
            elif self.EXP_TODAS_MEDIDAS in nombre:
                corpus.write('nom,nom,nom,nom,num,num,num\n')
                corpus.write('A,S,J,O,AD,CC,APL,AS,R\n')
            elif self.EXP_ADCCAPLAS in nombre:
                corpus.write('num,num,num,num\n')
                corpus.write('AD,CC,APL,AS,R\n')
            elif self.EXP_CCAPLAS in nombre:
                corpus.write('num,num,num\n')
                corpus.write('CC,APL,AS,R\n')
            self.red = Red(dicci_to_list(conjuntos_red),'redCorpus', range(len(conjuntos_red)))

        else:
            corpus.write('nom,nom,nom,nom\n')
            corpus.write('A,S,J,O,R\n')


        lineaBI = 0

        for lineaBI, clasificacion in zip(busqueda_inicial,clasificados):
            print 'iteracion corpus'
            perteneceA = lineaBI in conjunto_a
            perteneceS = lineaBI in conjunto_s
            perteneceJ = lineaBI in conjunto_j
            perteneceO = lineaBI in conjunto_o

            #print (perteneceA)

            if corpus_red:

                #Autores qye trabajaron en el paper lineaBI
                autores_borrados= self.obtener_autores_borrados(lineaBI,diccionario_todos_autores)
                #Diccionario autores-eid sin los autores que se borran
                dicci_sin_autores = self.generar_dicci_sin_autores(autores_borrados, conjuntos_red)
                #Red sin autores
                redsita = Red(dicci_to_list(dicci_sin_autores), self.DIRECTORIO_REDES+str(lineaBI))
                ##print 'red retornada'
                average_path_lenght = redsita.average_path_lenght()
                ##print 'APL'
                average_degree = redsita.average_degree()
                ##print 'AD'
                clustering_coefficient = redsita.clustering_coefficient()
                ##print 'CC'
                ##print 'medidas basicas'
                average_strength = redsita.average_strength()
                ##print 'AS'
                ##print 'apl'
                '''corpus.write(str(int(perteneceA))+','+str(int(perteneceS))+','+str(int(perteneceJ))+','+
                     str(int(perteneceO))+','+str(average_degree)+','+str(clustering_coefficient)+','+
                     str(average_path_lenght)+','+str(average_strength)+','+clasificacion.rstrip()+'\n')'''
                if self.EXP_BASE_WEIGHTS in nombre:
                    corpus.write(str(int(perteneceA))+','+str(int(perteneceS))+','+str(int(perteneceJ))+','+
                         str(int(perteneceO))+','+str(redsita.weights())+','+clasificacion.rstrip()+'\n')
                elif self.EXP_TODAS_MEDIDAS in nombre:
                    corpus.write(str(int(perteneceA))+','+str(int(perteneceS))+','+str(int(perteneceJ))+','+
                     str(int(perteneceO))+','+str(average_degree)+','+str(clustering_coefficient)+','+
                     str(average_path_lenght)+','+str(average_strength)+','+clasificacion.rstrip()+'\n')
                elif self.EXP_ADCCAPLAS in nombre:
                    corpus.write(str(average_degree)+','+str(clustering_coefficient)+','+
                     str(average_path_lenght)+','+str(average_strength)+','+clasificacion.rstrip()+'\n')
                elif self.EXP_CCAPLAS in nombre:
                    corpus.write(str(clustering_coefficient)+','+
                     str(average_path_lenght)+','+str(average_strength)+','+clasificacion.rstrip()+'\n')
            else:
                self.data.append([int(perteneceA), int(perteneceS), int(perteneceJ),
                                  int(perteneceO)])#, int(incide_red_sc)])
                corpus.write(str(int(perteneceA))+','+str(int(perteneceS))+','+str(int(perteneceJ))+','+
                         str(int(perteneceO))+','+clasificacion.rstrip()+'\n')



            self.target.append(int(clasificacion.rstrip()))


        #return corpus
        corpus.close()
        print self.data
        print self.target

    def obtener_atributo_existe_relacion(self, nombre_red, paper, average_strength_red_completa):
        '''Decide si un paper incide en la construcción de la red especificada.
        '''
        g = self.obtener_grafo(nombre_red, paper)
        average_strength = self.average_strength(g)
        respuesta = '1'
        if (average_strength_red_completa - average_strength == 0):
            respuesta = '0'
        return respuesta

    def average_strength(self, g):
	    return sum(g.strength(weights=g.es['weight']))/float(len(g.strength(weights=g.es['weight'])))

    '''def obtener_grafo(self, nombre_red, paper):
        return igraph.read(self.DIRECTORIO_REDES+nombre_red+'Redes/'+paper.rstrip()+".net",format="pajek")'''

    def obtener_autores_borrados(self, numero_paper, dicci):
        '''Elimina del diccionario los autores que hayan trabajado en el paper.
        Parámetros
        Número_paper: Es un entero que identifica a un paper
        dicci: Es el diccionario con el que va a ser formada la red.
        '''
        #dicci_respuesta = dicci.copy()
        autores_borrados = []
        for autor in dicci:
            if numero_paper in dicci[autor]:
                autores_borrados.append(autor)
        return autores_borrados

    def generar_dicci_sin_autores(self, autores_borrados, dicci):
        dicci_respuesta = dicci.copy()
        for autor in autores_borrados:
            if(dicci.get(autor) != None):
                del dicci_respuesta[autor]
        return dicci_respuesta

#Toma el conjunto de búsqueda inicial validado y hace las mismas validaciones con el conjunto más grande de toda la universidad
def validarExperto(papersRelevantes, archivo_validar, directorio):
    #obtenerPapersRelevantes();
    #Solo los papers relevantes
    #papersRelevantes = open(Corpus.DIRECTORIO_CVS+'relevantes.csv','r')
    #Todos los papers de la universidad
    #dataPapers = open(Corpus.DIRECTORIO_CVS+'dataPapers.csv', 'r')
    #Archivo donde va la validación 0s y 1s
    nombre_archivo_validar = basename(archivo_validar.name)
    validacion = open(directorio+'validacion'+nombre_archivo_validar, 'w')
    print validacion.name
    print basename(validacion.name)

    for paperData in archivo_validar:
        #Booleano que indica si un paperData es relevante
        papersRelevantes.seek(0)
        paperDataRelevante = False
        paperData = paperData[:-1]
        #print(paperData)
        for paperRelevante in papersRelevantes:
            #print(paperRelevante)
            paperRelevante = paperRelevante[:-1]
            #print(paperData)
            #print(paperRelevante)
            #print (paperData == paperRelevante)
            #print (paperData in paperRelevante)
            #print (paperRelevante in paperData )
            if(paperRelevante in paperData):
                paperDataRelevante = True
        if(paperDataRelevante):
            validacion.write(str(1)+'\n')
        else:
            validacion.write(str(0)+'\n')


def obtenerPapersRelevantes(validacionInicial, directorio):
    papersRelevantes = open(directorio+'relevantes.csv','w')
    papers_relevantes_fecha = open(directorio+'relevantesFecha.csv','w')
    #validacionInicial = open(Corpus.DIRECTORIO_CVS+'validacionInicial.csv', 'r')
    #Pruebas
    #a = 0
    for paper in validacionInicial:
        #Para quitar el salto de linea \n
        paper = paper[:-1]
        x = paper.split(',')
        if(x[1] == '1'):
            papersRelevantes.write(x[0]+'\n')
            papers_relevantes_fecha.write(x[2]+'\n')
            #Pruebas
            #a= a+1
            #print(a)

def dividir_archivo_fecha(archivo, archivo_fechas, fecha_division ):
    '''Crea un nuevo archivo que contenga solo los papers hasta la fecha indicada
    '''
    archivo_dividido = open('CVSs/archivoDividido.csv', 'w+')
    for fecha, instancia in zip(archivo_fechas, archivo):
        #print int(fecha.rstrip())>=fechaDivision
        if(int(fecha.rstrip())<fecha_division):
            archivo_dividido.write(instancia)
            #print 'hola'
        else:
            #entrenamiento.write(instancia)
            pass #Aquí debería escribir en el otro archivo
    #archivo_dividido.close()
    archivo.close()
    archivo_dividido.seek(0)
    return archivo_dividido

def prueba_dividir():
    #obtenerPapersRelevantes()
    dividir_archivo_fecha(open('CVSs/relevantes.csv'), open('CVSs/relevantesFecha.csv'), 2011)


def prueba():
    c = Corpus()

    busquedaInicial=leer_archivo(open(c.DIRECTORIO_CVS+'bi.csv','r'), eliminar_primero=True)
    #busquedaInicial=leer_archivo(open(c.DIRECTORIO_CVS+'dataPapers.csv','r'), eliminar_primero=True)
    conjuntoA=leer_archivo(open(c.DIRECTORIO_CVS+'a.csv','r'),eliminar_primero=True)
    conjuntoS=leer_archivo(open(c.DIRECTORIO_CVS+'s.csv','r'),eliminar_primero=True)
    conjuntoJ=leer_archivo(open(c.DIRECTORIO_CVS+'j.csv','r'),eliminar_primero=True)
    conjuntoO=leer_archivo(open(c.DIRECTORIO_CVS+'o.csv','r'),eliminar_primero=True)
    clasificados = leer_archivo(open(c.DIRECTORIO_CVS+'clasificados.csv', 'r'),eliminar_primero=True)
    #clasificados = leer_archivo(open(c.DIRECTORIO_CVS+'validacion.csv', 'r'),eliminar_primero=True)
    xmls = [open('XMLs/xml0.xml'),open('XMLs/xml1.xml'),open('XMLs/xml2.xml'),open('XMLs/xml3.xml')]
    #c.construir_corpus(busquedaInicial, conjuntoA, conjuntoS, conjuntoJ, conjuntoO, clasificados, conjuntos_red=obtener_autores(xmls, leer_archivo(open('CVSs/relevantes.csv'), eliminar_primero=False)))
    #Archivos con los eid de los papers que van a conformar la red
    archivo_papers_red = dividir_archivo_fecha(open('CVSs/EISC/relevantes.csv'), open('CVSs/EISC/relevantesFecha.csv'), 2013)
    #Lista con los eid de los papers que van a conformar la red
    lista_papers_red = leer_archivo(archivo_papers_red, eliminar_primero=False)
    #Autores-papers de la red
    dicci_contruir_red = obtener_autores(xmls, lista_papers_red)
    #Aqué deberían estar todos los autores-papers del corpus
    dicci_todos_autores_papers = obtener_autores(xmls, leer_archivo(open('CVSs/EISC/bi.csv'), eliminar_primero=True))
    c.construir_corpus(busquedaInicial, conjuntoA, conjuntoS, conjuntoJ, conjuntoO, clasificados, c.DIRECTORIO_CVS,
                       conjuntos_red=dicci_contruir_red, diccionario_todos_autores=dicci_todos_autores_papers)
    #print leer_archivo(dividir_archivo_fecha(open('CVSs/relevantes.csv'), open('CVSs/relevantesFecha.csv'), 2011), eliminar_primero=False)
    # nb = MultinomialNB()
    # v = LeaveOneOut(len(c.target))
    # presiciones = cross_val_score(nb, numpy.array(c.data), numpy.array(c.target), cv=v)#len(c.target))
    # predic = open(c.DIRECTORIO_CVS+'prediccionesUnivalle.txt', 'w')
    # for i, classif in enumerate(presiciones):
    #     print i+2, classif
    #     predic.write(str(classif)+'\n')
    # print presiciones.sum()
    # #g = c.obtener_grafo('sc', 'EID')
    # #g.write_svg('grafo3.svg')

def prueba_generar_dicci_sin_autores():
    paper =2
    dicci ={'a':[1,2],'b':[1,3], 'c':[2,5]}
    c = Corpus()
    print c.generar_dicci_sin_autores(paper, dicci)
    print dicci

'''
def anios_interesantes():
    construir_entrenamiento_prueba('CVSs/corpusTodoUnivalle', 2013)
    construir_entrenamiento_prueba('CVSs/corpusTodoUnivalle', 2012)
    construir_entrenamiento_prueba('CVSs/corpusTodoUnivalle', 2011)
'''

def prueba_validar_experto():
    #validarExperto(open(Corpus.DIRECTORIO_CVS+'relevantes.csv','r'), open(Corpus.DIRECTORIO_CVS+'dataPapers.csv', 'r'), Corpus.DIRECTORIO_CVS)
    #validarExperto(open(Corpus.DIRECTORIO_INDUSTRIAL+'relevantes.csv','r'), open(Corpus.DIRECTORIO_INDUSTRIAL+'dataPapers.csv', 'r'), Corpus.DIRECTORIO_INDUSTRIAL)
    #validarExperto(open(Corpus.DIRECTORIO_INGENIERIA+'relevantes.csv','r'), open(Corpus.DIRECTORIO_INGENIERIA+'dataPapers.csv', 'r'), Corpus.DIRECTORIO_INGENIERIA)
    validarExperto(open(Corpus.DIRECTORIO_PITTS+'relevantes.csv','r'), open(Corpus.DIRECTORIO_PITTS+'dataPapers.csv', 'r'), Corpus.DIRECTORIO_PITTS)


def prueba_obtener_papers_relevantes():
    obtenerPapersRelevantes(open(Corpus.DIRECTORIO_CVS+'validacionInicial.csv', 'r'), Corpus.DIRECTORIO_CVS)
    #obtenerPapersRelevantes(open(Corpus.DIRECTORIO_INGENIERIA+'validacionInicial.csv', 'r'), Corpus.DIRECTORIO_INGENIERIA)
    #obtenerPapersRelevantes(open(Corpus.DIRECTORIO_INDUSTRIAL+'validacionInicial.csv', 'r'), Corpus.DIRECTORIO_INDUSTRIAL)
    #obtenerPapersRelevantes(open(Corpus.DIRECTORIO_PITTS+'validacionInicial.csv', 'r'), Corpus.DIRECTORIO_PITTS)
def corpus_univalle():
    c = Corpus()

    #busquedaInicial=leer_archivo(open(c.DIRECTORIO_CVS+'bi.csv','r'), eliminar_primero=True)
    busquedaInicial=leer_archivo(open(c.DIRECTORIO_CVS+'dataPapers.csv','r'), eliminar_primero=True)
    conjuntoA=leer_archivo(open(c.DIRECTORIO_CVS+'a.csv','r'),eliminar_primero=True)
    conjuntoS=leer_archivo(open(c.DIRECTORIO_CVS+'s.csv','r'),eliminar_primero=True)
    conjuntoJ=leer_archivo(open(c.DIRECTORIO_CVS+'j.csv','r'),eliminar_primero=True)
    conjuntoO=leer_archivo(open(c.DIRECTORIO_CVS+'o.csv','r'),eliminar_primero=True)
    #clasificados = leer_archivo(open(c.DIRECTORIO_CVS+'clasificados.csv', 'r'),eliminar_primero=True)
    clasificados = leer_archivo(open(c.DIRECTORIO_CVS+'validacion.csv', 'r'),eliminar_primero=True)
    xmls = [open('XMLs/xml0.xml'),open('XMLs/xml1.xml'),open('XMLs/xml2.xml'),open('XMLs/xml3.xml')]
    #c.construir_corpus(busquedaInicial, conjuntoA, conjuntoS, conjuntoJ, conjuntoO, clasificados, conjuntos_red=obtener_autores(xmls, leer_archivo(open('CVSs/relevantes.csv'), eliminar_primero=False)))
    c.construir_corpus(busquedaInicial, conjuntoA, conjuntoS, conjuntoJ, conjuntoO, clasificados, conjuntos_red=obtener_autores(xmls, leer_archivo(dividir_archivo_fecha(open('CVSs/relevantes.csv'), open('CVSs/relevantesFecha.csv'), 2011), eliminar_primero=False)), diccionario_todos_autores=obtener_autores(xmls, leer_archivo(open('CVSs/relevantes.csv'), eliminar_primero=False)))

def construir_un_corpus(directorio):
    c = Corpus()

    busquedaInicial=leer_archivo(open(directorio+'bi.csv','r'), eliminar_primero=True)
    #busquedaInicial=leer_archivo(open(directorio+'dataPapers.csv','r'), eliminar_primero=True)
    conjuntoA=leer_archivo(open(directorio+'a.csv','r'),eliminar_primero=True)
    conjuntoS=leer_archivo(open(directorio+'s.csv','r'),eliminar_primero=True)
    conjuntoJ=leer_archivo(open(directorio+'j.csv','r'),eliminar_primero=True)
    conjuntoO=leer_archivo(open(directorio+'o.csv','r'),eliminar_primero=True)
    clasificados = leer_archivo(open(directorio+'clasificados.csv', 'r'),eliminar_primero=True)
    #clasificados = leer_archivo(open(directorio+'validacion.csv', 'r'),eliminar_primero=True)
    c.construir_corpus('CorpusVigtech', busquedaInicial, conjuntoA, conjuntoS, conjuntoJ, conjuntoO, clasificados)

#prueba_generar_dicci_sin_autores()

#obtenerPapersRelevantes()
#validarExperto()
#construirCorpus()
#construirEntrenamientoPrueba('corpusMedidas', 2012)
#prueba()
#prueba_dividir()
#obtenerPapersRelevantes()
#validarExperto()
#anios_interesantes()
#prueba_obtener_papers_relevantes()
#prueba_validar_experto()
#construir_un_corpus(Corpus.DIRECTORIO_CVS)
#construir_un_corpus
#construir_un_corpus(Corpus.DIRECTORIO_PITTS)
#prueba()