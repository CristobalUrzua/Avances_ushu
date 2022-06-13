from turtle import pd
from Modulos_Help import needed_in_order, check_lotes_platos, check_lotes_ingredientes, df_orders, df_skus, df_receipts, a_quien_pedir, check_ingredients_in_stock, check_platos_in_stock
from Modulos import elaborar_en_fabrica, used_recepcion, used_pulmon, mover_entre_almacenes, used_cocina, used_despacho
import pandas as pd
from Modulos_OC import enviar_oc

# ****************************************************************************************************************** #
# ****************************************************************************************************************** #
def add_bandeja(sku, cantidad, order_id, fecha_vencimiento, df_orders):
    try:
        contador = max(df_orders["Prioridad"]) + 1
    except:
        contador=0
    basic_needed = needed_in_order(sku, cantidad, df_receipts, df_skus)
    plates_filter = check_lotes_platos(basic_needed, df_receipts, df_skus)
    final_needed = check_lotes_ingredientes(plates_filter, df_receipts, df_skus)
    ## cant_bandejas = final_needed["Bandeja"][list(final_needed["Bandeja"].keys())[0]]
    for n_bandeja in range(cantidad):
        bandeja = [order_id, "Esperando", "Bandeja", sku, "None", fecha_vencimiento, "Si", 0]
        df_orders = df_orders.append({"OrderID":bandeja[0], "Status":bandeja[1], "Tipo_Producto":bandeja[2], "SKU_Producto":bandeja[3], "IDProductoAsignado":bandeja[4], 
        "Vencimiento_Order":bandeja[5], "Prioridad": contador, "Sub_Producto_De": bandeja[7]}, ignore_index=True)
        skus_a_pedir = []
        for plato in final_needed["Platos"].keys(): 
            if a_quien_pedir(plato, df_skus) == 1:
                plato_add = [order_id, "Esperando", "Plato", plato, "None", fecha_vencimiento, "Si", sku]
                df_orders = df_orders.append({"OrderID":plato_add[0], "Status":plato_add[1], "Tipo_Producto":plato_add[2], "SKU_Producto":plato_add[3], "IDProductoAsignado":plato_add[4], 
                "Vencimiento_Order":plato_add[5], "Prioridad": contador, "Sub_Producto_De": plato_add[7]}, ignore_index=True)
                row_value = df_receipts[df_receipts["SKU Producto"] == plato]
                for valores in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist():
                    for repeat in range(valores[1]):
                        ingredient_add = [order_id, "Pidiendo", "Ingrediente", valores[0], "None", fecha_vencimiento, "Si", int(plato)]
                        df_orders = df_orders.append({"OrderID":ingredient_add[0], "Status":ingredient_add[1], "Tipo_Producto":ingredient_add[2], "SKU_Producto":ingredient_add[3], "IDProductoAsignado":ingredient_add[4], 
                         "Vencimiento_Order":ingredient_add[5], "Prioridad": contador, "Sub_Producto_De": ingredient_add[7]}, ignore_index=True)
                    skus_a_pedir.append(("Ingredients",valores[0]))
            else:
                plato_add = [order_id, "Pidiendo", "Plato", plato, "None", fecha_vencimiento, "Si", sku]
                df_orders = df_orders.append({"OrderID":plato_add[0], "Status":plato_add[1], "Tipo_Producto":plato_add[2], "SKU_Producto":plato_add[3], "IDProductoAsignado":plato_add[4], 
                "Vencimiento_Order":plato_add[5], "Prioridad": contador, "Sub_Producto_De": plato_add[7]}, ignore_index=True)
                skus_a_pedir.append(("Platos", plato))

    for a_pedir in skus_a_pedir:
        if a_quien_pedir(a_pedir[1], df_skus) == 1 and a_pedir[0] == "Ingredients":
            orden_a_fabrica = elaborar_en_fabrica(a_pedir[1], int(final_needed[a_pedir[0]][a_pedir[1]]))
            print("############## PIDIENDO #############")
            print(final_needed[a_pedir[0]][a_pedir[1]], "---", a_pedir[0], "----", a_pedir[1])
            # print(orden_a_fabrica)
        
        elif a_quien_pedir(a_pedir[1], df_skus) != 1:
            # orden_a_otro_grupo = pedir_otro_grupo(a_pedir[1], int(final_needed[a_pedir[0]][a_pedir[1]]))
            print("############## PIDIENDO NONONOO #############")
            print(final_needed[a_pedir[0]][a_pedir[1]], "---", a_pedir[0], "----", a_pedir[1])
            #print(orden_a_fabrica)

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)
    return df_orders
