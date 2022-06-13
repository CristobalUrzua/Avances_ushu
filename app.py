from flask import Flask, jsonify, make_response, request, render_template
import json
import pandas as pd
from Modulos import obtener_info_almacenes, obtener_skus_con_stock
from Modulos_Help import df_orders
from Modulos_OC import OC_return

app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey123"
key_development =b"jLxHi.a:JyUHPQI"
key_production = b"LYT#Vk05V2;.4eY"
key = key_development
id_pulmon_develop = '627ed48d22ec60541f0459fe'
id_recepcion_develop = '627ed48d22ec60184c0459fb'
id_cocina_develop = '627ed48d22ec6047590459ff'
id_despacho_develop = '627ed48d22ec603c5f0459fc'

@app.route("/") 
def home():
    json_almacenes = obtener_info_almacenes()
    pulmon_stock = []
    recepcion_stock =[]
    cocina_stock =[]
    despacho_stock =[]
    ## Recorremos los almacenes y agregamos al stock total, los skus con stock y su cantidad
    for almacen in json_almacenes:
        if almacen["_id"] == id_pulmon_develop:
            stock = obtener_skus_con_stock(almacen["_id"])
            for item in stock: 
                pulmon_stock.append(item)

        elif almacen["_id"] == id_recepcion_develop:
            stock = obtener_skus_con_stock(almacen["_id"])
            for item in stock: 
                recepcion_stock.append(item)

        elif almacen["_id"] == id_cocina_develop:
            stock = obtener_skus_con_stock(almacen["_id"])
            for item in stock: 
                cocina_stock.append(item)

        elif almacen["_id"] == id_despacho_develop:
            stock = obtener_skus_con_stock(almacen["_id"])
            for item in stock: 
                despacho_stock.append(item)


    return render_template("stock.html", pulmon_stock=pulmon_stock, recepcion_stock=recepcion_stock ,cocina_stock=cocina_stock, despacho_stock=despacho_stock)

@app.route("/orders") 
def orders():
    df_orders.to_csv("Produccion/order_tracker.csv", index=False)
    print(df_orders)
    return render_template("orders.html", df_orders=df_orders)


@app.route("/stocks") 
def stocks():
    ## Obtenemos los almacenes
    json_almacenes = obtener_info_almacenes()
    full_stock =[]
    ## Recorremos los almacenes y agregamos al stock total, los skus con stock y su cantidad
    for almacen in json_almacenes:
        stock = obtener_skus_con_stock(almacen["_id"])
        for item in stock: 
            full_stock.append(item)
        
    ## Creamos la response, que corresponde a los stocks por sku
    ## total_stock = total_stocks(full_stock)
    body_json = json.dumps(full_stock)
    response = make_response(body_json, 200)
    response.headers["Content-Type"] = "application/json"
    return response 

@app.route("/updatedata") 
def updatedata():  
    update_data()
    return make_response(jsonify({"mensaje": "Datos update"}), 200)

@app.route("/ordenes-compra/<id_>", methods=["POST"])
def order_received(id_):
    content_type = request.headers.get('Content-Type')
    ## Obtenemos el body del request
    if (content_type == 'application/json'):
        json_request = request.json ## Recibimos los datos del request de la orden
        response_body = OC_return(json_request, id_) ## Creamos el body que retornaremos
        if response_body == 0: ## OC Duplicada
            return make_response(jsonify({"mensaje": "Orden ya fue recibida"}), 400)
        else: ## OC ok, retornamos el body
            return make_response(jsonify(response_body), 201)

@app.route("/ordenes-compra/<id_>", methods=["PATCH"])
def our_order_status(id_):
    print(id_)
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json_request = request.json ## Recibimos la actualización de una orden (Aceptada o Rechazada)
    string = "Order " + str(id_) + " Update Received" 
    return make_response(jsonify({'Message': string}), 204)

if __name__ == "__main__":
    app.run()