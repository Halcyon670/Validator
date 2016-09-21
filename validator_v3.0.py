import tkinter
import xml.etree.ElementTree as ET
from restcall import REST
import reformat
import json
import database
import pypyodbc
import variables
from other import Other
from xlsx import xlsxsheet
import xlsxwriter

class ValidationMain(tkinter.Tk):

    # Initialize the frames on startup
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand="true")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, DocList, Confirmation):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

    # Automatically go to the first frame on startup
        self.show_frame(StartPage)

    # Define show_frame: this takes frames and moves them to the front.
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tkinter.Frame):

    # Initialize the starting frame
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        controller.minsize(width=1100, height=700)
        label = tkinter.Label(self, text='Validator\n', font='bold')
        label.grid(column=1, row=0, pady=10, padx=10)

        changelog = tkinter.Label(self, font=('Times New Roman', 12), text='Current Release: v3.0\n\nThis is a complete overhaul of the original validator. The purpose of this one is to connect directly to the database and automate the entire process.\n\nAny issues, ideas, death threats, etc. can be sent to cory.clanin@vizexplorer.com', relief='ridge', width=110, height=25)
        changelog.grid(column=1, row=1, sticky='ew', padx=50)

        singleval = tkinter.Button(self, text="Begin!", pady=10, padx=10, fg="black", command=lambda: controller.show_frame(DocList))
        singleval.grid(column=1, row=2, pady=10, padx=473, sticky='w')

        quitapp = tkinter.Button(self, text="Quit", fg="black", pady=10, padx=10, command=lambda: exit())
        quitapp.grid(column=1, row=3, pady=10, padx=10)

        settings = tkinter.Button(self, text="Settings", fg="black", pady=10, padx=10)
        settings.grid(column=1, row=2, pady=10, sticky='e', padx=473)


