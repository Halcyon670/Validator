
class reformat:

    # Find, then return, the positions of the last two UNION ALLs
    def findunions(self, sql):
        pos = 0
        unions = []
        temp = ''

        # Isolate all UNION ALLs------------------------------------------------------
        for i in sql:
            if i != ' ':
                temp += i
                pos += 1
            elif i == ' ':
                if temp == 'UNION' and sql[pos+1] == 'A' and sql[pos+2] == 'L' and sql[pos+3] == 'L':
                    unions.append(pos-5)
                    pos += 1
                else:
                    temp = ''
                    pos += 1
        # ---------------------------------------------------------------------------

        # Limit to the last two -----------------------------------------------------
        length = len(unions) - 2
        i = 0

        while i < length:
            unions.remove(unions[0])
            i+= 1
        # ---------------------------------------------------------------------------

        return unions

    # Use the list generated in findunions to isolate the last two queries
    def findqueries(self, sql, unions):
        queries = []

        queries.append(sql[unions[0]+10:unions[1]])
        queries.append(sql[unions[1]+10:])

        return queries

    # Change the queries to the CTE format
    def formatqueries(self, queries):
        pass