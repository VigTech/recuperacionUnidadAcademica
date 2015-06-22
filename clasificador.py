#!/usr/bin/env python
# -*- coding: utf-8 -*-
from manejadorArchivos import leer_corpus, escribir_archivo, escribir_archivo2
import numpy
from scipy import stats
from sklearn.metrics import roc_auc_score, roc_curve, auc# average_precision_score, precision_score
import ntpath
#import pylab as pl
#from herramienta.views import DIRECTORIO_ARCHIVOS

DIRECTORIO_ARCHIVOS = 'herramienta/preprocesamiento/archivosPruebas/'
class NaiveBayes:
    #corpus = open('corpus.csv', 'r')
    #Cantidad de relevantes en el atributo i con valor j.
    cant_relevantes_atributo_valor = []
    #Cantidad de relevantes fuera del conjunto i
    nni1 = []
    #Cantidad no relevantes en el atributo i con el valor j
    cant_irrelevantes_atributo_valor = []
    #Cantidad de documentos no relevantes fuera del conjunto i
    nni0 = []
    #Cantidad de relevantes
    cant_relevantes = 0
    #Cantidad no relevantes
    cant_irrelevantes = 0
    #Cantidad de documentos
    cant_instancias = 0
    #Clasificación hecha a un test
    clasificadosNB = []
    #
    clasificadosExperto = []
    #Cantidad de posibles valores para el atributo i
    cant_valores_atributo = []
    #Lista de diccionarios que guarda la media y desviación estándar de cada atributo numérico si es relevante
    media_devastandar_relevantes_atributo = []
    #Lista de diccionarios que guarda la media y desviación estándar de cada atributo numérico si es irrelevante
    media_devastandar_irrelevantes_atributo = []

    archivo_resultados = None

    probabilidades1 = []

    def __init__(self, archivo_entrenamiento, archivo_prueba = None, funcion_test=None):
        #print (3)
        print archivo_entrenamiento.name#, archivo_prueba.name
        self.corpus = archivo_entrenamiento
        self.data, self.target, self.data_numeric = leer_corpus(archivo_entrenamiento)
        self.data_numeric = lista_lista_to_float(self.data_numeric)
        #print self.data, self.target
        self.cant_atributos = len(self.data[0])
        self.cant_atributos_numericos = len(self.data_numeric[0])
        self.posibles_valores_atributo = obtener_valores_atributos(self.cant_atributos, self.data)
        self.todos_valores_numericos_atributo = obtener_todos_valores_atributos(self.cant_atributos_numericos, self.data_numeric)
        self.probabilidades1 = []
        self.inicializarVariablesModelo()
        self.contar()
        if(archivo_prueba != None):
            self.archivo_test = archivo_prueba
            data, target, data_numeric = leer_corpus(archivo_prueba)
            self.clasificar(data,data_numeric,target)


    def inicializarVariablesModelo(self):

        self.cant_relevantes_atributo_valor = crear_lista_listas(self.cant_atributos,self.posibles_valores_atributo)
        self.cant_irrelevantes_atributo_valor = crear_lista_listas(self.cant_atributos,self.posibles_valores_atributo)
        self.clasificadosNB = []
        self.clasificadosExperto = []
        self.media_devastandar_relevantes_atributo= [None]*self.cant_atributos_numericos
        self.media_devastandar_irrelevantes_atributo= [None]*self.cant_atributos_numericos

        print self.cant_relevantes_atributo_valor
    def contar(self):
        self.entrenar_datos_discretos()
        self.entrenar_datos_continuos()
        print (self.cant_relevantes_atributo_valor, self.cant_instancias, self.cant_irrelevantes, self.cant_relevantes)
        self.corpus.close

    def entrenar_datos_discretos(self):
        for k, instancia in enumerate(self.data):
            for i, atributo in enumerate(instancia):
                for j, valor in enumerate(self.posibles_valores_atributo[i]):
                    if(atributo == valor):
                        if (self.target[k]  == '1'):
                            self.cant_relevantes_atributo_valor[i][j] += 1
                        elif (self.target[k]  == '0'):
                            self.cant_irrelevantes_atributo_valor[i][j] += 1
            if (self.target[k]  == '1'):
                self.cant_relevantes += 1
            elif (self.target[k]  == '0'):
                self.cant_irrelevantes += 1
            self.cant_instancias += 1


    def entrenar_datos_continuos(self):
        valores_relevantes_atributo = [None]*self.cant_atributos_numericos
        valores_irrelevantes_atributo = [None]*self.cant_atributos_numericos
        for k, instancia in enumerate(self.data_numeric):
            for i, atributo in enumerate(instancia):
                if (self.target[k]  == '1'):
                    if type(valores_relevantes_atributo[i]) is not list:
                        valores_relevantes_atributo[i]=[]
                    valores_relevantes_atributo[i]= valores_relevantes_atributo[i] + [atributo]
                elif (self.target[k]  == '0'):
                    if type(valores_irrelevantes_atributo[i]) is not list:
                        valores_irrelevantes_atributo[i]=[]
                    valores_irrelevantes_atributo[i] = valores_irrelevantes_atributo[i] + [atributo]
        print valores_relevantes_atributo
        print valores_irrelevantes_atributo
        for i in range(self.cant_atributos_numericos):
            self.media_devastandar_relevantes_atributo[i]=dict(mean=numpy.mean(numpy.array(valores_relevantes_atributo[i])),
                                                               std = numpy.std(numpy.array(valores_relevantes_atributo[i])))
            self.media_devastandar_irrelevantes_atributo[i]=dict(mean=numpy.mean(numpy.array(valores_irrelevantes_atributo[i])),
                                                            std = numpy.std(numpy.array(valores_irrelevantes_atributo[i])))
        print self.media_devastandar_irrelevantes_atributo
        print self.media_devastandar_relevantes_atributo




    def clasificar(self, data, data_numeric, target):
        #documento = archivo_prueba
        #data, target, data_numeric = leer_corpus(documento)
        #self.archivo_resultados = open('resultados/experimento.csv', 'w')
        i = 0
        data_numeric=lista_lista_to_float(data_numeric)

        apriori_relevante = self.cant_relevantes/float(self.cant_instancias)
        apriori_irrelevante = self.cant_irrelevantes/float(self.cant_instancias)
        for instancia_continuos, instancia_discretos in zip(data_numeric, data):
            print instancia_continuos, instancia_discretos
            probabilidad1 = self.productoria_atributos_dada_clase_discreto(instancia_discretos, relevante=True) *\
                            self.productoria_atributos_dada_clase_continuo(instancia_continuos,relevante=True) * apriori_relevante
            probabilidad0 = self.productoria_atributos_dada_clase_discreto(instancia_discretos, relevante=False)*\
                            self.productoria_atributos_dada_clase_continuo(instancia_continuos,relevante=False) * apriori_irrelevante
            print "Probabilidad de que el documento "+str(i+1)+" sea relevante: ", (probabilidad1/float((probabilidad1 + probabilidad0)))*100,"%"
            print "Probabilidad de que el documento "+str(i+1)+" no sea relevante: ", (probabilidad0/float((probabilidad1 + probabilidad0)))*100,"%"
            #self.probabilidades1.append(probabilidad1)
            self.probabilidades1.append((probabilidad1/float((probabilidad1 + probabilidad0))))
            if( max(probabilidad1, probabilidad0) == probabilidad1 ):
                print "El documento "+str(i+1)+" ha sido clasificado como Relevante"
                self.clasificadosNB.append(1)
            else:
                print "El documento "+str(i+1)+" ha sido clasificado como No Relevante"
                self.clasificadosNB.append(0)
            self.clasificadosExperto.append(int(target[i]))
            i += 1

    def productoria_atributos_dada_clase_discreto(self, instancia, relevante=True):
        if relevante == True:
            cant_atributo_valor = self.cant_relevantes_atributo_valor
            cant = self.cant_relevantes
            mensaje = 'relevante'
        else:
            cant_atributo_valor = self.cant_irrelevantes_atributo_valor
            cant = self.cant_irrelevantes
            mensaje = 'irrelevante'
        probabilidad = [None]*self.cant_atributos
        for i, atributo in enumerate(instancia):
            for j, valor in enumerate(self.posibles_valores_atributo[i]):
                if(atributo == valor):
                    probabilidad[i] = (cant_atributo_valor[i][j] + 1) / float((cant + self.cant_atributos))
        print "probabilidades discretas "+mensaje+": ",probabilidad
        return self.productoria(probabilidad)

    def productoria_atributos_dada_clase_continuo(self, instancia, relevante = True):
        if relevante == True:
            media_devastandar_atributo = self.media_devastandar_relevantes_atributo
            mensaje = 'relevante'
        else:
            media_devastandar_atributo = self.media_devastandar_irrelevantes_atributo
            mensaje = 'irrelevante'

        probabilidad= [None]*self.cant_atributos_numericos
        for i, atributo in enumerate(instancia):
            print 'media', media_devastandar_atributo[i]['mean']
            print 'std', media_devastandar_atributo[i]['std']
            probabilidad[i] = stats.norm.pdf(atributo, loc=media_devastandar_atributo[i]['mean'],
                                             scale=media_devastandar_atributo[i]['std'])
            if probabilidad[i]==0:
                probabilidad[i]=0.00000000000000001
        print "probabilidades continuas "+mensaje+": ",probabilidad
        #print self.productoria(probabilidad)
        return self.productoria(probabilidad)



    def productoria(self, probabilidad):
        productoria = 1
        for i in probabilidad:
            productoria *= i
        return productoria

    def medidas(self):
        #parece que esta línea no hace nada. :p
        #testC = open("testComprobacion.csv")
        nombre_entrenamiento = self.corpus.name
        nombre_prueba = self.archivo_test.name
        nombre_entrenamiento=ntpath.basename(nombre_entrenamiento).replace('.csv','')
        nombre_prueba=ntpath.basename(nombre_prueba).replace('.csv','')

        #self.archivo_resultados = open('archivosPruebas/resultados'+nombre_entrenamiento+nombre_prueba+'.txt', 'w')
        recuperadosYRelevantes = 0
        recuperados = 0
        relevantes = 0
        clasificados_bien = 0
        fp = 0
        negativos = 0
        for i in range(len(self.clasificadosNB)):
            if(self.clasificadosNB[i] == 1 and self.clasificadosExperto[i] == 1):
                recuperadosYRelevantes +=1
                recuperados += 1
                relevantes += 1
            elif (self.clasificadosNB[i] == 1):
                recuperados += 1
                fp += 1
                negativos += 1
            elif (self.clasificadosExperto[i] == 1):
                relevantes += 1
            else:
                negativos += 1
            if (self.clasificadosNB[i] == self.clasificadosExperto[i]):
                clasificados_bien += 1
            else:
                print 'clasificado mal', i+1, self.clasificadosExperto[i]
            #print i
        presicion1 = recuperadosYRelevantes/float(recuperados)
        recall1 = recuperadosYRelevantes/float(relevantes)
        #fpr = fp / float(negativos)
        print len(self.probabilidades1), len(self.clasificadosExperto)
        print self.clasificadosExperto
        #roc= roc_auc_score(self.clasificadosExperto, self.probabilidades1)
        #print 'Presicion: '+str(recuperadosYRelevantes/float(recuperados))
        #print 'Recall: '+str(recuperadosYRelevantes/float(relevantes))
        #print 'Accuracy: '+str(clasificados_bien/float(len(self.clasificadosNB)))
        #print 'Clasificados bien: '+str(clasificados_bien)
        #print 'roc11: '+str(roc)
        #print 'fpr: '+str(fpr)
        #print 'roc2: '+str(average_precision_score(self.clasificadosExperto, self.clasificadosNB))
        #escribir_archivo(self.clasificadosNB)
        #self.archivo_resultados.write('Presicion: '+str(presicion1)+'\n')
        #self.archivo_resultados.write('Recall: '+str(recall1)+'\n')
        #self.archivo_resultados.write('ROC Area: '+str(roc)+'\n')
        #self.archivo_resultados.write('FPR: '+str(fpr)+'\n')
        #self.archivo_resultados.close()
        #escribir_archivo(self.clasificadosNB)
        DIRECTORIO_ROCS = 'archivosPruebas/ROCS/'
        #escribir_archivo2(self.clasificadosExperto,DIRECTORIO_ROCS, nombre_entrenamiento+nombre_prueba+'ClasificacionesExperto')
        #escribir_archivo2(self.probabilidades1,DIRECTORIO_ROCS, nombre_entrenamiento+nombre_prueba+'Probabilidades')




