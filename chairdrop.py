import difflib
import variables

class reformat:

    # Find, then return, the positions of the last two UNION ALLs
    def findunions(self, sql, union1, union2):
        pos = 0
        unions = []
        temp = ''

        # Isolate all UNION ALLs------------------------------------------------------
        for i in sql:
            if i not in [' ', '\r', '\n']:
                temp += i
                pos += 1
            elif i in [' ', '\r', '\n']:
                if temp == 'UNION' and sql[pos+1] == 'A' and sql[pos+2] == 'L' and sql[pos+3] == 'L':
                    unions.append(pos-5)
                    pos += 1
                else:
                    temp = ''
                    pos += 1
        # ---------------------------------------------------------------------------
        # Limit to specified unions -------------------------------------------------
        newunions = []

        newunions.append(unions[union1-1])
        newunions.append(unions[union2-1])
        # ---------------------------------------------------------------------------
        return newunions

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
                if j in [' ', '\n', '\r'] and tempword == 'FROM' and parenpos == 0:
                    break
                elif j in [' ', '\n', '\r'] and tempword != 'FROM':
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
                if j == '\'' and i[pos+1] in [' ', '\n', '\r'] and i[pos+2] == ',' and parenpos == 0:
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

        # Find the point of difference between the two queries -----------------------
        d = difflib.Differ()
        diff = list(d.compare(queries[0], queries[1]))

        temp = ''
        newdiff = []
        plusflag = False

        for i in diff:
            if i[0] == '+' and plusflag is False:
                plusflag = True
                temp += i[2]
            elif i[0] == '+' and plusflag is True:
                temp += i[2]
            elif i[0] in [' ', '-'] and plusflag is True:
                newdiff.append(temp)
                temp = ''
                plusflag = False
            else:
                pass
        # ------------------------------------------------------------------------------
        # Identify which difference is the one we want ---------------------------------
        join = ''

        for i in newdiff:
            if 'JOIN' in i and 'ON' in i:
                join = i
        # ------------------------------------------------------------------------------
        # Identify the tables we seek --------------------------------------------------
        table1 = ''
        table2temp = ''
        temp = ''
        tableflag = False
        tempflag = False
        onflag = False

        for i in join:
            if i not in [' ', '\n', '\r']:
                temp += i
            elif i in [' ', '\n', '\r']:
                tempflag = True

            if tempflag is True and tableflag is not True and onflag is not True and temp == 'JOIN':
                tableflag = True
                tempflag = False
                temp = ''

            if tempflag is True and tableflag is True and onflag is not True:
                table1 = temp
                tableflag = False
                tempflag = False
                temp = ''

            if tempflag is True and tableflag is False and onflag is not True and temp == 'ON':
                tempflag = False
                onflag = True
                temp = ''

            if tempflag is True and tableflag is False and onflag is True:
                if len(temp) > 2 and table1 not in temp:
                    table2temp = temp
                    tempflag = False
                    temp = ''
                else:
                    tempflag = False
                    temp = ''

            if tempflag is True and tableflag is not True and onflag is not True and temp not in ['JOIN']:
                tempflag = False
                temp = ''

        # ----------------------------------------------------------------------------------
        # Now clean up table2temp to extract the actual table out of it --------------------
        table2temp = table2temp[::-1]
        table2 = ''
        table2flag = False

        for i in table2temp:
            if i == '.' and table2flag is False:
                table2flag = True
            elif table2flag is True:
                table2 += i
            else:
                pass

        table2 = table2[::-1]
        # -----------------------------------------------------------------------------------
        # Now grab the join predicates ------------------------------------------------------
        # I probably could have combined this with the table parsing, but oh, well
        onflag = False
        temppred = ''
        predlist = []

        for i in join:
            if i not in [' ', '\n', '\r', '(', ')']:
                temp += i
            elif i in ['(', ')']:
                pass
            elif i in [' ', '\n', '\r']:
                tempflag = True

            if tempflag is True and onflag is False and temp == 'ON':
                onflag = True
                temp = ''
                tempflag = False
            elif tempflag is True and onflag is False and temp != 'ON':
                temp = ''
                tempflag = False

            if tempflag is True and onflag is True and temp not in ['AND', 'OR', 'NOT']:
                temppred += temp
                temp = ''
                tempflag = False
            elif tempflag is True and onflag is True and temp in ['AND', 'OR', 'NOT']:
                predlist.append(temppred)
                temppred = ''
                temp = ''
                tempflag = False

        predlist.append(temppred)
        # --------------------------------------------------------------------------------
        # Now associate the predicates with the proper tables ----------------------------
        preddict = {}
        tempdict1 = []
        tempdict2 = []
        temp = ''

        for i in predlist:
            for j in i:
                if j not in ['=', '!=', '<>', '>', '<', '>=', '<=']:
                    temp += j
                elif j in ['=', '!=', '<>', '>', '<', '>=', '<=']:
                    if table1 in temp:
                        tempdict1.append(temp)
                    elif table2 in temp:
                        tempdict2.append(temp)
                    temp = ''
            if table1 in temp:
                tempdict1.append(temp)
            elif table2 in temp:
                tempdict2.append(temp)
            temp = ''

        preddict[table1] = tempdict1
        preddict[table2] = tempdict2
        preddict['B'] = table1
        preddict['A'] = table2
        # --------------------------------------------------------------------------------------
        return preddict

    # Alter the interior of the A and B subqueries to accomodate the new dimensions
    def changeab(self, queries, preddict):
        table1 = preddict['B']
        table2 = preddict['A']
        table1preds = preddict[table1]
        table2preds = preddict[table2]

        newqueries = []
        tempquery = ''
        temp = ''
        tempflag = False
        selectflag = False
        predflag = False
        pred = 0

        for i in queries:
            for j in i:
                if j not in [' ', '\r', '\n'] and selectflag is False and predflag is False:
                    temp += j
                elif j in [' ', '\r', '\n'] and selectflag is False and predflag is False:
                    tempflag = True

                if temp == 'SELECT' and tempflag is True and selectflag is False and predflag is False:
                    tempquery += temp
                    selectflag = True
                    temp = ''
                    tempflag = False
                elif temp != 'SELECT' and tempflag is True and selectflag is False and predflag is False:
                    tempquery += temp
                    temp = ''
                    tempflag = False

                if selectflag is True and predflag is False:
                    if pred == 0:
                        for k in table2preds:
                            tempquery += ' ' + k + ', '
                            predflag = True
                    elif pred == 1:
                        for k in table1preds:
                            tempquery += ' ' + k + ', '
                            predflag = True

                if selectflag is True and predflag is True:
                    tempquery += j

            if pred == 0:
                tempquery += ' GROUP BY '
                for k in table2preds:
                    tempquery += ' ' + k + ', '
            elif pred == 1:
                tempquery += ' GROUP BY '
                for k in table1preds:
                    tempquery += ' ' + k + ', '

            tempquery = tempquery[:-2:]

            pred += 1
            predflag = False
            selectflag = False
            newqueries.append(tempquery)
            tempquery = ''

        return newqueries

    # Combine the queries to the final format
    def combinequeries(self, queries, preddict):
        finalquery = ''
        table1 = preddict['B']
        table2 = preddict['A']
        table1preds = preddict[table1]
        table2preds = preddict[table2]

        # Begin the process with the first few lines -------------------------------------------
        finalquery += 'SELECT \'Drops\' AS Info, * FROM ('
        finalquery += queries[0]
        finalquery += ') AS A LEFT JOIN ('
        finalquery += queries[1]
        finalquery += ') AS B ON '
        # --------------------------------------------------------------------------------------
        # Add in the join predicates -----------------------------------------------------------
        pred = 0

        while pred < len(table1preds):
            if pred != 0:
                finalquery += ' AND '

            finalquery += table2preds[pred].replace(table2, 'A')
            finalquery += ' = '
            finalquery += table1preds[pred].replace(table1, 'B')

            pred += 1
        # --------------------------------------------------------------------------------------
        # Add in the WHERE clause --------------------------------------------------------------
        pred = 0

        finalquery += ' WHERE '
        while pred < len(table1preds):
            if pred != 0:
                finalquery += ' AND '

            finalquery += table1preds[pred].replace(table1, 'B')
            finalquery += ' IS NULL'

            pred += 1

        # Check for comparisons -----------------------------------------------------------------
        if len(variables.dropcomparison) != 0:
            for k in variables.dropcomparison:
                pass
        return finalquery


class DropCheck:

    def checkfordrop(self, results):

        # Reassign to a list format for easier comparison --------------------------------------------
        tempsteps = []
        temp = []
        length = 0

        for i in results:
            length = 0
            for j in i:
                temp.append(j)
                length += 1
            tempsteps.append(temp)
            temp = []
        # --------------------------------------------------------------------------------------------
        # Now compare the individual steps and find which ones have drops ----------------------------
        drops = []
        curstep = 0
        curmetric = 1

        while True:
            if curstep + 1 >= len(tempsteps):
                break

            if tempsteps[curstep][curmetric] - tempsteps[curstep+1][curmetric] > 10.0 and 'Restriction' not in tempsteps[curstep+1][length-1]:
                drops.append([curstep, curstep+1])
                curstep += 1
                curmetric = 1
            elif curmetric < length - 2:
                curmetric += 1
            else:
                curmetric = 1
                curstep += 1

        # --------------------------------------------------------------------------------------------
        return drops