class DocList(tkinter.Frame):

    moveint = 0

    # Generate a list of documents via a REST call.
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        label = tkinter.Label(self, text='Here\'s your document list:\n\n', font='bold')
        label.grid(row=0, column=2, sticky='w')

        DocList.text = tkinter.StringVar()

        valbutton = tkinter.Button(self, text="Validate!", pady=10, padx=10, fg="black", command=lambda: self.validate(controller))
        valbutton.grid(row=1, column=3, padx=50, sticky='n', pady=240)

        refbutton = tkinter.Button(self, text="Refresh!", fg="black", pady=10, padx=10, command=lambda: self.refresh())
        refbutton.grid(row=1, column=3, padx=30, sticky='s', pady=232)

        rightbutton = tkinter.Button(self, text='>', fg='black', pady=10, padx=10, command=lambda: self.moveright())
        rightbutton.grid(row=1, column=1, sticky='n', pady=150, padx=5)

        leftbutton = tkinter.Button(self, text='<', fg='black', pady=10, padx=10, command=lambda: self.moveleft())
        leftbutton.grid(row=1, column=1, sticky='n', pady=200, padx=5)

        scrolly = tkinter.Scrollbar(self)
        scrolly.grid(row=1, column=0, sticky='nse')
        scrollx = tkinter.Scrollbar(self, orient='horizontal')
        scrollx.grid(row=2, column=0, sticky='new', padx=10)

        DocList.listbox = tkinter.Listbox(self, height=35, width=70, yscrollcommand=scrolly.set, xscrollcommand=scrollx.set, selectmode='single')
        DocList.listbox.grid(row=1, column=0, padx=10)

        doclabel = tkinter.Label(self, textvariable=DocList.text, bd=4, relief='groove', width=60, height=15)
        doclabel.grid(row=1, column=2, padx=10, sticky='s')

        DocList.addeddoclistbox = tkinter.Listbox(self, height=20, width=70, selectmode='single')
        DocList.addeddoclistbox.grid(row=1, column=2, sticky='n')

        scrolly.config(command=DocList.listbox.yview)
        scrollx.config(command=DocList.listbox.xview)

        DocList.populate(self)
        DocList.listbox.bind('<<ListboxSelect>>', self.updatedoclabel)

    # Populates the listboxes from docxml.xml. DocList.listbox must be empty for this to work properly.
    def populate(self):
        file = open('docxml.xml', 'r')
        doclist = ''
        for i in file:
            doclist += i
        file.close()

        root = ET.fromstring(doclist)

        docsraw = root.findall('./VisualDocInfo')
        for i in docsraw:
            variables.docids.append(i.find('./ID').text)
            variables.docnames[i.find('./ID').text] = i.find('./Name').text
            variables.doclastmodified[i.find('./ID').text] = i.find('./LastModified').text
            variables.docstartdate[i.find('./ID').text] = i.find('./StartDate').text
            variables.docenddate[i.find('./ID').text] = i.find('./EndDate').text
            variables.docdescription[i.find('./ID').text] = i.find('./Description').text
            variables.doctag[i.find('./ID').text] = i.find('./Tag').text

        DocList.docnames = variables.docnames

        index = 1
        for i in variables.docids:
            DocList.listbox.insert(index, variables.docnames[i])
            index += 1

    # Displays doc information on the doclabel. This only does this one at a time, and is set to a trigger for clicking on a doc.
    def updatedoclabel(self, event):

        temp = ''
        for i in DocList.listbox.curselection():
            temp += 'Doc: ' + str(variables.docnames[variables.docids[i]]) + '\nDescription: ' + str(variables.docdescription[variables.docids[i]]) + '\nTag: ' + str(variables.doctag[variables.docids[i]]) + '\nStartDate: ' + str(variables.docstartdate[variables.docids[i]]) + '\nEndDate: ' + str(variables.docenddate[variables.docids[i]]) + '\nLast Modified: ' + str(variables.doclastmodified[variables.docids[i]]) + '\n\n'

        DocList.text.set(temp)

    # Moves documents from listbox to addeddoclist. Tied to a button.
    def moveright(self):
        if DocList.listbox.curselection() is not None:
            movevar = 0

            for i in DocList.listbox.curselection():
                movevar = int(i)

            variables.valdocs.append(variables.docids[movevar])
            DocList.addeddoclistbox.insert(DocList.moveint, DocList.listbox.get(movevar))
            DocList.listbox.itemconfig(movevar, {'bg': 'grey'})
            DocList.moveint += 1

    # Moves documents from addeddoclist to listbox. Tied to a button.
    def moveleft(self):
        if DocList.addeddoclistbox.curselection() is not None:
            movevar = 0

            for i in DocList.addeddoclistbox.curselection():
                movevar = int(i)

            DocList.addeddoclistbox.delete(movevar)
            DocList.listbox.itemconfig(variables.docids.index(variables.valdocs[movevar]), {'bg': 'white'})
            variables.valdocs.remove(variables.valdocs[movevar])

    # Refreshes docxml, then repopulates.
    def refresh(self):
        REST.getcookie(REST)
        REST.authentify(REST)
        REST.getUser(REST)
        doclistxml = REST.list("visualDocIndex?ExcludeSiblings=true&VisualdocStatus=NotModifiable")

        doclistxml = str(doclistxml)
        doclistxml = doclistxml[:-1]
        doclistxml = doclistxml[40:]

        doclist = open('docxml.xml', 'w')

        doclist.write(str(doclistxml))
        doclist.close()

        DocList.valdocs = []

        DocList.listbox.delete(0, 10000)
        DocList.addeddoclistbox.delete(0, 10000)

        DocList.populate(self)

        DocList.moveint = 0

    def validate(self, controller):

        REST.getcookie(REST)
        REST.authentify(REST)
        REST.getUser(REST)

        file = open('docxml.xml', 'r')
        doclist = ''
        for i in file:
            doclist += i
        file.close()

        root = ET.fromstring(doclist)

        docsraw = root.findall('./VisualDocInfo')
        for i in docsraw:
            variables.datasetids[i.find('./ID').text] = i.find('./DataSetID').text

        for i in variables.valdocs:
            variables.docjson[i] = REST.list("dataSetMeta/" + str(variables.datasetids[i]) + '.json?visualDocId=' + str(i))

        for i in variables.valdocs:
            temp = ''
            temp = str(variables.docjson[i])
            temp = temp[2:]
            temp = temp[:-1]
            tempquery = ''

            parsed_json = json.loads(temp.replace('\\\'', '\''))

            tempquery = Other.removedash(Other, parsed_json['DataSet']['QueryPlan'])
            tempquery = Other.removedash(Other, tempquery)

            variables.docqueries[i] = tempquery

        # Confirmation.valdocs = variables.valdocs
        for i in variables.valdocs:
            Confirmation.valdocs.append(i)
        Confirmation.docqueries = variables.docqueries
        Confirmation.docnames = variables.docnames

        Confirmation.populate(Confirmation, Confirmation.valdocs, Confirmation.docqueries)

        controller.show_frame(Confirmation)