# ****************************************************************************************************************** #
# ****************************************************************************************************************** #
def add_plato(sku, cantidad, order_id, fecha_vencimiento, df_orders):
    try:
        contador = max(df_orders["Prioridad"]) + 1
    except:
        contador=0
    basic_needed = needed_in_order(sku, cantidad, df_receipts, df_skus)
    plates_filter = check_lotes_platos(basic_needed, df_receipts, df_skus)
    final_needed = check_lotes_ingredientes(plates_filter, df_receipts, df_skus)
    for n_platos in range(cantidad):
        if a_quien_pedir(sku, df_skus) == 1:
            plato_add = [order_id, "Esperando", "Plato", sku, "None", fecha_vencimiento, "Si", 0]
            df_orders = df_orders.append({"OrderID":plato_add[0], "Status":plato_add[1], "Tipo_Producto":plato_add[2], "SKU_Producto":plato_add[3], "IDProductoAsignado":plato_add[4], 
            "Vencimiento_Order":plato_add[5], "Prioridad": contador, "Sub_Producto_De": plato_add[7]}, ignore_index=True)
            row_value = df_receipts[df_receipts["SKU Producto"] == sku]
            #print(row_value)
            for valores in row_value[["SKU Ingrediente", "Cantidad"]].values.tolist():
                for repeat in range(valores[1]):
                    ingredient_add = [order_id, "Pidiendo", "Ingrediente", valores[0], "None", fecha_vencimiento, "Si", sku]
                    df_orders = df_orders.append({"OrderID":ingredient_add[0], "Status":ingredient_add[1], "Tipo_Producto":ingredient_add[2], "SKU_Producto":ingredient_add[3], "IDProductoAsignado":ingredient_add[4], 
                        "Vencimiento_Order":ingredient_add[5], "Prioridad": contador, "Sub_Producto_De": ingredient_add[7]}, ignore_index=True)
        
        else:
            ###########################################################################################
            # rechazar_orden -> Anular la orden de id order_id y retornar que nuestro grupo no hace este plato
            ###########################################################################################
            break

    
    ## Hacer el pedido de Ingredientes según final_needed
    for ingredient in final_needed["Ingredients"].keys():
        if a_quien_pedir(ingredient, df_skus) == 1:
            print("############## PIDIENDO #############")
            print(int(final_needed["Ingredients"][ingredient]), "--- Ingredient ---", ingredient)
            print(f"Mandando a fabricar sku {sku}")
            orden_a_fabrica = elaborar_en_fabrica(ingredient, int(final_needed["Ingredients"][ingredient]))
            # print(orden_a_fabrica)
        elif a_quien_pedir(ingredient, df_skus) != 1:
            print("############## PIDIENDO NONONONONO #############")
            print(int(final_needed["Ingredients"][ingredient]), "--- Ingredient ---", ingredient)
            # orden_otro_grupo = pedir_orden_otro_grupo(sku,cantidad)
            pass

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)
    return df_orders
# ****************************************************************************************************************** #
# ****************************************************************************************************************** #
def add_ingredient(sku, cantidad, order_id, fecha_vencimiento, df_orders):
    try:
        contador = max(df_orders["Prioridad"]) + 1
    except:
        contador=0
    basic_needed = needed_in_order(sku, cantidad, df_receipts, df_skus)
    final_needed = check_lotes_ingredientes(basic_needed, df_receipts, df_skus)
    for n_ingredient in range(cantidad):
        ingredient_add = [order_id, "Pidiendo", "Ingrediente", sku, "None", fecha_vencimiento, contador, 0]
        df_orders = df_orders.append({"OrderID":ingredient_add[0], "Status":ingredient_add[1], "Tipo_Producto":ingredient_add[2], "SKU_Producto":ingredient_add[3], "IDProductoAsignado":ingredient_add[4], 
            "Vencimiento_Order":ingredient_add[5], "Prioridad": contador, "Sub_Producto_De": ingredient_add[7]}, ignore_index=True)

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)
    if a_quien_pedir(sku, df_skus) == 1:
        orden_a_fabrica = elaborar_en_fabrica(sku, int(final_needed["Ingredients"][sku]))
        print("############## PIDIENDO #############") 
        print(int(final_needed["Ingredients"][sku]), "--- Ingredient ---", sku)

        #print(orden_a_fabrica)
    elif a_quien_pedir(sku, df_skus) != 1:
        # rechazar_orden -> Anular la orden de id order_id y retornar que nuestro grupo no hace ese ingrediente
        pass

    
    ########## Pedir Ingrediente Segun Final_neeeded
    return(df_orders)
