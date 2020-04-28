from flask import Flask, jsonify, make_response, request
import datetime
import pymysql
import os

app = Flask(__name__)

def getDBConnection():
    #####
    # PYMYSQL VARIABLES
    host = 'eu-cdbr-west-02.cleardb.net'
    user = 'bf0d0fe69040cf'
    password = '7a8c5510'
    database = 'heroku_cace524c997f2ec'
    port = 3306
    #####

    return pymysql.connections.Connection(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# ATM without params. WIl lhave to add params later when board is connected
@app.route('/data', methods=['POST'])
def post_data():
    # temp,pressure,VOC,CO2,humidity
    print(request.data.decode("UTF-8"))
    data = request.data.decode("UTF-8").split(",")
    # TEST INSERT
    conn = getDBConnection()
    cur = conn.cursor()

    print("""INSERT INTO sensor_data (board_ID, temp, voc, hum, co2, pres) VALUES (%s, %s, %s, %s, %s, %s);""" %
                (data[0], data[1], data[3], data[5], data[4], data[2]))
    cur.execute("""INSERT INTO sensor_data (board_ID, temp, voc, hum, co2, pres) VALUES (%s, %s, %s, %s, %s, %s);""" %
                (data[0], data[1], data[3], data[5], data[4], data[2]))
    conn.commit()

    conn.close()
    return "All done"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
