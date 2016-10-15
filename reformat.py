from other import Other


class Formatting:

    def keywordsearch(self, keyword, sql):
        position = 0
        word = ''
        worddict = {}

        for i in sql:
            if i.isalpha():
                word = word + i
            else:
                for j in keyword:
                    if word == j:
                        worddict[position - len(j)] = j
                word = ''
            position += 1
        return worddict

    def parensubstring(self, sql, position):
        parencount = 0
        newsql = ''
        for i in sql[position - 1:]:

            if i == '(':
                parencount += 1
            elif i == ')':
                parencount -= 1

            newsql += i

            if parencount == 0:
                break

        newsql = newsql[1:]
        newsql = newsql[:-1]

        return newsql

    def firsttwoelements(self, list):
        first = 1000000000
        for i in list:
            if i < first:
                first = i

        second = 2000000000
        for i in list:
            if first < i < second:
                second = i

        newlist = []
        newlist.append(first)
        newlist.append(second)

        return newlist

    def dictorder(self, dict):
        list = []
        for i in dict:
            list.append(i)
        list.sort()

        return list

    def multitablewherecheck(self, joinorder, whereelement):
        flag = 0

        for i in joinorder:
            if i in whereelement:
                flag += 1
            else:
                continue

        if flag >= 2:
            return True
        else:
            return False

    def singletablewherecheck(self, table, whereelement):
        if table in whereelement:
            return True
        else:
            return False

    def singlemultiwhereelementcheck(self, table, whereelement, joins):
        flag = 0

        for i in joins:
            if i in whereelement:
                flag += 1
            else:
                continue

        if flag >= 2:
            return True
        else:
            return False