# ****************************************************************************************************************** #
# ****************************************************************************************************************** #


############################################################################################################################################
####              Crear macro-funcion que revise lo que hay en recepcion y vaya asignando al excel y moviendo a cocina                 ####
#### Crear macro-funcion que revise lo que vaya siendo cocinable en cocina, y enviar a cocinar a fabrica, siguiendo el orden del excel ####
####           Crear macro-funcion que revise ordenes listas -> las borra del excel -> las envia a despacho -> las despacha            ####
###########################################################################################################################################


def revisar_recepcion_pulmon():
    ### Revisar en el excel en orden de pedidos, los que estén en pidiendo a ver si llegaron esos skus
    ### Revisar el excel en orden y ver si tenemos esos skus en bodega o repecion y asignar el sku
    ### Creamos un df solamente con los elementos que tienen status "Pidiendo" y ordenamos por prioridad
    df_pidiendo = df_orders[(df_orders['Status'] == 'Pidiendo')].sort_values("Prioridad")
    # Recorrermos el df y revisamos la existencia de cada elemento en recepcion y pulmon
    print(df_pidiendo)
    for j in df_pidiendo.index:
        sku = df_pidiendo["SKU_Producto"][j]

        producto_id = check_ingredients_in_stock(sku, used_recepcion, used_pulmon)

        if producto_id == "0":
            # Si no está el elemento, o se hace nada
            print(f"No hay del sku {sku} en recepcion ni en pulmon")
        else:
            # Si está el elemento, este se mueve a cocina y se le asigna ID junto a status "Listo"
            print("EL ELEMENTO SI ESTA")
            mover_entre_almacenes(producto_id, used_cocina)
            print("Se ha movido a cocina")
            df_orders["IDProductoAsignado"][j] = producto_id
            df_orders["Status"][j] = "Listo"

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)



