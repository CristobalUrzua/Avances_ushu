import paramiko
import requests
import datetime
import datetime
from datetime import timezone
from datetime import timedelta
from datetime import timezone
from Modulos_OC import recepcionar_orden, rechazar
from metomi.isodatetime.parsers import TimePointParser
from Modulos_Help import order_response
import pandas as pd
import dateutil.parser
import datetime
from pytz import utc
from dateutil import parser


df_receipts = pd.read_csv("Produccion/receipts.csv")
df_skus = pd.read_csv("Produccion/skus.csv")


##FTP CPNECCTION##
def get_orders():
    host,port ="ensalada.ing.puc.cl",22
    transport = paramiko.Transport((host,port))
    username,password = "grupo8_desarrollo","mdy1mb7PrhJnsCa5Leqj"
    transport.connect(None,username,password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(path='pedidos')
    archivos = sftp.listdir()
    gap = []
    platos2 = ["10000", "11000", "12000"]

    for xml_file in archivos:
        if xml_file != ".cache":
            with sftp.open(xml_file) as remote_file:
                for line in remote_file.readlines():
                    print("LINE")
                    print(line)
                    if line[1] == "o":
                        url_almacenes = "https://dev.api-bodega.2022-1.tallerdeintegracion.cl/oc/obtener/{}".format(line[11:35])
                        response = requests.request("GET", url_almacenes)
                        arreglo = (response.json())
                        arreglo2 = arreglo[0]
                        fecha_entrega = arreglo2['fechaEntrega']
                        identificador = arreglo2['_id']
                        time_now = datetime.datetime.now(timezone.utc)
                        time_now2 = time_now.isoformat().replace("+00:00", "Z")
                        date1 = parser.parse(fecha_entrega)
                        date2 = parser.parse(time_now2)
                        if line[45:50] in platos2:
                            print(f"ES BANDEJA sku:{line[45:50]}")
                            if date1 > date2:
                                tiempo_total = int(order_response(int(line[45:50]), fecha_entrega, int(line[61]), df_receipts, df_skus))/60
                                horas_agregar = datetime.timedelta(hours=int(tiempo_total))
                                date3 = date2 + horas_agregar
                                if date3 < date1: 
                                    if len(gap) > 5:
                                        break
                                    print("Podemos_recibirla")
                                    print(f"Date 3: {date3} & Date 1: {date1}")
                                    print(recepcionar_orden(identificador))
                                    gap.append([fecha_entrega, time_now2, identificador, line[45:50], line[61], xml_file])
                                    
                                    sftp.remove(xml_file)
                                else:
                                    print(f"Date 3: {date3} & Date 1: {date1}")
                                    print("rechazo")
                                    rechazar(identificador)
                                    sftp.remove(xml_file)
                            elif date1 < date2:
                                print("la elimino porque venció")
                                print(f"Date 1: {date1} & Date 2: {date2}")
                                sftp.remove(xml_file)
                        else:
                            print(f"ES PLATO sku:{line[45:49]}")
                            if date1 > date2:
                                tiempo_total = int(order_response(int(line[45:49]), fecha_entrega, int(line[60]), df_receipts, df_skus))/60
                                date3 = date2 + timedelta(hours=int(tiempo_total))
                                if date3 < date1:
                                    if len(gap) > 5:
                                        break
                                    print("podemos_recibirla")
                                    print(f"Date 3: {date3} & Date 1: {date1}")
                                    print(recepcionar_orden(identificador))
                                    gap.append([fecha_entrega, time_now2, identificador, line[45:49], line[60], xml_file])
                                    sftp.remove(xml_file)
                                else:
                                    print("rechazo")
                                    print(f"Date 3: {date3} & Date 1: {date1}")
                                    rechazar(identificador)
                                    sftp.remove(xml_file)
                            elif date2 > date1:
                                print("la elimino porque venció")
                                print(f"Date 1: {date1} & Date 2: {date2}")
                                sftp.remove(xml_file)

    gap.sort(reverse=True)
    sftp.close()
    transport.close()
    return(gap)


if __name__ == "__main__":
    print(get_orders())


# print(get_orders())
# with open('orders_ftp.csv', 'w') as file:
#     writer = csv.writer(file, delimiter= ',')
#     low_orders = low_orders[:5]
#     for oc in low_orders:
#         writer.writerow(oc)
#     file.close()

# [['2022-06-12T02:02:00.000Z', '2022-06-11T22:10:58.243620Z', '62a510d8ffe0cc25e67ab31b', '10000', '1', '1654984920682-4482.xml']]   
