import pymysql
import pandas
import matplotlib.pyplot as plt
import sys


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

print("Sisesta 1 - Öised andmed")
print("Sisesta 2 - Hommiksued ja päevased andmed")
whichQuery = int(input("Valik: "))
if whichQuery == 1:
    # Öised andmed
    query = """SELECT * FROM sensor_data WHERE created < '2020-04-24 06:30:00';"""
elif whichQuery == 2:
    # Hommikused ja päevased andmed
    query = """SELECT * FROM sensor_data WHERE created > '2020-04-24 06:30:00' and created < '2020-04-24 11:20:00';"""
else:
    sys.exit("Vale sisend. Sisend saab olla kas 1 või 2. Programm lõpetab töö ...")
conn = getDBConnection()

df = pandas.read_sql(query, conn)
conn.close()
del df['ID']
del df['board_ID']



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
#sub_df3.set_index('created')['temp'].plot()

# hum plot
sub_df4 = df[['created', 'hum']].copy()
# Konverteerime datetime objektideks datetimeid
sub_df4['created'] = pandas.to_datetime(sub_df4['created'])
#sub_df4.set_index('created')['hum'].plot()

print()
print("Sisesta 1 - CO2")
print("Sisesta 2 - VOC")
print("Sisesta 3 - Temp")
print("Sisesta 4 - Hum")
number = int(input("Valik: "))

if number == 1:
    sub_df.set_index('created')['co2'].plot()
if number == 2:
    sub_df2.set_index('created')['voc'].plot()
if number == 3:
    sub_df3.set_index('created')['temp'].plot()
if number == 4:
    sub_df4.set_index('created')['hum'].plot()
plt.show()