def revisar_cocina(id_cocina, id_despacho,df_orders):
    ## Esperando -> necesita sub_productos para mandarlo a fabricar
    ## Pidiendo -> estan pedidos y esperando a que lleguen
    ## Cocinando -> preparandose en cocina
    ## Listo -> para ser usado
    ## Despachar -> Enviar a despachar y despachar
    df_cocinando = df_orders[(df_orders['Status'] == 'Cocinando')].sort_values("Prioridad")
    df_esperando = df_orders[(df_orders['Status'] == 'Esperando')].sort_values("Prioridad")
    df_sub_productos = df_orders[(df_orders['Sub_Producto_De'] != 0)].sort_values("Prioridad")

    print("--------ESPERANDO--------------")
    print(df_esperando)
    print("--------SUB PRODUCTOS----------")
    print(df_sub_productos)
    print("--------COCINANDO--------------")
    print(df_cocinando)

    ## REVISAMOS LOS PLATOS/BANDEJA COCINANDO A VER SI LLEGARON y SI ES SOLO y LLEGÓ, SE ENVIA ALTIRO A DESPACHO ##

    if not df_cocinando.empty:
        for id_plato in df_cocinando.index:
            # Revisamos si es un plato solo
            print(df_cocinando["Sub_Producto_De"][id_plato], " --- ID_Plato: ", id_plato)
            if df_cocinando["Sub_Producto_De"][id_plato] == 0:
                print("estoy aca ----------")
                tipo = df_cocinando["Tipo_Producto"][id_plato]
                sku = df_cocinando["SKU_Producto"][id_plato]
                # Revisamos si está
                if check_platos_in_stock(sku, used_cocina) != "0":
                    _id = check_platos_in_stock(sku, used_cocina)
                    # Se envía a despacho y se cambia el Status a "Despachar"
                    mover_entre_almacenes(_id, used_despacho)#--------------------------------
                    print(f"Se ha movido la {tipo} a despacho")
                    ########################## Agregar IDAsignado Producto #####################################
                    df_orders["IDProductoAsignado"][id_plato] = _id
                    df_orders["Status"][id_plato] = "Despachar"
                else:
                    print(f"El/la {tipo} con sku {sku} no ha llegado a cocina")

            else:
                sku = df_cocinando["SKU_Producto"][id_plato]
                # Revisamos si está
                if check_platos_in_stock(sku, used_cocina) != "0":
                    _id = check_platos_in_stock(sku, used_cocina)
                    # se deja en listo
                    df_orders["Status"][id_plato] = "Listo"
                else:
                    print(f"El plato con sku {sku} no ha llegado a cocina")
        df_sub_productos = df_orders[(df_orders['Sub_Producto_De'] != 0)].sort_values("Prioridad")
        df_esperando = df_orders[(df_orders['Status'] == 'Esperando')].sort_values("Prioridad")
        print(df_esperando)
    ###########################################################################################################
    ## ACA SE REVISA QUE CADA PLATO DE CADA BANDEJA SE ENCUENTRE COMPLETO, SI ESE ES EL CASO, SE MANDA A COCINAR Y SE DEJA EN STATUS "COCINANDO" ##
    for i in df_esperando.index:
        if (df_esperando["Tipo_Producto"][i] == "Bandeja"):
            print("ES BANDEJAA")
            # Guardamos el sku de la bandeja en cuestión
            sku_bandeja = df_esperando["SKU_Producto"][i]
            # guardamos un df el cual es solamente los platos de la bandeja
            df_sub_platos = df_sub_productos[df_sub_productos["Sub_Producto_De"] == sku_bandeja]

            print("REVISION DE BANDEJA")
            ## REVISAREMOS QUE TODOS LOS PLATOS DE ESA BANDEJA ESTEN LISTOS y SI ESTÁN LISTOS SE MANDA A FABRICAR LA BENDEJA Y SE DEJA EN ESTADO COCINANDO ##
            lista_status_platos = df_sub_platos["Status"].values.tolist()
            # eliminados prioridades repetidas
            lista_status_limpia = list(dict.fromkeys(lista_status_platos))
            print(lista_status_limpia)
            listo_1 = True
            for status in lista_status_limpia:
                if status != "Listo":
                    listo_1 = False
            # Si estaan todos los platos listos, la bandeja se pide a fábrica y entonces la bandeja pasa a estar en status "Cocinando"
            if listo_1 == True:
                df_orders["Status"][i] = "Cocinando"
                sku_buscar = df_skus[df_skus["SKU"] == sku_bandeja]
                lote_sku = sku_buscar['Lote producción'].values[0]
                print("#######################################")
                print(int(sku_bandeja), int(lote_sku))
                print(elaborar_en_fabrica(int(sku_bandeja), int(lote_sku)))#------------------------------------------------
                print("#######################################")
                df_orders.to_csv("Produccion/order_tracker.csv", index=False)
                break
            else:
                print(f"No todos los platos de la bandeja sku: {sku_bandeja} están listos")

            print(df_sub_platos)
            for j in df_sub_platos.index:
                # Guardamos el sku del plato en cuestión
                sku_plato = df_sub_platos["SKU_Producto"][j]
                # guardamos un df el cual es solamente productos del plato
                df_sub_ingredientes = df_sub_productos[df_sub_productos["Sub_Producto_De"] == sku_plato]
                print(df_sub_ingredientes)
                # guardamos prioridades en una lista, ya que estas diferencian ordenes
                lista_prioridades = df_sub_ingredientes["Prioridad"].values.tolist()
                # eliminados prioridades repetidas
                lista_prioridades_limpia = list(dict.fromkeys(lista_prioridades))
                for prio in lista_prioridades_limpia:
                    df_especifico = df_sub_ingredientes[(df_sub_ingredientes["Prioridad"] == prio)]
                    # Creamos una lista con los status de los ingredientes de esa prioridad
                    lista_status = df_especifico["Status"].values.tolist()
                    listo = True
                    for status in lista_status:
                        if status != "Listo":
                            listo = False
                    # Si todo está listo, entonces breakeamos (no tenemo que revisar más ingredientes de ese plato)
                    if listo == True:
                        df_orders["Status"][j] = "Cocinando"
                        print(f"Se ha mandado a cocinar el plato de index: {j}")
                        sku_buscar = df_skus[df_skus["SKU"] == sku_plato]
                        lote_sku = sku_buscar['Lote producción'].values[0]
                        print("#######################################")
                        print(int(sku_plato), int(lote_sku))
                        print(elaborar_en_fabrica(int(sku_plato), int(lote_sku)))#--------------------------------------------------
                        print("#######################################")
                        break

        elif (df_esperando["Tipo_Producto"][i] == "Plato"):
            if df_esperando["Sub_Producto_De"][i] == 0:
                print("EL PEDIDO ES UN PLATO NOMAS")
                # Guardamos el sku del plato en cuestión
                sku_producto = df_esperando["SKU_Producto"][i]
                # guardamos un df el cual es solamente productos del plato
                df_sub_de_sku = df_sub_productos[df_sub_productos["Sub_Producto_De"] == sku_producto]
                print(df_sub_de_sku)
                # guardamos prioridades en una lista, ya que estas diferencian ordenes
                lista_prioridades = df_sub_de_sku["Prioridad"].values.tolist()
                # eliminados prioridades repetidas
                lista_prioridades_limpia = list(dict.fromkeys(lista_prioridades))
                for prio in lista_prioridades_limpia:
                    df_especifico = df_sub_de_sku[(df_sub_de_sku["Prioridad"] == prio)]
                    # Creamos una lista con los status de los ingredientes de esa prioridad
                    lista_status = df_especifico["Status"].values.tolist()
                    listo = True
                    for status in lista_status:
                        if status != "Listo":
                            listo = False
                    # Si todo está listo, entonces breakeamos (no tenemo que revisar más ingredientes de ese plato)
                    if listo == True:
                        df_orders["Status"][i] = "Cocinando"
                        print(f"Se ha mandado a cocinar el id plato {i}")
                        sku_buscar = df_skus[df_skus["SKU"] == sku_producto]
                        lote_sku = sku_buscar['Lote producción'].values[0]
                        print("#######################################")
                        print(int(sku_producto), int(lote_sku))
                        print(elaborar_en_fabrica(int(sku_producto), int(lote_sku)))#----------------------------------------------------
                        print("#######################################")
                        break

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)