class SectionStrip:

    def stripouterquery(self, sql):
        while True:

            selectqueries = Formatting.keywordsearch(Formatting, ['SELECT'], sql)
            selects = Formatting.firsttwoelements(Formatting, selectqueries)

            firstselectquery = sql[selects[0]:selects[1]]
            firstselectqueryagg = Formatting.keywordsearch(Formatting, ['SUM', 'COUNT', 'AVG', 'MAX', 'MIN'], firstselectquery)

            if firstselectqueryagg == {}:
                sql = Formatting.parensubstring(Formatting, sql, selects[1])
            else:
                break

        return sql

    def stripaggs(self, sql):

        sql = SectionStrip.stripouterquery(SectionStrip, sql)
        selectqueries = Formatting.keywordsearch(Formatting, ['SELECT', 'FROM'], sql)

        selectfrom = 100001
        for i in selectqueries:
            if selectqueries[i] == 'FROM':
                if i < selectfrom:
                    selectfrom = i

        subselect = sql[:selectfrom - 1]

        aggpos = Formatting.keywordsearch(Formatting, ['SUM', 'COUNT'], subselect)
        aggposordered = Formatting.dictorder(Formatting, aggpos)
        aggfinal = []
        pos = 0
        for i in aggposordered:
            temp = ''

            if i >= pos:
                pos = i
            else:
                continue

            parencount = 0

            while True:


                if pos >= len(subselect):
                    break
                elif subselect[pos] == '(':
                    parencount += 1
                elif subselect[pos] == ')':
                    parencount -= 1
                elif parencount == 0 and subselect[pos] == ',':
                    aggfinal.append(temp)
                    break

                temp += subselect[pos]
                pos += 1

        return aggfinal

    def stripjoins(self, sql):

        sql = SectionStrip.stripouterquery(SectionStrip, sql)
        joinstructure = Formatting.keywordsearch(Formatting, ['FROM', 'INNER', 'LEFT', 'RIGHT', 'FULL'], sql)

        joinposorder = Formatting.dictorder(Formatting, joinstructure)

        joinfinal = []
        pos = 0
        j = 0
        parencount = 0

        for i in joinposorder:
            tempfull = ''

            if i >= pos:
                pos = i

            else:
                continue

            # Add an exception for RIGHT and LEFT string modifiers
            if sql[pos] + sql[pos + 1] + sql[pos + 2] + sql[pos + 3] + sql[pos + 4] + sql[pos + 5] == 'RIGHT(' or sql[pos] + sql[pos + 1] + sql[pos + 2] + sql[pos + 3] + sql[pos + 4] == 'LEFT(':
                continue

            while True:
                temp = ''

                while True:
                    if sql[pos + j] == ' ':
                        temp += sql[pos + j]
                        j += 1
                        break
                    elif sql[pos + j] == '(':
                        parencount += 1
                    elif sql[pos + j] == ')':
                        parencount -= 1

                    temp += sql[pos + j]
                    j += 1

                if temp in ['INNER ', 'LEFT ', 'RIGHT ', 'FULL ', 'JOIN ', 'WHERE ', 'GROUP '] and parencount == 0 and len(tempfull) > 15: # Not quite happy with this length check. Probably need to fix this up a bit.
                    j = 0
                    break

                else:
                    tempfull += temp
                    pos += j
                    j = 0

            joinfinal.append(tempfull)

        return joinfinal

    def stripwhere(self, sql):
        sql = SectionStrip.stripouterquery(SectionStrip, sql)
        wherestructure = Formatting.keywordsearch(Formatting, ['WHERE'], sql)

        # Check to see if there even IS a WHERE clause. If not, return an empty string. -----------------------------------------
        whereflag = False
        parenflag = 0
        temp = ''

        for i in sql:
            if i == '(':
                parenflag += 1
            elif i == ')':
                parenflag -=1
            elif i == ' ':
                if temp.upper() == 'WHERE' and parenflag == 0:
                    whereflag = True
                    temp = ''
                else:
                    temp = ''
            else:
                temp += i
        # -----------------------------------------------------------------------------------------------------------------------

        # If there is a WHERE clause, cycle through it character by character and pull it out, paying attention to the GROUP BY and ORDER BY clauses.
        # Otherwise, return an empty string. ------------------------------------------------------------------------------------
        if whereflag == True:
            wherelocation = 1
            for i in wherestructure:
                if i > wherelocation:
                    wherelocation = i

            wherefinal = ''
            pos = wherelocation
            parencount = 0

            while True:
                temp = ''

                while True:

                    if len(sql) < pos:
                        break
                    if sql[pos] == ' ':
                        temp += sql[pos]
                        pos += 1
                        break
                    elif sql[pos] == '(':
                        parencount += 1
                    elif sql[pos] == ')':
                        parencount -= 1

                    temp += sql[pos]
                    pos += 1

                if parencount == 0 and (temp in ['GROUP ', ' ORDER '] or len(sql) < pos):
                    break
                else:
                    wherefinal += temp

            return wherefinal

        else:
            wherefinal = ''
            return wherefinal

