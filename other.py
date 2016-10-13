from datetime import datetime

class Other:

    def alphanumupper(self, i):
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        return alphabet[i]

    def removedash(self, query):
        query = query.replace('\\n', ' ')
        query = query.replace('\\t', ' ')
        return query

    def formatfunction(self, table):
        newtable = ''

        for j in table:
            if j == '(':
                break
            else:
                newtable += j

        return newtable

    def sortlist(self, list, dict):
        newlist = []
        tempdict = {}
        temp = datetime.strptime('1970-01-01', '%Y-%m-%d')
        value = ''

        for i in list:
            tempdict[i] = dict[i]

        while len(tempdict) > 0:
            for i in tempdict:
                if tempdict[i] > temp:
                    temp = tempdict[i]
                    value = i
                else:
                    pass
            newlist.append(value)
            del tempdict[value]
            value = ''
            temp = datetime.strptime('1970-01-01', '%Y-%m-%d')

        return newlist
