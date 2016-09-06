from restcall import REST

class BuildList:
    def refresh(self):
        REST.getcookie(REST)
        REST.authentify(REST)
        REST.getUser(REST)
        doclistxml = REST.list("visualDocIndex?ExcludeSiblings=true&VisualdocStatus=NotModifiable")

        doclist = open('doclist.txt', 'w')

        doclist.write(str(doclistxml))
        doclist.close()