class Confirmation(tkinter.Frame):

    valdocs = []
    docqueries = {}
    docaggs = []
    docaggdict = {}
    docrestrict = {}
    docjoins = []
    docjoindict = {}
    docwhere = []
    docnames = {}

    # Initialize the starting frame
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        controller.minsize(width=1100, height=700)

        Confirmation.docname = tkinter.StringVar()

        doclabel = tkinter.Label(self, textvariable=Confirmation.docname, relief='groove', width=20, height=1)
        doclabel.grid(column=0, row=0, sticky='nesw', pady=5, padx=5, columnspan=3)

        metriclabel = tkinter.Label(self, text='\nPlease choose your metrics:')
        metriclabel.grid(column=0,row=1)

        metricscrolly = tkinter.Scrollbar(self)
        metricscrolly.grid(column=0, row=2, sticky='ens')
        metricscrollx = tkinter.Scrollbar(self, orient='horizontal')
        metricscrollx.grid(column=0, row=3, sticky='new', padx=10)
        restrictscrolly = tkinter.Scrollbar(self)
        restrictscrolly.grid(column=1, row=2, sticky='ens')
        restrictscrollx = tkinter.Scrollbar(self, orient='horizontal')
        restrictscrollx.grid(column=1, row=3, sticky='new', padx=10)

        Confirmation.metriclistbox = tkinter.Listbox(self, height=37, width=70, selectmode='multiple', yscrollcommand=metricscrolly.set, xscrollcommand=metricscrollx.set, exportselection=0)
        Confirmation.metriclistbox.grid(column=0, row=2, padx=10, sticky='n')

        restrictlabel = tkinter.Label(self, text='\nPlease choose your restrictions:')
        restrictlabel.grid(column=1, row=1)

        Confirmation.restrictlistbox = tkinter.Listbox(self, height=37, width=70, selectmode='multiple', yscrollcommand=restrictscrolly.set, xscrollcommand=restrictscrollx.set, exportselection=0)
        Confirmation.restrictlistbox.grid(column=1, row=2, padx=10, sticky='n')

        continuebutton = tkinter.Button(self, text='Continue', command=lambda: self.cont())
        continuebutton.grid(column=2, row=2, padx=80, ipadx=10, ipady=10)

    def populate(self, valdocs, docqueries):

        # Check to see if we are at the end of the list. If we are, move on to the next piece.
        if len(valdocs) > 0 is not None:
            Confirmation.docaggs = reformat.Isolation.aggorder(reformat, docqueries[valdocs[0]])
            Confirmation.docaggdict = reformat.Isolation.aggdict(reformat, docqueries[valdocs[0]], Confirmation.docaggs)
            Confirmation.docjoins = reformat.Isolation.joinorder(reformat, docqueries[valdocs[0]])
            Confirmation.docjoindict = reformat.Isolation.joindict(reformat, docqueries[valdocs[0]], Confirmation.docjoins)
            Confirmation.docwhere = reformat.Isolation.wherelist(reformat, docqueries[valdocs[0]])
            Confirmation.docwhereand = reformat.Isolation.whereand(reformat, docqueries[valdocs[0]])

            for i in Confirmation.docaggs:
                Confirmation.metriclistbox.insert(Confirmation.docaggs.index(i), i)

            for i in Confirmation.docwhere:
                Confirmation.restrictlistbox.insert(Confirmation.docwhere.index(i), i)

            Confirmation.docname.set(Confirmation.docnames[valdocs[0]])

        else:
            docresults = {}
            temp = ''
            for i in variables.valdocs:
                try:
                    print(variables.docqueries[i])
                    print(variables.finalqueries[i])
                    temp = database.Query.runquery(Confirmation, variables.finalqueries[i])
                    docresults[i] = temp
                    temp = ''
                except pypyodbc.ProgrammingError:
                    variables.valdocs.remove(i)
                    print('Error!')

            workbook = xlsxwriter.Workbook('DV_20160921.xlsx')

            for i in variables.valdocs:
                xlsxsheet.addsheet(xlsxsheet, workbook, variables.docnames[i], 'http://app5.internal.bis2.net/index.html?id=' + str(i), str(variables.docstartdate[i]) + ' - ' + str(variables.docenddate[i]), variables.doclastmodified[i], variables.docaggs[i], docresults[i], [], variables.finalqueries[i])


    def cont(self):

        useragglist = []
        userrestrictlist = []

        for i in Confirmation.metriclistbox.curselection():
            useragglist.append(Confirmation.metriclistbox.get(i))

        for i in Confirmation.restrictlistbox.curselection():
            userrestrictlist.append(Confirmation.restrictlistbox.get(i))

        variables.finalqueries[Confirmation.valdocs[0]] = reformat.Reconstruction.recombine(reformat, Confirmation.docjoins, useragglist, Confirmation.docwhere, Confirmation.docaggdict, Confirmation.docjoindict, Confirmation.docwhereand, userrestrictlist)
        variables.docaggs[Confirmation.valdocs[0]] = useragglist

        Confirmation.docaggs = []
        Confirmation.docaggdict = {}
        Confirmation.docjoins = []
        Confirmation.docjoindict = {}
        Confirmation.docwhere = []
        Confirmation.docwhereand = {}
        Confirmation.valdocs.remove(Confirmation.valdocs[0])

        Confirmation.populate(Confirmation, Confirmation.valdocs, Confirmation.docqueries)


# Run the program
app = ValidationMain()
app.mainloop()