def revisar_despacho(df_orders):

    try:
        min_prioridad = min(df_orders["Prioridad"])
        max_prioridad = max(df_orders["Prioridad"])

    except:
        print("No Orders")
        return "No Orders"
    
    if max_prioridad == 0: 
        df_pedido = df_orders[df_orders["Sub_Producto_De"] == 0]
        df_pedido = df_pedido[df_pedido["Prioridad"] == 0]
        df_listos = df_pedido[df_pedido["Status"] == "Despachar"]
        if len(df_pedido) == len(df_listos) and len(df_pedido) != 0 and len(df_listos) != 0:
            print(enviar_oc(df_listos["OrderID"].values[0], df_listos["IDProductoAsignado"].values[0]))
            print(df_listos["IDProductoAsignado"].values[0])
            print("He enviado la ORDEN DE COMPRA")
            df_orders.drop(df_orders[df_orders['OrderID'] == df_listos["OrderID"].values[0]].index, inplace = True)

    else:
        for x in range(min_prioridad,max_prioridad+1):
            df_pedido = df_orders[df_orders["Sub_Producto_De"] == 0]
            df_pedido = df_pedido[df_pedido["Prioridad"] == x]
            df_listos = df_pedido[df_pedido["Status"] == "Despachar"]
            print(f"LISTOS: {df_listos}")
            print(f"lenLISTOS: {len(df_listos)}")
            print(f"PEDIDO: {df_pedido}")
            print(f"lenPEDIDO: {len(df_pedido)}")
            if len(df_pedido) == len(df_listos) and len(df_pedido) != 0 and len(df_listos) != 0:
                print("ENtre al if")
                print(enviar_oc(df_listos["OrderID"].values[0], df_listos["IDProductoAsignado"].values[0]))
                print("He enviado la orden de compra por abajo")
                df_orders.drop(df_orders[df_orders['OrderID'] == df_listos["OrderID"].values[0]].index, inplace = True)

    df_orders.to_csv("Produccion/order_tracker.csv", index=False)
    return df_orders

def revisar_ordenes_vencidas(df_orders):
    ## if df_orders["Vencimiento_Order"] < Tiempo_actual:
    ## Eliminar la Orden del excel
    ## Anular la orden
    pass


## Se gatilla el scheduler:

# revisar_recepcion_pulmon()
# revisar_cocina("id_cocina", "id_despacho",df_orders)
# df_orders = add_bandeja(11000, 1, "aaaa", df_orders)
# df_orders = add_bandeja(10000, 1, "bbbb", df_orders)
# revisar_despacho(0,0,df_orders)
# df_orders = add_plato(3000, 1, "cccc", df_orders)
# df_orders = add_plato(3000, 1, "aaaa", df_orders)
# df_orders = add_plato(3000, 1, "bbbb", df_orders)
# df_orders = add_ingredient(50, 1, "dddd", df_orders)
# revisar_recepcion_pulmon()
# print(df_orders)

def get_row_orders(sku, df_orders):
    row_value = df_orders[df_orders["SKU_Producto"] == sku]
    row_value = row_value[row_value["Sub_Producto_De"] == 3000]


## get_row_orders(56, df_orders)
## '62a510d8ffe0cc25e67ab31b'