# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
'''Este módulo sirve para leer archivos y convertirlos en listas.'''

DIRECTORIO_CVS = 'CVSs/'


def escribir_archivo(lista):
    pdfs = open('listaPdfs.csv', 'w')
    for pdf in lista:
        pdfs.write(str(pdf)+'\n')

def escribir_archivo2(lista, directorio, nombre):
    pdfs = open('%s%s.csv'%(directorio, nombre), 'w')
    for pdf in lista:
        pdfs.write(str(pdf)+'\n')

def leer_archivo(archivo, eliminar_primero=False):
    '''Convierte un archivo a una lista, línea a línea

    Parámetros:
    Si eliminar_primero es True, entonces no se tiene en cuenta la primera línea del archivo

    '''
    lista = []
    if eliminar_primero:
        archivo.readline()
    for linea in archivo:
        lista.append(linea.rstrip())
    return lista

def obtener_autores(xmls, lista_papers):
    '''Obtiene un diccionario que tiene como llave los autores y almacena la lista de los eid en los que ha participado
    Parámetros
    xmls (lista de archivos): Son los xml de la búsqueda de scopus
    lista_paper (lista de cadenas): Los papers que van a participar de la red
    '''
    autores = {}
    documento = 1
    id = ''
    for xml in xmls:
        tree = ET.parse(xml)
        root = tree.getroot()
        #documento = documento - 4
        for child in root:
            id = ''
            for eid in child.findall('{http://www.w3.org/2005/Atom}eid'):
                id = eid.text
                print eid.text
            if id in lista_papers:
                documento += 1
                for authors in child.findall('{http://www.w3.org/2005/Atom}author'):
                    for child2 in authors.findall('{http://www.w3.org/2005/Atom}authname'):
                        print child2.tag, child2.text, documento
                        autor = child2.text.encode('utf-8')
                        if(autores.get(autor) == None):
                            autores[autor] = []
                        autores[autor].append(id)
        xml.seek(0)
    print autores
    print len(autores)
    return autores

def dicci_to_list(dicci):
    list = []
    for autor in dicci:
        list.append(dicci[autor])
    return list

def leer_corpus(corpus_archivo):
    data = []
    data_numeric = []
    target = []
    corpus = corpus_archivo
    tipo_datos = corpus.readline().rstrip().split(',')
    print tipo_datos
    corpus.readline()

    for linea in corpus:
        #Para quitar el salto de linea \n
        linea = linea.rstrip()
        instancia = linea.split(',')
        atributos_numericos = []
        atributos_nominales = []
        for tipo, atributo in zip(tipo_datos, instancia):
            if tipo == 'nom':
                atributos_nominales.append(atributo)
            elif tipo == 'num':
                atributos_numericos.append(atributo)
        data.append(atributos_nominales)
        data_numeric.append(atributos_numericos)
        #pop elimina de la lista el elemento en el índice indicado y lo retorna
        #target.append(instancia.pop(len(instancia)-1))
        target.append(instancia[len(instancia)-1])

    return data, target, data_numeric



def prueba_leer_corpus():
    corpus = open(DIRECTORIO_CVS+'corpusNum.csv')
    a, b, c = leer_corpus(corpus)
    print a
    print b
    print c
    corpus.close()


#prueba_leer_corpus()
#obtener_autores([open('XMLs/xml0.xml'),open('XMLs/xml1.xml'),open('XMLs/xml2.xml'),open('XMLs/xml3.xml')],
#                leer_archivo(open('CVSs/relevantes.csv'), eliminar_primero=False))
#prueba_net_to_json()