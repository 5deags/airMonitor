import pymysql
import pandas
import matplotlib.pyplot as plt
import sys
from datetime import timedelta
from matplotlib.dates import DateFormatter


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

print("Sisesta 1 - Kaasa NETATMO andmed")
netatmo = int(input("Kaasa NETATMO?: "))

print("Sisesta 1 - VANAD Öised andmed")
print("Sisesta 2 - VANAD Hommiksued ja päevased andmed")
print("Sisesta 3 - UUED andmed")
whichQuery = int(input("Valik: "))
if whichQuery == 1:
    # Öised andmed
    query = """SELECT * FROM sensor_data WHERE created < '2020-04-24 06:30:00';"""
elif whichQuery == 2:
    # Hommikused ja päevased andmed
    query = """SELECT * FROM sensor_data WHERE created > '2020-04-24 06:30:00' and created < '2020-04-24 11:20:00';"""
elif whichQuery == 3:
    query = """SELECT * FROM sensor_data WHERE created > '2020-05-03 08:33:00' and created < '2020-05-04 08:37:00';"""
else:
    sys.exit("Vale sisend. Sisend saab olla kas 1 või 2. Programm lõpetab töö ...")
conn = getDBConnection()

df = pandas.read_sql(query, conn)
conn.close()
# EELTÖÖTLUS
del df['ID']
del df['board_ID']

df['created'] = pandas.DatetimeIndex(df['created']) + timedelta(hours=3)
df['created'] = df['created'].map(lambda t: t.strftime('%Y-%m-%d %H:%M:%S'))

if netatmo == 1:
    df_netatmo = pandas.read_csv("C:\\Users\\Michael\\Desktop\\LÕPUTÖÖ\\Smart Home Paab_5_5_2020.csv")
    del df_netatmo['Timestamp_UNIX']
    del df_netatmo['Noise']
    del df_netatmo['Pressure']
    df_netatmo['Timestamp'] = pandas.to_datetime(df_netatmo['Timestamp'])
    #print(df_netatmo)
    print("----------------------NETATMO DATA START----------------------")
    av_column_net = df_netatmo.mean(axis=0)
    print()
    print("------- MEAN -------")
    print(av_column_net)
    print("--------------------")
    print("------- STD -------")
    print(df_netatmo.std())
    print("-------------------")
    print("MIN/MAX per column")
    print("CO2 max:", df_netatmo.loc[df_netatmo['CO2'].idxmax()])
    print("CO2 min:", df_netatmo.loc[df_netatmo['CO2'].idxmin()])
    print("temp max:", df_netatmo.loc[df_netatmo['Temperature'].idxmax()])
    print("temp min:", df_netatmo.loc[df_netatmo['Temperature'].idxmin()])
    print("hum max:", df_netatmo.loc[df_netatmo['Humidity'].idxmax()])
    print("hum min:", df_netatmo.loc[df_netatmo['Humidity'].idxmin()])
    print("-----------------------NETATMO DATA END-----------------------")



# MEAN OF ALL DF VALUES
av_column = df.mean(axis=0)
print()
print("------- MEAN -------")
print(av_column)
print("--------------------")
print("------- STD -------")
print(df.std())
print("-------------------")
print("MIN/MAX per column")
print("CO2 max:", df.loc[df['co2'].idxmax()])
print("CO2 min:", df.loc[df['co2'].idxmin()])
print("VOC max:", df.loc[df['voc'].idxmax()])
print("VOC min:", df.loc[df['voc'].idxmin()])
print("temp max:", df.loc[df['temp'].idxmax()])
print("temp min:", df.loc[df['temp'].idxmin()])
print("hum max:", df.loc[df['hum'].idxmax()])
print("hum min:", df.loc[df['hum'].idxmin()])
print("pres max:", df.loc[df['pres'].idxmax()])
print("pres min:", df.loc[df['pres'].idxmin()])
#df.plot(kind='bar')
#av_column.plot(kind='bar')
#plt.show()
#print(df)
#print(av_column)

# CO2 Plot
sub_df = df[['created', 'co2']].copy()
# Konverteerime datetime objektideks datetimeid
sub_df['created'] = pandas.to_datetime(sub_df['created'])
if netatmo == 1:
    sub_df_netatmo = df_netatmo[['Timestamp', 'CO2']].copy()
#sub_df.set_index('created')['co2'].plot()


# VOC Plot
sub_df2 = df[['created', 'voc']].copy()
# Konverteerime datetime objektideks datetimeid
sub_df2['created'] = pandas.to_datetime(sub_df2['created'])
#sub_df2.set_index('created')['voc'].plot()

# Temp plot
sub_df3 = df[['created', 'temp']].copy()
# Konverteerime datetime objektideks datetimeid
sub_df3['created'] = pandas.to_datetime(sub_df3['created'])
if netatmo == 1:
    sub_df3_netatmo = df_netatmo[['Timestamp', 'Temperature']].copy()
#sub_df3.set_index('created')['temp'].plot()

# hum plot
sub_df4 = df[['created', 'hum']].copy()
# Konverteerime datetime objektideks datetimeid
sub_df4['created'] = pandas.to_datetime(sub_df4['created'])
if netatmo == 1:
    sub_df4_netatmo = df_netatmo[['Timestamp', 'Humidity']].copy()
#sub_df4.set_index('created')['hum'].plot()

print()
print("Sisesta 1 - CO2"),
if netatmo == 1:
    print(" + NETATMO CO2")
else:
    print("\n")
print("Sisesta 2 - VOC")
print("Sisesta 3 - Temp"),
if netatmo == 1:
    print(" + NETATMO TEMP")
else:
    print("\n")
print("Sisesta 4 - Hum"),
if netatmo == 1:
    print(" + NETATMO HUM")
else:
    print("\n")
number = int(input("Valik: "))

if number == 1:
    if netatmo == 1:
        sub_df_netatmo.set_index('Timestamp')['CO2'].plot()
    ax = sub_df.set_index('created')['co2'].plot()
    date_form = DateFormatter("%Y-%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
    #ax.set_xticklabels([pandas_datetime.strftime("%Y-%m-%d %H:%M:%S") for pandas_datetime in df.created])
if number == 2:
    ax = sub_df2.set_index('created')['voc'].plot()
    date_form = DateFormatter("%Y-%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
if number == 3:
    if netatmo == 1:
        sub_df3_netatmo.set_index('Timestamp')['Temperature'].plot()
    ax = sub_df3.set_index('created')['temp'].plot()
    date_form = DateFormatter("%Y-%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)
if number == 4:
    if netatmo == 1:
        sub_df4_netatmo.set_index('Timestamp')['Humidity'].plot()
    ax = sub_df4.set_index('created')['hum'].plot()
    date_form = DateFormatter("%Y-%m-%d %H:%M:%S")
    ax.xaxis.set_major_formatter(date_form)

plt.show()
