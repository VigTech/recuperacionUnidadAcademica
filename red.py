# -*- coding: utf-8 -*-
import igraph
from manejadorArchivos import leer_archivo, obtener_autores

class Red:
    '''La clase representa una red que se construye a partir de listas.
    '''
    def __init__(self, conjuntos, nombre, etiquetas_nodos = None):
        self.grafo, self.nombre_punto_net = self.construir_red_autocorrelacion(conjuntos, nombre, self.contar_coincidencias, etiquetas_nodos)


    def construir_red_autocorrelacion(self, conjuntos, nombre, contar_coinc, etiquetas_nodos):
        '''Construye la red de autocorrelación de un conjunto de conjuntos

        Parámetros
        Conjuntos es una lista de listas'''
        print(len(conjuntos))
        cantidad_nodos = len(conjuntos)
        red = open(nombre+".net", 'w')
        red.write("*Vertices "+str(cantidad_nodos)+"\n")

        if etiquetas_nodos!=None:
            for i,etiqueta in enumerate(etiquetas_nodos):
                red.write(str(i+1)+' "'+str(etiqueta)+'"\n')

        red.write("*Edges\n")
        for i in range(cantidad_nodos-1):
            #print i
            for j in range(i+1, cantidad_nodos):
                #print(i,j)
                coinc = contar_coinc(conjuntos[i],conjuntos[j])
                if(coinc > 0):
                    #print(i,j,"  ",coinc)
                    red.write(str(i+1)+" "+str(j+1)+" "+str(coinc)+"\n")
        red.close()
        print 'acabó la red'
        return igraph.read(nombre+".net",format="pajek"), red.name
    def contar_coincidencias(self, conjunto_1, conjunto_2):
        coincidencias = 0
        for elemento_en_1 in conjunto_1:
            if elemento_en_1 in conjunto_2:
                    coincidencias+=1
        return coincidencias
    def average_degree(self):
	    return sum(self.grafo.degree())/float(len(self.grafo.degree()))

    def average_strength(self):
        return sum(self.grafo.strength(weights=self.grafo.es['weight']))/float(len(self.grafo.strength(weights=self.grafo.es['weight'])))

    def weights(self):
        return sum(self.grafo.strength(weights=self.grafo.es['weight']))
    def clustering_coefficient(self):
        return self.grafo.transitivity_undirected()

    def average_path_lenght(self):
        return self.grafo.average_path_length()

    def generar_json(self):
        '''Construye el json que se usa como entrada de D3, a partir de una red .net'''
        punto_net = open(self.nombre_punto_net)
        json = open('json', 'w')
        nodos = []
        aristas = []
        sample_data = ''
        connections = ''

        #Se lee la primera línea, se divide el string por espacios y se obtiene la segunda posición
        cant_vertices = int(punto_net.readline().split(' ')[1])
        #Aquí se van a almacenar los tamaños de los nodos en función de sus aristas.
        tamanos = [0]*cant_vertices
        for i in range(cant_vertices):
            autor = punto_net.readline().rstrip().split(' "')
            id = autor[0]
            name = autor[1]
            nodos.append('{"name": "'+name+', "size": tamanio, "id": '+id+'},')
        #Para saltarse la línea que dice "edges" en el .net
        punto_net.readline()
        for arista in punto_net:
            arista = arista.rstrip().split(' ')
            origen = arista[0]
            destino = arista[1]
            peso = arista[2]
            tamanos[int(origen)-1] += int(peso)
            tamanos[int(destino)-1] += int(peso)
            aristas.append('{"source": '+origen+', "target": '+destino+', "strength": '+peso+'},')
        #Volver al inicio del .net
        punto_net.seek(0)
        #Saltarse la línea que especifica la cantidad de vértices
        punto_net.readline()
        for i in range(cant_vertices):
            nodos[i] = nodos[i].replace('tamanio', str(tamanos[i]))
        punto_net.seek(0)

        print tamanos
        print sum_lista_strings(nodos)
        print sum_lista_strings(aristas)

def sum_lista_strings(lista):
    string_completa= ''
    for elemento in lista:
        string_completa += elemento
    return string_completa


def xmls_to_red(xmls, nombre):
    '''Gernera un objeto Red, a partir de una lista de xml
    '''
    diccionario_autores = obtener_autores(xmls, leer_archivo(open('CVSs/relevantes.csv'), eliminar_primero=False))
    lista_autores = []
    lista_nombres = []
    for autor in diccionario_autores:
        lista_autores.append(diccionario_autores[autor])
        lista_nombres.append(autor)
    return Red(lista_autores, nombre, lista_nombres)
def main():
    # nodos = 15
    # conjuntos = []
    # for i in range(15):
    #     conjuntos.append(leer_archivo(open('redes/s/s'+str(i+1)+'.csv', 'r')))
    # print conjuntos
    # r = Red(conjuntos, 's')

    #diccionario_autores = obtener_autores([open('XMLs/xml0.xml'),open('XMLs/xml1.xml'),open('XMLs/xml2.xml'),open('XMLs/xml3.xml')])
    # lista_autores = []
    # lista_nombres = []
    # for autor in diccionario_autores:
    #     lista_autores.append(diccionario_autores[autor])
    #     lista_nombres.append(autor)lista_autores = []
    # lista_nombres = []
    xmls_to_red([open('XMLs/xml0.xml'),open('XMLs/xml1.xml'),open('XMLs/xml2.xml'),open('XMLs/xml3.xml')], 'chapotero').generar_json()
    #r=Red(lista_autores, 'autores3', lista_nombres)
    #r.grafo.write_svg('autores4.svg')
    #layout = r.grafo.layout("kk")
    #igraph.plot(r.grafo,'autoresCircle.pdf', layout=layout, )

    # visual_style = {}
    # visual_style["vertex_size"] = 1
    # #visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
    # #visual_style["vertex_label"] = g.vs["name"]
    # visual_style["edge_width"] = 0.1
    # visual_style["layout"] = layout
    # visual_style["bbox"] = (300, 300)
    # visual_style["margin"] = 20
    # igraph.plot(r.grafo,'autoresNUEVoo.pdf', **visual_style)

#main()
