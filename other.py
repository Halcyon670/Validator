
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