import requests
import time
from Modulos_Help import df_skus, a_quien_pedir, ingredient_time, plate_time, bandeja_time
from Modulos import used_link, key
import requests
import json
import hmac
import base64
from hashlib import sha1
from Modulos import used_link

dic_id_grupos = {"1": "627ed2d422ec6057a70459a2",
"2": "627ed2d422ec603bbe0459a3", "3": "627ed2d422ec6097af0459a4",
"4": "627ed2d422ec606d950459a5", "5": "627ed2d422ec60b9c10459a6",
"6": "627ed2d422ec60ecd50459a7", "7": "627ed2d422ec6078860459a8",
"8": "627ed2d422ec60f0f80459a9", "9": "627ed2d422ec6004730459aa",
"10": "627ed2d422ec60262c0459ab", "11": "627ed2d422ec6048aa0459ac",
"12": "627ed2d422ec60b6ec0459ad", "13": "627ed2d422ec603db30459ae",
"14": "627ed2d422ec6040e30459af", "15": "627ed2d422ec6003d20459b0",
"16": "627ed2d422ec60681d0459b1", "17": "627ed2d422ec60cdf00459b2",
"18": "627ed2d422ec60d0330459b3"}

def comprobar_idOC(oc_id):
    ## Obtenemos los almacenes desde la api, con el hash indicado
    url_almacenes = "{}/oc/obtener/{}".format(used_link, oc_id)
    response = requests.request("GET", url_almacenes)
    return response.status_code

def OC_return(oc_request, oc_id):
    respuesta = comprobar_idOC(oc_request, oc_id) ## comprobar es 0 si esta duplicado, 1 eoc
    if respuesta == 200:
        return 0
    ## Creamos el diccionario que enviaremos en el body de respuesta
    dictionary = {}
    dictionary["id"] = oc_id
    for key in oc_request.keys():
        dictionary[key] = oc_request[key]
    dictionary["estado"] = "recibida"
    return dictionary

def recepcionar_orden(order_id):
    url_order = "{}/oc/recepcionar/{}".format(used_link, order_id)
    data = {"id":order_id}
    data1 = json.dumps(data)
    loaded_data = json.loads(data1)
    response = requests.request("POST", url_order, data=loaded_data)
    if response.status_code == 200:
        json_fabricacion = response.json()
        return json_fabricacion
    else:
        print(response.status_code)
        json_fabricacion = {"Respuesta" : "Error en la solicitud."}
        return json_fabricacion

def rechazar(order_id):
    url_order = "{}/oc/rechazar/{}".format(used_link, order_id)
    data = {"id":order_id, "rechazo": "rechazada porque no cumple con el gap"}
    data1 = json.dumps(data)
    loaded_data = json.loads(data1)
    response = requests.request("POST", url_order, data=loaded_data)
    if response.status_code == 200:
        json_fabricacion = response.json()
        return json_fabricacion
    else:
        print(response.status_code)
        json_fabricacion = {"Respuesta" : "Error en la solicitud."}
        return json_fabricacion

# print(recepcionar_orden('62a510d8ffe0cc25e67ab31b'))
# print(comprobar_idOC('62a1201011703e499a6419d0'))

def OC_create(sku, quantity):

    url = "{}/oc/crear".format(used_link)
    lista_grupos = a_quien_pedir(sku, df_skus)

    print(lista_grupos)
    for grupo in lista_grupos: 
        id_grupo = dic_id_grupos[grupo]

        if int(sku) < 1000:
            min_time = ingredient_time(sku, df_skus)
        elif int(sku) <= 10000:
            min_time = plate_time(sku, df_skus)
        else: 
            min_time = bandeja_time(sku, df_skus)

        actual_time = int(round(time.time() * 1000))

        data_loaded = {
        "cliente": "627ed2d422ec60f0f80459a9",
        "proveedor": id_grupo,
        "sku": str(sku),
        "fechaEntrega": actual_time + min_time,
        "cantidad": str(quantity),
        "precioUnitario": "100",
        "canal": "b2b",
        "notas": "Gracias",
        "urlNotificacion": "brocoli8.ing.puc.cl/ordenes-compra/id_orden"
        }

        data_loaded = json.dumps(data_loaded)
        data_loaded = json.loads(data_loaded)
        print(data_loaded.json())

        #response = requests.request("PUT", url, data=data_loaded)
        #print(response)

def enviar_oc(id_order, producto_id):
    url_fabrica = "{}/bodega/stock".format(used_link)
    string = ('DELETE{}{}{}{}'.format(producto_id, "buzon", 1, id_order)).encode()
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    data = {"productoId":str(producto_id),"oc":str(id_order), "direccion":"buzon", "precio":1}
    data1 = json.dumps(data)
    loaded_data = json.loads(data1)
    response = requests.request("DELETE", url_fabrica, headers={'Authorization': 'INTEGRACION grupo8:'+hs}, data=loaded_data)
    if response.status_code == 200:
        json_fabricacion = response.json()
        return json_fabricacion
    else:
        print(response.status_code)
        json_fabricacion = {"Respuesta" : "Error en la solicitud."}
        return json_fabricacion


