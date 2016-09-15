import pypyodbc


class Query:

    def runquery(self, sql):
        connection = pypyodbc.connect('DRIVER={SQL Server};SERVER=10.0.4.26;DATABASE=CRMDemo;uid=BIS2User;pwd=3Bx?zPaae')
        cursor = connection.cursor()
        sqlcommand = sql
        cursor.execute(sqlcommand)
        results = cursor.fetchall()
        connection.close()
        return results