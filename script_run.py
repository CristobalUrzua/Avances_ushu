from read_ftp import get_orders
import pandas as pd
import csv
from Flujo import add_bandeja, add_ingredient, add_plato, revisar_recepcion_pulmon, revisar_despacho, revisar_cocina
from Modulos_Help import needed_in_order, check_lotes_platos, check_lotes_ingredientes, df_orders, df_skus, df_receipts, a_quien_pedir, check_ingredients_in_stock
from Modulos import elaborar_en_fabrica, used_recepcion, used_pulmon, mover_entre_almacenes, id_cocina_develop, id_despacho_develop

revisar_recepcion_pulmon()
revisar_cocina(id_cocina_develop, id_despacho_develop, df_orders)
revisar_despacho(df_orders)
## VER SI FUNCIONA DESPACHO O DESPACHAR MANUAL.

# new_order = get_orders()
new_order = [['2022-06-13T12:12:00.000Z', '2022-06-13T08:27:20.889958Z', '62a6f1507e2c0482a69c3576', '5100', '3', '1655107920538-6867.xml'], ['2022-06-13T12:12:00.000Z', '2022-06-13T08:27:20.042958Z', '62a6f1507e2c04f4269c3573', '5000', '1', '1655107920540-9095.xml'], ['2022-06-13T12:12:00.000Z', '2022-06-13T08:27:18.238964Z', '62a6f1507e2c04f54a9c3572', '12000', '3', '1655107920541-7662.xml'], ['2022-06-13T12:12:00.000Z', '2022-06-13T08:27:17.337961Z', '62a6f1507e2c04da7e9c3574', '12000', '4', '1655107920542-3202.xml'], ['2022-06-13T12:02:00.000Z', '2022-06-13T08:27:21.747982Z', '62a6eef87e2c048ed29c3456', '12000', '1', '1655107321008-5001.xml'], ['2022-06-13T12:02:00.000Z', '2022-06-13T08:27:19.184959Z', '62a6eef87e2c0424899c3458', '5000', '4', '1655107321006-4545.xml']]
for order in new_order:
    print(f"Viendo orden {order[2]}")
    df = pd.read_csv("Produccion/orders_ftp.csv")
    lista_id = []
    for index, row in df.iterrows():
        lista_id.append(row["id"])
    if order[2] not in lista_id:
        # Se hace y se escribe
        print("entre")
        with open('Produccion/orders_ftp.csv', 'a') as file:
            writer = csv.writer(file, delimiter= ',')
            #escribimos en el csv los que tienen un sku primero
            writer.writerow(order)
        new_order = order

        if int(new_order[3]) < 1000:
            ### aceptar la orden
            df_orders = add_ingredient(int(new_order[3]), int(new_order[4]), new_order[2], new_order[0], df_orders)

        elif int(new_order[3]) >= 1000 and int(new_order[3]) < 10000:
            ### aceptar la orden
            df_orders = add_plato(int(new_order[3]), int(new_order[4]), new_order[2], new_order[0], df_orders)

        elif int(new_order[3]) >= 10000:
            ### aceptar la orden
            df_orders = add_bandeja(int(new_order[3]), int(new_order[4]), new_order[2], new_order[0], df_orders)

