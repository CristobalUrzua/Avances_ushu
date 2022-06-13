import json
from hashlib import sha1
import datetime as dt
from datetime import datetime
from Modulos import obtener_info_almacenes, obtener_sku_en_almacen, obtener_skus_con_stock, elaborar_en_fabrica, mover_entre_almacenes, id_cocina_develop, id_despacho_develop
import pandas as pd
from datetime import datetime, timezone
from metomi.isodatetime.parsers import TimePointParser
import requests

################# Al recibir una orden:
# {
# "cliente": string
# "sku": number,
# "fechaEntrega": Date,
# "cantidad": number,
# "urlNotificacion": string
# }

df_receipts = pd.read_csv("Produccion/receipts.csv")
df_skus = pd.read_csv("Produccion/skus.csv")

df_orders = pd.read_csv("Produccion/order_tracker.csv")
# df_orders = df_orders.append({"OrderID":"d123d", "Status":False, "Tipo_Producto":"Ingredient", "SKU_Producto":10, "IDProductoAsignado":"a123a", "Vencimiento_Order":"12-04-2023"}, ignore_index=True)
# df_orders.to_csv("Produccion/order_tracker.csv", index=False)
# df_orders2 = pd.read_csv("Produccion/order_tracker.csv")
# print(df_orders2)

def a_quien_pedir(sku, df_skus):
    sku_row = df_skus[df_skus["SKU"] == sku]
    productors = sku_row['Grupos Productores'].values[0]
    if str(8) in productors or productors == "todos":
        return 1
    else:
        return 1
        #return productors.split(", ")

# print(a_quien_pedir(56, df_skus))

def needed_in_order(sku, cantidad, df_receipts, df_skus):
    needed = {}
    ### Si piden solo un ingrediente
    if sku < 1000:
        needed["Ingredients"] = {sku: cantidad}
    
    ### Si piden un plato
    elif sku >= 1000 and sku < 10000:
        row_value = df_receipts[df_receipts["SKU Producto"] == sku]
        needed["Platos"] = {sku: cantidad}
        if a_quien_pedir(sku, df_skus) == 1: 
            ingr = {}
            for valores in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist():
                if valores[0] in ingr.keys():
                    ingr[valores[0]] += valores[1]
                else:
                    ingr[valores[0]] = valores[1]
            needed["Ingredients"] = ingr

    ### Si piden una bandeja
    elif sku >= 10000 and sku < 100000:
        row_value = df_receipts[df_receipts["SKU Producto"] == sku]
        needed["Bandeja"] = {sku: cantidad}
        ##needed["Platos"] = row_value[["SKU Ingrediente", "Cantidad"]].values.tolist()
        plates = {}
        for valores_ in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist(): ## recorre cada plato que hay que usar para la bandeja
            if valores_[0] in plates.keys():
                plates[valores_[0]] += valores_[1]
            else:
                plates[valores_[0]] = valores_[1]
        needed["Platos"] = plates
        ingr = {}
        for sku_ in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist():
            if a_quien_pedir(sku_[0], df_skus) == 1:
                row_value_ = df_receipts[df_receipts["SKU Producto"] == sku_[0]]
                for valores in row_value_[["SKU Ingrediente", "Cantidad"]].values.tolist(): ## recorre los ingredientes para cada plato
                    if valores[0] in ingr.keys():
                        # ingr[valores[0]] += valores[1]
                        pass
                    else:
                        ingr[valores[0]] = valores[1]
        needed["Ingredients"] = ingr

    contador = 0
    if len(needed.keys()) > 1 and cantidad > 1:
        for needed_key in needed.keys():
            if contador > 0:
                for specific_key in needed[needed_key].keys():
                    needed[needed_key][specific_key] = needed[needed_key][specific_key] * cantidad
            contador += 1

    return needed

# print(needed_in_order(1000, 2, df_receipts, df_skus))

def ingredient_time(sku, df_skus):
    ingredient_row = df_skus[df_skus["SKU"] == sku]
    ingredient_time = ingredient_row['Tiempo esperado producción (mins)'].values[0]
    if a_quien_pedir(sku, df_skus) != 1:
        ingredient_time += 10 ## tiempo extra considerado si tenemos que pedirle el ingrediente a otro grupo
    return ingredient_time

# print(ingredient_time(20, df_skus))