def crear_lista_listas(filas, columnas):
    '''Crea una lista de listas a partir de una cantidad de filas y una cantidad de columna para cada una de ellas.

    Parámetros:
    filas: (entero) número de filas
    columnas: (lista de enteros) cantidad de columnas por cada fila
    '''
    matriz = [None]*filas
    for i in range(filas):
        matriz[i] = [0]*len(columnas[i])
    print matriz
    return matriz

def obtener_valores_atributos(cant_atributos, data):
    '''Devuelve los posibles valores que puede tener cada uno de los atributos de un corpus
    Parámetros:
    cant_atributos : (int)
                     Es la cantidad de atributos que tiene el corpus. Es igual que len(data[0])
    data :           (lista de listas)
                     Es el corpus en donde cada instancia se representa con su lista de características
    '''
    todos_valores_atributo = obtener_todos_valores_atributos(cant_atributos, data)
    valores_atributo = []
    for atributo in todos_valores_atributo:
        valores_atributo.append(list(set(atributo)))
    return valores_atributo

def obtener_todos_valores_atributos(cant_atributos, data):
    '''Devuelve una lista de listas con los valores de cada atributo que hay en la totalidad del corpus
    Parámetros:
    cant_atributos : int
                     Es la cantidad de atributos que tiene el corpus. Es igual que len(data[0])
    data :           lista de listas
                     Es el corpus en donde cada instancia se representa con su lista de características
    '''

    todos_valores_atributo = [None]*cant_atributos
    for instancia in data:
        for i, valor in enumerate(instancia):
            if type(todos_valores_atributo[i]) is not list:
                todos_valores_atributo[i] = []
            todos_valores_atributo[i].append(valor)
            #print valores_atributo
    return todos_valores_atributo

