import pymysql
from pymysql.cursors import DictCursor

def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='admin',
        db='bd_hotel_san_eduardo',
        port=3306
    )

def obtener_conexion_dict():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='admin',
        db='bd_hotel_san_eduardo',
        port=3306,
        cursorclass=DictCursor
    )