def plate_time(sku, df_receipts, df_skus):
    plate_row = df_skus[df_skus["SKU"] == sku]
    plate_time = plate_row['Tiempo esperado producción (mins)'].values[0]
    row_value = df_receipts[df_receipts["SKU Producto"] == sku]
    max_tiempo_ingredientes = 0
    for valor in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist():
        if ingredient_time(valor[0], df_skus) > max_tiempo_ingredientes:
            max_tiempo_ingredientes = ingredient_time(valor[0], df_skus)
    if a_quien_pedir(sku, df_skus) != 1:
        plate_time += 10
    plate_time += max_tiempo_ingredientes
    return plate_time

# print(plate_time(2000, df_receipts, df_skus))

def bandeja_time(sku, df_skus):
    bandeja_row = df_skus[df_skus["SKU"] == sku]
    bandeja_time = bandeja_row['Tiempo esperado producción (mins)'].values[0]
    if a_quien_pedir(sku, df_skus) != 1:
        bandeja_time += 10 ## tiempo extra considerado si tenemos que pedirle el ingrediente a otro grupo
    return bandeja_time

# print(ingredient_time(20, df_skus))

def min_lote(value1, value2):
    actual_lote = value2
    while True:
        if actual_lote >= value1:
            break
        else:
            actual_lote += value2
    diference = actual_lote - value1
    return ((actual_lote, diference)) 

def check_lotes_platos(needed_dict, df_receipts, df_skus):
    if "Platos" in needed_dict.keys():
        for plato_key in needed_dict["Platos"].keys():
            if a_quien_pedir(plato_key, df_skus) != 1:
                pass
            else:
                sku_row = df_skus[df_skus["SKU"] == plato_key]
                lote_sku = sku_row['Lote producción'].values[0]
                ingredients_ = df_receipts[df_receipts["SKU Producto"] == plato_key]
                values_changes = min_lote(needed_dict["Platos"][plato_key], lote_sku)
                needed_dict["Platos"][plato_key] = values_changes[0]

                # for ingredient in ingredients_[["SKU Ingrediente", "Cantidad"]].values.tolist():
                #     needed_dict["Ingredients"][ingredient[0]] += (ingredient[1] * values_changes[1])

    return needed_dict

# def check_lotes_ingredientes(needed_dict, df_receipts, df_skus):
#     if "Ingredients" in needed_dict.keys():
#         for ingredient_key in needed_dict["Ingredients"].keys():
#             if a_quien_pedir(ingredient_key, df_skus) != 1:
#                 pass
#             else:
#                 sku_row = df_skus[df_skus["SKU"] == ingredient_key]
#                 lote_sku = sku_row['Lote producción'].values[0]
#                 values_changes = min_lote(needed_dict["Ingredients"][ingredient_key], lote_sku)
#                 needed_dict["Ingredients"][ingredient_key] = values_changes[0]
#     return needed_dict

def check_lotes_ingredientes(needed_dict, df_receipts, df_skus):
    for ingredient_key in needed_dict["Ingredients"].keys():
            needed_dict["Ingredients"][ingredient_key] = 0
    
    if "Platos" in needed_dict.keys() and "Ingredients" in needed_dict.keys():
         for ingredient_key in needed_dict["Ingredients"].keys():
            needed_dict["Ingredients"][ingredient_key] = 0
        
         ingredientes = {}
         for plato in needed_dict["Platos"].keys():
            sku_row = df_skus[df_skus["SKU"] == plato]
            lote_sku = sku_row['Lote producción'].values[0]
            ingredients_ = df_receipts[df_receipts["SKU Producto"] == plato]
            cantidad_lotes = int(needed_dict["Platos"][plato] / lote_sku)
            skus = list(ingredients_["SKU Ingrediente"])
            cantidades = list(ingredients_["Cantidad"]) * cantidad_lotes

            for x in range(len(skus)):
                if skus[x] in ingredientes.keys():
                    ingredientes[skus[x]] += cantidades[x]
                else: 
                    ingredientes[skus[x]] = cantidades[x]

         for ingredient_key in needed_dict["Ingredients"].keys():
            sku_row = df_skus[df_skus["SKU"] == ingredient_key]
            lote_sku = sku_row['Lote producción'].values[0]
            values_changes = min_lote(ingredientes[ingredient_key], lote_sku)
            needed_dict["Ingredients"][ingredient_key] = values_changes[0]

    return needed_dict