def lista_lista_to_float(lista_lista):
        respuesta = []
        for elemento_lista in lista_lista:
            elemento_lista = map(float, elemento_lista)
            respuesta.append(elemento_lista)
        return respuesta

#print crear_lista_listas(3, [1, 2, 3])
def prueba():
    print lista_lista_to_float([[1,2,2],['3',3,'3']])

'''
def dibujar_roc(clasificaciones_experto, probabilidades):
    # Compute ROC curve and area the curve
    fpr, tpr, thresholds = roc_curve(clasificaciones_experto, probabilidades)
    roc_auc = auc(fpr, tpr)
    print "Area under the ROC curve : %f" % roc_auc

    # Plot ROC curve
    pl.clf()
    pl.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
    pl.plot([0, 1], [0, 1], 'k--')
    pl.xlim([0.0, 1.0])
    pl.ylim([0.0, 1.0])
    pl.xlabel('False Positive Rate')
    pl.ylabel('True Positive Rate')
    pl.title('Receiver operating characteristic example')
    pl.legend(loc="lower right")
    pl.show()
'''
#prueba()
# # #print (2)
# nb = NaiveBayes(open('corpusUnivalle.csv'))
# # #nb = NaiveBayes('corpusUnivalleTraining.csv')
#nb = NaiveBayes(open('preprocesamiento/CVSs/corpusBusquedaInicial.csv'))
#nb = NaiveBayes(open('preprocesamiento/CVSs/corpusBusquedaInicial.csv'),archivo_prueba=open('preprocesamiento/CVSs/corpusBusquedaInicial.csv'))
#nb.corpus = open('corpusBusquedaInicial.csv', 'r')
#nb.contar()
#nb.clasificar(open('preprocesamiento/CVSs/corpus.csv'))
# #nb.clasificar('corpusUnivalle.csv')
# # #nb.clasificar('corpusUnivalleTest.csv')
# nb.clasificar(open('corpusUnivalle.csv'))
# #nb.corpus = open('corpusBusquedaInicial.csv', 'r')
# # print(nb.clasificadosNB)
# # print(nb.clasificadosExperto)
#nb.medidas()
# # #print (nb.productoria([1,2,3]))