class Isolation:

    def aggorder(self, sql):

        aggs = SectionStrip.stripaggs(SectionStrip, sql)
        aggorder = []

        for i in aggs:
            temp = ''
            pos = 0
            tempi = i[::-1]

            while True:
                if tempi[pos] == ' ':
                    break
                else:
                    temp += tempi[pos]
                    pos += 1

            temp = temp[::-1]
            aggorder.append(temp)

        return aggorder

    def aggdict(self, sql, aggorder):
        aggs = SectionStrip.stripaggs(SectionStrip, sql)
        aggdict = {}

        index = 0
        for i in aggorder:
            aggdict[i] = aggs[index]
            index += 1

        return aggdict

    def joinorder(self, sql):

        joins = SectionStrip.stripjoins(SectionStrip, sql)
        joinorder = []

        for i in joins:
            temp = ''
            readflag = 0
            pos = 0

            while True:
                tempword = ''
                if readflag == 0:
                    while True:
                        if i[pos] == ' ':
                            pos += 1
                            break
                        else:
                            tempword += i[pos]
                            pos += 1

                elif readflag == 1:
                    while True:
                        if i[pos] in [' ', '*'] or (i[pos] == '(' and readflag == 1) or pos > len(i):
                            pos += 1
                            break
                        else:
                            temp += i[pos]
                            pos += 1

                    # Handle the possibility of an alias
                    if ' AS ' in i[pos:] and '*/' not in i[pos:]: # Checks for the possibility of an alias while ignoring the telltale comment sign of an SQLTC
                        newtemp = ''
                        asflag = 0
                        temp = ''

                        while True:
                            newtemp = ''
                            while True:
                                if pos >= len(i) or (asflag == 1 and i[pos] == ' '):
                                    break
                                elif i[pos] != ' ' and asflag == 0 and pos < len(i):
                                    newtemp += i[pos]
                                    pos += 1
                                elif i[pos] == ' ' and asflag == 0 and pos < len(i):
                                    pos += 1
                                    break
                                elif asflag == 1 and pos < len(i):
                                    temp += i[pos]
                                    pos += 1

                            if newtemp == 'AS' and asflag == 0:
                                asflag = 1
                            elif asflag == 1:
                                break

                    joinorder.append(temp)
                    break

                if readflag == 0 and tempword == 'FROM':
                    readflag = 1

                elif readflag == 0 and tempword == 'JOIN' and i[pos] != '(':
                    readflag = 1

                elif readflag == 0 and tempword == 'JOIN' and i[pos] == '(':
                    continue

                elif readflag == 0 and tempword in ['SqlTableCalculator:', 'SqlTableCalculator']:
                    readflag = 1

                else:
                    continue

        return joinorder

    def joindict(self, sql, joinorder):
        joins = SectionStrip.stripjoins(SectionStrip, sql)
        joindict = {}

        index = 0
        for i in joinorder:
            joindict[i] = joins[index]
            index += 1

        return joindict

    def wherelist(self, sql):
        where = SectionStrip.stripwhere(SectionStrip, sql)

        # Check to see if the WHERE clause has any length. If not, return an empty list. -------------------------------------
        if len(where) != 0:

            # Remove the WHERE keyword from the beginning
            where = where[6::]

            # Remove the outermost parentheses
            if where[0] and where[1] == '(':
                where = Formatting.parensubstring(Formatting, where, 1)

            # Cycle through the string, word by word, stopping at any AND / OR / NOT that is not whithin parentheses, or the end of line.
            wherefinal = []
            pos = 0
            parencount = 0
            tempfull = ''
            while True:
                temp = ''

                while True:

                    if pos >= len(where):
                        break
                    elif where[pos] == ' ':
                        temp += where[pos]
                        pos += 1
                        break
                    elif where[pos] == '(':
                        parencount += 1
                        temp += where[pos]
                        pos += 1
                    elif where[pos] == ')':
                        parencount -= 1
                        temp += where[pos]
                        pos += 1
                    else:
                        temp += where[pos]
                        pos += 1

                if pos >= len(where):
                    tempfull += temp
                    wherefinal.append(tempfull)
                    break
                if temp in ['AND ', 'OR ', 'NOT '] and parencount == 0:
                    wherefinal.append(tempfull)
                    # wherefinal.append(temp)
                    tempfull = ''
                else:
                    tempfull += temp
            return wherefinal

        else:
            wherefinal = []
            return wherefinal
        # ---------------------------------------------------------------------------------------------------------------

    def whereand(self, sql):
        where = SectionStrip.stripwhere(SectionStrip, sql)

        # Also a check on whether the WHERE even exists. ------------------------------------------------------------------
        if len(where) != 0:

            # Remove the WHERE keyword from the beginning
            where = where[6::]

            # Remove the outermost parentheses
            if where[0] and where[1] == '(':
                where = Formatting.parensubstring(Formatting, where, 1)

            # Cycle through the string, word by word, stopping at any AND / OR / NOT that is not whithin parentheses, or the end of line.
            wherefinal = {}
            pos = 0
            parencount = 0
            tempfull = ''
            key = 'start'
            while True:
                temp = ''

                while True:

                    if pos >= len(where):
                        break
                    elif where[pos] == ' ':
                        temp += where[pos]
                        pos += 1
                        break
                    elif where[pos] == '(':
                        parencount += 1
                        temp += where[pos]
                        pos += 1
                    elif where[pos] == ')':
                        parencount -= 1
                        temp += where[pos]
                        pos += 1
                    else:
                        temp += where[pos]
                        pos += 1

                if pos >= len(where):
                    tempfull += temp
                    wherefinal[tempfull] = key
                    break
                if temp in ['AND ', 'OR ', 'NOT '] and parencount == 0:
                    wherefinal[tempfull] = key
                    tempfull = ''
                    key = temp
                else:
                    tempfull += temp
            return wherefinal

        else:
            wherefinal = {}
            return wherefinal

        # ---------------------------------------------------------------------------------------------------------------

