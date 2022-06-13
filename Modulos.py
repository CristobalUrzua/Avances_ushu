import requests
import json
import hmac
import base64
from hashlib import sha1
import datetime as dt
from datetime import datetime

key_develop =b"jLxHi.a:JyUHPQI"
key_production = b"LYT#Vk05V2;.4eY"
link_development = "https://dev.api-bodega.2022-1.tallerdeintegracion.cl"
link_production = "https://prod.api-bodega.2022-1.tallerdeintegracion.cl"
id_recepcion_develop = '627ed48d22ec60184c0459fb'
id_pulmon_develop = '627ed48d22ec60541f0459fe'
id_cocina_develop = '627ed48d22ec6047590459ff'
id_despacho_develop = '627ed48d22ec603c5f0459fc'

#########################################
key = key_develop
used_recepcion = id_recepcion_develop
used_cocina = id_cocina_develop
used_despacho = id_despacho_develop
used_pulmon = id_pulmon_develop
used_link = link_development 
#########################################

def obtener_info_almacenes():
    ## Obtenemos los almacenes desde la api, con el hash indicado
    url_almacenes = "{}/bodega/almacenes".format(used_link)
    string = b"GET"
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    response = requests.request("GET", url_almacenes, headers={'Authorization': 'INTEGRACION grupo8:'+hs})
    json_almacenes = response.json()

    return json_almacenes

def obtener_skus_con_stock(almacenid):
    ## Obtenemos los skus con stocks para el almacen de almacenID
    url_almacenes = "{}/bodega/skusWithStock?almacenId={}".format(used_link, almacenid)
    string = ('GET{}'.format(almacenid)).encode()
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    response = requests.request("GET", url_almacenes, headers={'Authorization': 'INTEGRACION grupo8:'+hs})
    stock = response.json()
    for element in stock:
            element['sku'] = element.pop("_id")
    return stock

def obtener_sku_en_almacen(almacenid, sku):
    ## Obtenemos los productos de sku=sku en almacen de almacenID, retorna ID para cada producto.
    url_almacenes = "{}/bodega/stock?almacenId={}&sku={}".format(used_link, almacenid, sku)
    string = ('GET{}{}'.format(almacenid, sku)).encode()
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    response = requests.request("GET", url_almacenes, headers={'Authorization': 'INTEGRACION grupo8:'+hs})
    json_productos = response.json()

    return json_productos

def elaborar_en_fabrica(sku, cantidad):
    ## Le pedimos una cantidad de tal sku a la fabrica, cantidad debe ser multiplo del lote para el sku.
    url_fabrica = "{}/bodega/fabrica/fabricarSinPago".format(used_link)
    string = ('PUT{}{}'.format(sku, (cantidad))).encode()
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    data_ = {"sku":str(sku), "cantidad":cantidad}
    data = json.dumps(data_)
    loaded_data = json.loads(data)
    response = requests.request("PUT", url_fabrica, headers={'Authorization': 'INTEGRACION grupo8:'+hs}, data=loaded_data)
    if response.status_code == 200:
        #se manda a fabricar
        json_fabricacion = response.json()
        return json_fabricacion
    else:
        json_fabricacion = {"Respuesta" : "Error en la solicitud."}
        return json_fabricacion

def mover_entre_almacenes(producto_id, almacen_id):
    # movemos el productoID al almacenID, si vamos a mover a Pulmon, productoID debe estar en recepcion
    url_fabrica = "{}/bodega/moveStock".format(used_link)
    string = ('POST{}{}'.format(producto_id, almacen_id)).encode()
    hashed = hmac.new(key, string, sha1).digest()
    hs = base64.b64encode(hashed).decode()
    data = {"productoId":str(producto_id), "almacenId":str(almacen_id)}
    data1 = json.dumps(data)
    loaded_data = json.loads(data1)
    print(data)
    response = requests.request("POST", url_fabrica, headers={'Authorization': 'INTEGRACION grupo8:'+hs}, data=loaded_data)
    if response.status_code == 200:
        json_fabricacion = response.json()
        return json_fabricacion
    else:
        print(response.status_code)
        json_fabricacion = {"Respuesta" : "Error en la solicitud."}
        return json_fabricacion


#print(obtener_info_almacenes())
## print(disponibilidad_de_productos(bandeja_cielo_azul))
# print(obtener_skus_con_stock(id_recepcion_develop)) 
# print(obtener_sku_en_almacen(id_cocina_develop, 50))

## Cosas para bandeja cielo azul
#print(elaborar_en_fabrica(5100, 3)) #
# print(elaborar_en_fabrica(101, 3)) #
# print(elaborar_en_fabrica(20, 10)) #
# print(elaborar_en_fabrica(15, 3)) #
# print(elaborar_en_fabrica(1, 20)) #
# print(elaborar_en_fabrica(80, 6)) #
# print(elaborar_en_fabrica(70, 5)) #
# print(elaborar_en_fabrica(50, 2)) #
# print(elaborar_en_fabrica(60, 4)) #
# print(elaborar_en_fabrica(90, 8)) #
# print(elaborar_en_fabrica(10, 15)) #S
# print(elaborar_en_fabrica(40, 5)) #

# print(obtener_sku_en_almacen(id_recepcion_develop, 1))
# print(obtener_info_almacenes())
# print("**********************************************************************************************")
# print(mover_entre_almacenes('62a5037cffe0cc2d727aaf7f', id_despacho_develop))
# print("**********************************************************************************************")
# print(obtener_info_almacenes())
# print("**********************************************************************************************")
# print(mover_entre_almacenes('62a5037cffe0cc2d727aaf7f', id_pulmon_develop))
# print("**********************************************************************************************")
# print(obtener_info_almacenes())
# print("**********************************************************************************************")
# print(mover_entre_almacenes('62a53a90e27591f205d4ebc2', id_cocina_develop))
# print(mover_entre_almacenes('62a53a90e275913994d4ebc0', id_cocina_develop))
# print("**********************************************************************************************")
# print(obtener_info_almacenes())

# print(mover_entre_almacenes('62a39e10596fb3df145a0a71', id_cocina_develop))
# print(mover_entre_almacenes('62a39e10596fb3d96c5a0a72', id_cocina_develop))
# print(mover_entre_almacenes('62a39e10596fb32e9f5a0a73', id_cocina_develop))
# print(mover_entre_almacenes('62a39e10596fb36b4e5a0a74', id_cocina_develop))
# print(elaborar_en_fabrica(3000, 2))
# print(obtener_skus_con_stock(id_recepcion_develop))

# print(obtener_info_almacenes())

## '629fe1d021cdd918ac1427c5'
## '629fe1d021cdd9b1741427c6'

# print(obtener_info_almacenes())
# print(mover_entre_almacenes('629fe1d021cdd9b1741427c6', id_cocina_develop))
# print(mover_entre_almacenes('629fe1d021cdd92a121427c8', id_pulmon_develop))
# # print(mover_entre_almacenes('629fe1d021cdd9b1741427c6', id_pulmon_develop))
# print(obtener_info_almacenes())