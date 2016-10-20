
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
            i += 1
        # ---------------------------------------------------------------------------

        return unions

    # Use the list generated in findunions to isolate the last two queries
    def findqueries(self, sql, unions):
        queries = []

        queries.append(sql[unions[0]+10:unions[1]])
        queries.append(sql[unions[1]+10:])

        return queries

    # Prepare the queries for CTE format
    def removestep(self, queries):
        selectqueries = []

        # Isolate the SELECT statement----------------------------------------------------
        for i in queries:
            pos = 0
            parenpos = 0
            tempword = ''

            for j in i:
                if j == ' ' and tempword == 'FROM' and parenpos == 0:
                    break
                elif j == ' ' and tempword != 'FROM':
                    pos += 1
                    tempword = ''
                elif j == '(':
                    tempword += j
                    pos += 1
                    parenpos += 1
                elif j == ')':
                    tempword += j
                    pos += 1
                    parenpos -= 1
                else:
                    tempword += j
                    pos += 1

            selectqueries.append(i[:pos-5])
        # --------------------------------------------------------------------------------

        # Cycle through the SELECT statement, removing Step ------------------------------
        selectqueriesstep = []

        for i in selectqueries:
            templine = ''
            firstpos = 0
            pos = 0
            readline = False
            parenpos = 0

            for j in i:
                if readline is True and j == ',' and parenpos == 0:
                    templine += j
                    break
                elif j == '\'' and i[pos+1] == 'S' and i[pos+2] == 't' and i[pos+3] == 'e' and i[pos+4] == 'p' and i[pos+5] == ' ':
                    firstpos = pos
                    readline = True
                    templine += j
                    pos += 1
                elif j == '(' and readline is True:
                    parenpos += 1
                    pos += 1
                    templine += j
                elif j == ')' and readline is True:
                    parenpos -= 1
                    pos += 1
                    templine += j
                elif readline is True:
                    templine += j
                    pos += 1
                else:
                    pos += 1

            selectqueriesstep.append(i.replace(i[firstpos:pos+1], '')[::-1])
        # -----------------------------------------------------------------------------

        # Now remove StepInfo: ---------------------------------------------------------
        selectqueriesstepinfo = []

        for i in selectqueriesstep:
            templine = ''
            pos = 0
            parenpos = 0

            for j in i:
                if j == '\'' and i[pos+1] == ' ' and i[pos+2] == ',' and parenpos == 0:
                    templine += j
                    pos += 1
                    break
                elif j == '(':
                    parenpos += 1
                    pos += 1
                    templine += j
                elif j == ')':
                    parenpos -= 1
                    pos += 1
                    templine += j
                else:
                    templine += j
                    pos += 1

            selectqueriesstepinfo.append(i.replace(i[:pos+2], '')[::-1])
        # ---------------------------------------------------------------------------

        # Return the modified queries ----------------------------------------------
        finalqueries = []
        querynum = 0

        for i in queries:
            finalqueries.append(i.replace(selectqueries[querynum], selectqueriesstepinfo[querynum]))
            querynum += 1

        return finalqueries
        # --------------------------------------------------------------------------

    # Find the BIS2_GEO_chairs join, and format the queries based on the predicates
    def standid(self, queries):
        pass

    # Combine the queries to the final format
    def combinequeries(self, queries):
        finalquery = ''

        finalquery = 'WITH A AS('
        finalquery += queries[0]
        finalquery += ') , B AS('
        finalquery += queries[1]
        finalquery += ')  SELECT \'Drops\', * FROM A LEFT JOIN B ON A.StandID = B.StandID WHERE B.StandID IS NULL UNION ALL SELECT \'Not Equal\', * FROM A FULL OUTER JOIN B ON A.StandID = B.StandID WHERE A.TheoWin <> B.TheoWin AND A.TheoWin IS NOT NULL AND B.TheoWin IS NOT NULL'

        return finalquery