class Reconstruction:

    def selectreconstruct(self, aggorder, aggdict, joinorder, table, restrictlevel):

        table = Other.formatfunction(Other, table)
        # Begin writing the final query based on the input from the user
        queryfinal = 'SELECT'

        if restrictlevel > 0:
            queryfinal += ' \'Step ' + str(len(joinorder)) + Other.alphanumupper(Other, int(restrictlevel)) + '\' AS Step, '
        else:
            queryfinal += ' \'Step ' + str(len(joinorder)) + '\' AS Step, '

        for i in aggorder:
            queryfinal += aggdict[i] + ', '

        if restrictlevel > 0:
            queryfinal += '\'' + str(table) + ' (Restriction)\' AS StepInfo '
        else:
            queryfinal += '\'' + str(table) + '\' AS StepInfo '

        return queryfinal

    def joinreconstruct(self, joinorder, joindict):

        # Reconstruct the join structure
        finaljoin = ''

        for i in joinorder:
            finaljoin += joindict[i]

        return finaljoin

    def wherereconstruct(self, wherelist, whereand):

        # Reconstruct the where clause, if it exists. If not, return an empty string.

        if len(wherelist) > 0:
            wherefinal = 'WHERE '

            for i in wherelist:
                if whereand[i] in ['and ', 'AND ']:
                    wherefinal += ' AND ' + i
                elif whereand[i] in ['or ', 'OR ']:
                    wherefinal += ' OR ' + i
                elif whereand[i] in ['not ', 'NOT ']:
                    wherefinal += ' NOT ' + i
                elif whereand[i] == 'start':
                    wherefinal += i
            return wherefinal

        else:
            wherefinal = ''
            return wherefinal

    def recombine(self, joinorder, aggorder, wherelist, aggdict, joindict, whereand, restrict):
        finalquery = ''
        joinprog = []
        whereprog = []
        joinpos = 0
        wherepos = 0

        joinprog.append(joinorder[joinpos])
        while True:

            restrictlevel = 0
            skipflag = 0
            initrestrictlevel = 0
            currentrestrict = []
            for i in restrict:
                if joinprog[joinpos] in i:
                    restrictlevel += 1
                    initrestrictlevel += 1
                    skipflag = 1
                    currentrestrict.append(i)

            while restrictlevel >= 0:

                for j in range(20):
                    for i in wherelist:

                        # Check if there is more than one table in the predicate. If so, check whether more than one element is already present in joinprog. If so, append.
                        if Formatting.multitablewherecheck(Formatting, joinorder, i) and i not in restrict == True:
                            if Formatting.singlemultiwhereelementcheck(Formatting, joinprog[joinpos], i, joinprog) == True:
                                whereprog.append(i)
                                wherelist.remove(i)

                        # Check that there is only one table, and if there is only one, check whether its table is already in joinprog. If so, append.
                        elif Formatting.singletablewherecheck(Formatting, joinprog[joinpos], i) == True and Formatting.multitablewherecheck(Formatting, joinorder, i) == False and i not in restrict:
                            whereprog.append(i)
                            wherelist.remove(i)

                if skipflag == 1:
                    pass

                elif len(currentrestrict) > 0:
                    whereprog.append(currentrestrict[0])
                    currentrestrict.remove(currentrestrict[0])

                else:
                    pass

                finalquery += Reconstruction.selectreconstruct(Reconstruction, aggorder, aggdict, joinprog, joinprog[joinpos], initrestrictlevel - restrictlevel) + Reconstruction.joinreconstruct(Reconstruction, joinprog, joindict) + Reconstruction.wherereconstruct(Reconstruction, whereprog, whereand)
                if restrictlevel > 0:
                    finalquery += ' UNION ALL '

                if restrictlevel == 0:
                    joinpos += 1
                restrictlevel -= 1
                skipflag = 0

            if joinpos >= len(joinorder):
                break
            else:
                finalquery += ' UNION ALL '
                joinprog.append(joinorder[joinpos])

        return finalquery