#!flask/bin/python
from flask import Flask, jsonify, request
from clasificadorUnidadesAcademicas import  ClasificadorUnidadesAcademicas

app = Flask(__name__)



@app.route('/clasificacionUnidadAcademica/', methods=['GET'])
def get_clasificacion():
    if request.method =='GET':
        json = request.args.get('datosJson')
        c = ClasificadorUnidadesAcademicas('eisc')
        print c
        json = c.procesar_json_entrada(json)
        #c.clasificar_docs()
        return jsonify({'clasificacion':c.clasificar_docs()})
        #return jsonify(json)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