# # [['2022-06-12T02:02:00.000Z', '2022-06-11T22:10:58.243620Z', '62a510d8ffe0cc25e67ab31b', '10000', '1', '1654984920682-4482.xml']]
# new_order = [['2022-06-13T11:42:00.000Z', '2022-06-13T07:43:22.087030Z', '62a6ea487e2c0449589c2c63', '12000', '3', '1655106121305-3932.xml'], ['2022-06-13T11:42:00.000Z', 
#'2022-06-13T07:43:19.505050Z', '62a6ea487e2c048dbf9c2c60', '12000', '2', '1655106121304-2953.xml'], ['2022-06-13T11:42:00.000Z', '2022-06-13T07:42:08.221315Z', '62a6ea487e2c0438399c2c62', '5000', '1', '1655106121306-6531.xml'], ['2022-06-13T11:42:00.000Z', '2022-06-13T07:42:07.261253Z', '62a6ea487e2c0477b69c2c61', '5000', '1', '1655106121310-9713.xml'], ['2022-06-13T11:22:00.000Z', '2022-06-13T07:43:05.242349Z', '62a6e5987e2c046c369c2c18', '10000', '2', '1655104921202-1152.xml'], ['2022-06-13T11:22:00.000Z', '2022-06-13T07:42:54.653605Z', '62a6e5987e2c0460529c2c17', '5100', '2', '1655104921199-1281.xml'], ['2022-06-13T11:22:00.000Z', '2022-06-13T07:42:25.416045Z', '62a6e5987e2c04e18c9c2c16', '11000', '3', '1655104921199-3721.xml'], ['2022-06-13T11:02:00.000Z', '2022-06-13T07:43:28.471345Z', '62a6e0e87e2c047c7a9c2bb7', '5000', '3', '1655103720847-9788.xml'], ['2022-06-13T11:02:00.000Z', '2022-06-13T07:43:12.358281Z', '62a6e0e87e2c042cfd9c2bb8', '11000', '2', '1655103720843-5540.xml'], ['2022-06-13T11:02:00.000Z', '2022-06-13T07:42:46.733359Z', '62a6e0e87e2c04436d9c2bb6', '11000', '2', '1655103720846-4286.xml'], ['2022-06-13T10:52:00.000Z', '2022-06-13T07:43:25.918038Z', '62a6de907e2c04cf5f9c2b97', '10000', '1', '1655103121401-9576.xml'], ['2022-06-13T10:52:00.000Z', '2022-06-13T07:42:14.288427Z', '62a6de907e2c043f759c2b96', '5100', '1', '1655103121395-9960.xml'], ['2022-06-13T10:42:00.000Z', '2022-06-13T07:42:34.447442Z', '62a6dc387e2c04546b9c2b6a', '11000', '1', '1655102520576-9868.xml'], ['2022-06-13T10:42:00.000Z', '2022-06-13T07:42:11.001748Z', '62a6dc387e2c04cf5c9c2b6b', '11000', '1', '1655102520571-2389.xml'], ['2022-06-13T10:32:00.000Z', '2022-06-13T07:42:38.547711Z', '62a6d9e07e2c04621a9c2b4c', '5100', '4', '1655101920961-3633.xml'], ['2022-06-13T10:32:00.000Z', '2022-06-13T07:42:12.395189Z', '62a6d9e07e2c0407a09c2b4e', '5100', '4', '1655101920971-3730.xml'], ['2022-06-13T10:22:00.000Z', '2022-06-13T07:42:57.975331Z', '62a6d7887e2c0480e59c2b1f', '10000', '1', '1655101321142-9397.xml'], ['2022-06-13T10:22:00.000Z', '2022-06-13T07:42:20.273397Z', '62a6d7887e2c04231d9c2b20', '11000', '3', '1655101321142-3716.xml'], ['2022-06-13T10:12:00.000Z', '2022-06-13T07:43:16.232517Z', '62a6d5307e2c0411819c2ae9', '5000', '1', '1655100720599-4560.xml'], ['2022-06-13T10:12:00.000Z', '2022-06-13T07:42:52.631089Z', '62a6d5307e2c04c4269c2aea', '12000', '1', '1655100720589-3172.xml'], ['2022-06-13T10:02:00.000Z', '2022-06-13T07:42:43.344057Z', '62a6d2d87e2c04fd719c2ac1', '10000', '1', '1655100121077-4442.xml'], ['2022-06-13T09:52:00.000Z', '2022-06-13T07:43:29.406468Z', '62a6d0807e2c0451209c2a8b', '10000', '3', '1655099521602-5387.xml'], ['2022-06-13T09:52:00.000Z', '2022-06-13T07:43:03.675139Z', '62a6d0807e2c041e159c2a8a', '5000', '1', '1655099521602-9418.xml'], ['2022-06-13T09:52:00.000Z', '2022-06-13T07:42:17.993131Z', '62a6d0807e2c0474be9c2a8c', '12000', '3', '1655099521598-1105.xml'], ['2022-06-13T09:42:00.000Z', '2022-06-13T07:42:17.072689Z', '62a6ce287e2c04d3469c2a5b', '5100', '4', '1655098920772-4686.xml'], ['2022-06-13T09:32:00.000Z', '2022-06-13T07:43:36.024560Z', '62a6cbd07e2c0428e79c2a34', '5000', '3', '1655098321232-1901.xml'], ['2022-06-13T09:12:00.000Z', '2022-06-13T07:42:59.391745Z', '62a6c7207e2c0459709c29e2', '11000', '3', '1655097120703-3588.xml'], ['2022-06-13T09:02:00.000Z', '2022-06-13T07:43:07.672448Z', '62a6c4c87e2c046b8f9c29b8', '5100', '1', '1655096521185-1778.xml'], ['2022-06-13T08:52:00.000Z', '2022-06-13T07:43:34.092109Z', '62a6c2707e2c0423629c2984', '10000', '3', '1655095920655-6762.xml'], ['2022-06-13T08:52:00.000Z', '2022-06-13T07:43:14.296244Z', '62a6c2707e2c0455fd9c2983', '5100', '2', '1655095920656-7385.xml']]