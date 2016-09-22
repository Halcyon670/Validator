import pypyodbc
import xml.etree.ElementTree as ET

class Query:

    def runquery(self, sql):
        file = open('config.xml', 'r')
        config = ''
        for i in file:
            config += i
        file.close()

        root = ET.fromstring(config)
        driver = root.find('./DatabaseSettings/Driver').text
        server = root.find('./DatabaseSettings/Server').text
        database = root.find('./DatabaseSettings/Database').text
        user = root.find('./DatabaseSettings/User').text
        password = root.find('./DatabaseSettings/Password').text

        connection = pypyodbc.connect('DRIVER={' + driver + '};SERVER=' + server + ';DATABASE=' + database + ';uid=' + user + ';pwd=' + password + '')
        cursor = connection.cursor()
        sqlcommand = sql
        cursor.execute(sqlcommand)
        results = cursor.fetchall()
        connection.close()
        return results