# basic_needed = needed_in_order(10000, 3, df_receipts, df_skus)
# print(basic_needed)
# values_a_pedir_ = check_lotes_platos(basic_needed, df_receipts, df_skus)
# print(values_a_pedir_)
# values_a_pedir = check_lotes_ingredientes(values_a_pedir_, df_receipts, df_skus)
# print(values_a_pedir)

def order_response(sku, fecha_entrega, cantidad, df_receipts, df_skus):
    basic_needed = needed_in_order(sku, cantidad, df_receipts, df_skus)
    values_a_pedir_ = check_lotes_platos(basic_needed, df_receipts, df_skus)
    values_a_pedir = check_lotes_ingredientes(values_a_pedir_, df_receipts, df_skus)
    max_capacity_usage = 0
    for product_type_dict in values_a_pedir.keys():
        if product_type_dict != "Bandeja":
            for product in values_a_pedir[product_type_dict].keys():
                max_capacity_usage += values_a_pedir[product_type_dict][product]

    tiempo_total = 0 
    if "Platos" in values_a_pedir.keys():
        max_plato = 0
        for plato in values_a_pedir["Platos"].keys():
            time_plato = plate_time(plato, df_receipts, df_skus)
            if time_plato > max_plato:
                max_plato = time_plato
        if "Bandeja" in values_a_pedir.keys():
            max_plato += bandeja_time(list(values_a_pedir["Bandeja"].keys())[0], df_skus)

        tiempo_total += max_plato
    elif "Ingredients" in values_a_pedir.keys() and len(values_a_pedir.keys()) == 1:
        tiempo_total = ingredient_time(list(values_a_pedir["Ingredients"].keys())[0], df_skus)

    ## Si tiempo_actual + tiempo_total < fecha_entrega and capacidad recepcion > max_capacity_usage --> Aceptar Orden, else Rechazar Orden.
    return tiempo_total
    # return max_capacity_usage

# print(order_response(10000, True, 1, df_receipts, df_skus))

def check_ingredients_in_stock(sku, id_recepcion, id_pulmon):
    ## Recibe sku, id_recepcion, id_pulmon y retorna el id de un producto de sku=sku que no ha vencido
    lista_ids = [id_recepcion, id_pulmon]
    # Primero Checkeamos en recepcion y luego pulmon
    for id_almacen in lista_ids:
        respuesta = obtener_sku_en_almacen(id_almacen, sku)
        for elemento in respuesta:
            # Guardamos el id del sku
            _id = elemento['_id']
            # Guardamos su fecha de vencimiento
            vencimiento = elemento['vencimiento']
            # Sacamos tiempo actual en UTC
            time_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            # Utilizamos Parser
            date1 = TimePointParser().parse(vencimiento)
            date2 = TimePointParser().parse(time_now)

            datediff = date1 - date2
            datediff_hours = datediff.hours
            datediff_minutes = datediff.minutes
            minutes_to_hours = datediff_minutes/60

            total_datediff = round(datediff_hours + minutes_to_hours, 1)
            print(total_datediff)
            if total_datediff > 1.3:
                return _id
    return "0"

def check_platos_in_stock(sku, id_cocina):
    ## Recibe sku, id_recepcion, id_pulmon y retorna el id de un producto de sku=sku que no ha vencido
    lista_ids = [id_cocina]
    # Primero Checkeamos en recepcion y luego pulmon
    for id_almacen in lista_ids:
        respuesta = obtener_sku_en_almacen(id_almacen, sku)
        for elemento in respuesta:
            # Guardamos el id del sku
            _id = elemento['_id']
            return _id
    while True:
        return "0"

def check_despachos_skus(sku, id_despacho, df_orders):
    
    respuesta = obtener_sku_en_almacen(id_despacho, sku)
    for elemento in respuesta:
        # Guardamos el id del sku
        _id = elemento['_id']
        if len(df_orders[df_orders["IDProductoAsignado"] == _id]) != 1:
            return _id
            

    return 0
# print(check_ingredients_in_stock(105, '627ed48d22ec60184c0459fb', '627ed48d22ec60541f0459fe'))
# print(check_platos_in_stock(12000, id_despacho_develop))
