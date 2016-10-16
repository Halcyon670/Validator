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
from datetime import datetime
from log import Log
import webbrowser
import time

class ValidationMain(tkinter.Tk):

    # Initialize the frames on startup
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        container = tkinter.Frame(self)
        container.pack(side="top", fill="both", expand="true")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, DocList, Confirmation, Settings, RunFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        # Automatically go to the first frame on startup
        self.show_frame(StartPage)

        # Clear the log file
        file = open('log.txt', 'w')
        file.write('')
        file.close()

        Log.writetolog(Log, 'Successfully purged prior log and started a new one.')

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

        changelog = tkinter.Label(self, font=('Times New Roman', 12), text='Current Release: v3.0\n\nThis is a complete overhaul of the original validator. The purpose of this one is to connect directly to the database and automate the entire process.\n\nAny issues, ideas, etc. can be sent to cory.clanin@vizexplorer.com', relief='ridge', width=110, height=25)
        changelog.grid(column=1, row=1, sticky='ew', padx=50)

        singleval = tkinter.Button(self, text="Begin!", pady=10, padx=10, fg="black", command=lambda: controller.show_frame(DocList))
        singleval.grid(column=1, row=2, pady=10, padx=473, sticky='w')

        quitapp = tkinter.Button(self, text="Quit", fg="black", pady=10, padx=10, command=lambda: exit())
        quitapp.grid(column=1, row=3, pady=10, padx=10)

        settings = tkinter.Button(self, text="Settings", fg="black", pady=10, padx=10, command=lambda: self.showsettings(controller))
        settings.grid(column=1, row=2, pady=10, sticky='e', padx=473)

    def showsettings(self, controller):

        Settings.urltext.delete(1.0, tkinter.END)
        Settings.urlusertext.delete(1.0, tkinter.END)
        Settings.urlpasstext.delete(1.0, tkinter.END)
        Settings.databasedrivertext.delete(1.0, tkinter.END)
        Settings.databaseservertext.delete(1.0, tkinter.END)
        Settings.databasedbtext.delete(1.0, tkinter.END)
        Settings.databaseusertext.delete(1.0, tkinter.END)
        Settings.databasepasstext.delete(1.0, tkinter.END)
        Settings.startingjointext.delete(1.0, tkinter.END)
        Settings.endingjointext.delete(1.0, tkinter.END)
        config = ''
        file = open('config.xml', 'r')
        for i in file:
            config += i
        file.close()

        root = ET.fromstring(config)

        url = root.find('./URLSettings/URL').text
        urluser = root.find('./URLSettings/URLuser').text
        urlpass = root.find('./URLSettings/URLpass').text
        dbdriver = root.find('./DatabaseSettings/Driver').text
        dbserver = root.find('./DatabaseSettings/Server').text
        dbdatabase = root.find('./DatabaseSettings/Database').text
        dbuser = root.find('./DatabaseSettings/User').text
        dbpassword = root.find('./DatabaseSettings/Password').text
        startingjoins = root.find('./AdvancedSettings/StartingJoins').text
        endingjoins = root.find('./AdvancedSettings/EndingJoins').text

        Settings.urltext.insert(tkinter.END, url)
        Settings.urlusertext.insert(tkinter.END, urluser)
        Settings.urlpasstext.insert(tkinter.END, urlpass)
        Settings.databasedrivertext.insert(tkinter.END, dbdriver)
        Settings.databaseservertext.insert(tkinter.END, dbserver)
        Settings.databasedbtext.insert(tkinter.END, dbdatabase)
        Settings.databaseusertext.insert(tkinter.END, dbuser)
        Settings.databasepasstext.insert(tkinter.END, dbpassword)
        Settings.startingjointext.insert(tkinter.END, startingjoins)
        Settings.endingjointext.insert(tkinter.END, endingjoins)

        controller.show_frame(Settings)


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
        DocList.listbox.delete(0, 10000)

        file = open('docxml.xml', 'r')
        doclist = ''
        for i in file:
            doclist += i
        file.close()

        root = ET.fromstring(doclist)

        docsraw = root.findall('./VisualDocInfo')
        for i in docsraw:
            temptag = ''
            tempdesc = ''
            variables.docids.append(i.find('./ID').text)
            variables.docnames[i.find('./ID').text] = i.find('./Name').text
            variables.doclastmodified[i.find('./ID').text] = datetime.strptime(i.find('./LastModified').text[:-3], '%Y%m%d%H%M%S')
            variables.docstartdate[i.find('./ID').text] = datetime.strptime(i.find('./StartDate').text[:-3], '%Y%m%d%H%M%S')
            variables.docenddate[i.find('./ID').text] = datetime.strptime(i.find('./EndDate').text[:-3], '%Y%m%d%H%M%S')
            tempdesc = i.find('./Description').text
            if tempdesc is None:
                variables.docdescription[i.find('./ID').text] = ''
            else:
                variables.docdescription[i.find('./ID').text] = tempdesc.replace('\\\\', '\\')
            temptag = i.find('./Tag').text
            if temptag is None:
                variables.doctag[i.find('./ID').text] = ''
            else:
                variables.doctag[i.find('./ID').text] = temptag.replace('\\\\', '\\')

        # Sort the list in descending order by LastModified
        variables.docids = Other.sortlist(Other, variables.docids, variables.doclastmodified)

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

        Log.writetolog(Log, 'Moving forward with the following docs: ' + str(variables.valdocs))

        Confirmation.populate(Confirmation, Confirmation.valdocs, Confirmation.docqueries, controller)

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

        continuebutton = tkinter.Button(self, text='Continue', command=lambda: self.cont(controller))
        continuebutton.grid(column=2, row=2, padx=80, ipadx=10, ipady=10)

    def populate(self, valdocs, docqueries, controller):

        # Clear the listboxes before moving on
        Confirmation.metriclistbox.delete(0, 100000)
        Confirmation.restrictlistbox.delete(0, 10000)
        removeddocs = []

        # Check to see if we are at the end of the list. If we are, move on to the next piece.
        if len(valdocs) > 0 is not None:
            Log.writetolog(Log, 'Remaining docs: ' + str(valdocs))
            Confirmation.docaggs = reformat.Isolation.aggorder(reformat, docqueries[valdocs[0]])
            Confirmation.docaggdict = reformat.Isolation.aggdict(reformat, docqueries[valdocs[0]], Confirmation.docaggs)
            Confirmation.docjoins = reformat.Isolation.joinorder(reformat, docqueries[valdocs[0]])
            Confirmation.docjoindict = reformat.Isolation.joindict(reformat, docqueries[valdocs[0]], Confirmation.docjoins)
            Confirmation.docwhere = reformat.Isolation.wherelist(reformat, docqueries[valdocs[0]])
            Confirmation.docwhereand = reformat.Isolation.whereand(reformat, docqueries[valdocs[0]])

            # Move the specified joins to their proper places
            root=ET.parse('config.xml')
            startjoins = root.find('./AdvancedSettings/StartingJoins').text
            endjoins = root.find('./AdvancedSettings/EndingJoins').text
            startjoinlist = []
            endjoinlist = []
            temp = ''

            for i in startjoins:
                if i != ',':
                    temp += i
                else:
                    startjoinlist.append(temp)
                    temp = ''
            startjoinlist.append(temp)
            temp = ''

            for i in endjoins:
                if i != ',':
                    temp += i
                else:
                    endjoinlist.append(temp)
                    temp = ''
            endjoinlist.append(temp)
            temp = ''

            for i in Confirmation.docjoins:
                if i in endjoinlist:
                    Confirmation.docjoins.remove(i)
                    Confirmation.docjoins.append(i)

                elif i in startjoinlist:
                    Confirmation.docjoins.insert(1, Confirmation.docjoins.pop(Confirmation.docjoins.index(i)))

            Log.writetolog(Log, 'Checking ' + str(valdocs[0]) + ' (' + str(variables.docnames[valdocs[0]]) + '):' + '\n\tQuery: ' + str(variables.docqueries[valdocs[0]]) + '\n\tDocAggs: ' + str(Confirmation.docaggs) + '\n\tDocAggDict: ' + str(Confirmation.docaggdict) + '\n\tDocJoins: ' + str(Confirmation.docjoins) + '\n\tDocJoinDict: ' + str(Confirmation.docjoindict) + '\n\tDocWhere: ' + str(Confirmation.docwhere) + '\n\tDocWhereAnd: ' + str(Confirmation.docwhereand))

            for i in Confirmation.docaggs:
                Confirmation.metriclistbox.insert(Confirmation.docaggs.index(i), i)

            for i in Confirmation.docwhere:
                Confirmation.restrictlistbox.insert(Confirmation.docwhere.index(i), i)

            Confirmation.docname.set(Confirmation.docnames[valdocs[0]])

        else:
            variables.removeddocs = removeddocs
            controller.show_frame(RunFrame)

    def cont(self, controller):

        useragglist = []
        userrestrictlist = []

        for i in Confirmation.metriclistbox.curselection():
            useragglist.append(Confirmation.metriclistbox.get(i))

        for i in Confirmation.restrictlistbox.curselection():
            userrestrictlist.append(Confirmation.restrictlistbox.get(i))

        variables.finalqueries[Confirmation.valdocs[0]] = reformat.Reconstruction.recombine(reformat, Confirmation.docjoins, useragglist, Confirmation.docwhere, Confirmation.docaggdict, Confirmation.docjoindict, Confirmation.docwhereand, userrestrictlist)
        Log.writetolog(Log, 'Final data about ' + str(Confirmation.valdocs[0]) + ':' + '\n\tUserAggList: ' + str(useragglist) + '\n\tUserRestrictList: ' + str(userrestrictlist) + '\n\tFinalQuery: ' + str(variables.finalqueries[Confirmation.valdocs[0]]))
        variables.docaggs[Confirmation.valdocs[0]] = useragglist

        Confirmation.docaggs = []
        Confirmation.docaggdict = {}
        Confirmation.docjoins = []
        Confirmation.docjoindict = {}
        Confirmation.docwhere = []
        Confirmation.docwhereand = {}
        Confirmation.valdocs.remove(Confirmation.valdocs[0])

        Confirmation.populate(Confirmation, Confirmation.valdocs, Confirmation.docqueries, controller)


class Settings(tkinter.Frame):

    # Initialize the starting frame
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        controller.minsize(width=1100, height=700)

        settingslabel = tkinter.Label(self, text='Settings:\n\n', font='bold')
        settingslabel.grid(row=0, column=1)

        # URL Settings
        urlsettingslabel = tkinter.Label(self, text='URL Info:\n')
        urlsettingslabel.grid(row=1, column=0)

        urllabel = tkinter.Label(self, text='URL:')
        urllabel.grid(row=2, column=0, sticky='w', padx=30)

        Settings.urltext = tkinter.Text(self, height=1, width=35)
        Settings.urltext.grid(row=3, column=0, padx=30)

        urluserlabel = tkinter.Label(self, text='\nUsername:')
        urluserlabel.grid(row=4, column=0, sticky='w', padx=30)

        Settings.urlusertext = tkinter.Text(self, height=1, width=35)
        Settings.urlusertext.grid(row=5, column=0, padx=30)

        urlpasslabel = tkinter.Label(self, text='\nPassword:')
        urlpasslabel.grid(row=6, column=0, sticky='w', padx=30)

        Settings.urlpasstext = tkinter.Text(self, height=1, width=35)
        Settings.urlpasstext.grid(row=7, column=0, padx=30)

        # Database Settings
        databasesettingslabel = tkinter.Label(self, text='Database Info:\n')
        databasesettingslabel.grid(row=1, column=1, padx=70)

        databasedriverlabel = tkinter.Label(self, text='Driver:')
        databasedriverlabel.grid(row=2, column=1, sticky='w', padx=70)

        Settings.databasedrivertext = tkinter.Text(self, height=1, width=35)
        Settings.databasedrivertext.grid(row=3, column=1, padx=70)

        databaseserverlabel = tkinter.Label(self, text='\nServer:')
        databaseserverlabel.grid(row=4, column=1, sticky='w', padx=70)

        Settings.databaseservertext = tkinter.Text(self, height=1, width=35)
        Settings.databaseservertext.grid(row=5, column=1, padx=70)

        databasedblabel = tkinter.Label(self, text='\nDatabase:')
        databasedblabel.grid(row=6, column=1, sticky='w', padx=70)

        Settings.databasedbtext = tkinter.Text(self, height=1, width=35)
        Settings.databasedbtext.grid(row=7, column=1, padx=70)

        databaseuserlabel = tkinter.Label(self, text='\nUserName:')
        databaseuserlabel.grid(row=8, column=1, sticky='w', padx=70)

        Settings.databaseusertext = tkinter.Text(self, height=1, width=35)
        Settings.databaseusertext.grid(row=9, column=1, padx=70)

        databasepasslabel = tkinter.Label(self, text='\nPassword:')
        databasepasslabel.grid(row=10, column=1, sticky='w', padx=70)

        Settings.databasepasstext = tkinter.Text(self, height=1, width=35)
        Settings.databasepasstext.grid(row=11, column=1, padx=70)

        # Advanced Settings
        advancedsettingslabel = tkinter.Label(self, text='Advanced Settings:\n')
        advancedsettingslabel.grid(row=1, column=2, padx=20)

        startingjoinlabel = tkinter.Label(self, text='Starting Joins:')
        startingjoinlabel.grid(row=2, column=2, sticky='w', padx=20)

        Settings.startingjointext = tkinter.Text(self, height=1, width=35)
        Settings.startingjointext.grid(row=3, column=2, padx=20)

        endingjoinlabel = tkinter.Label(self, text='Ending Joins:')
        endingjoinlabel.grid(row=4, column=2, sticky='w', padx=20)

        Settings.endingjointext = tkinter.Text(self, height=1, width=35)
        Settings.endingjointext.grid(row=5, column=2, padx=2)

        # Other Stuff
        applybutton = tkinter.Button(self, text='Apply', command=lambda: self.applysettings(controller))
        applybutton.grid(row=12, column=2, sticky='s', pady=10)

        cancelbutton = tkinter.Button(self, text='Cancel', command=lambda: controller.show_frame(StartPage))
        cancelbutton.grid(row=13, column=2, sticky='s', pady=10)

    def applysettings(self, controller):

        url = Settings.urltext.get(1.0, tkinter.END)
        urluser = Settings.urlusertext.get(1.0, tkinter.END)
        urlpass = Settings.urlpasstext.get(1.0, tkinter.END)
        dbdriver = Settings.databasedrivertext.get(1.0, tkinter.END)
        dbserver = Settings.databaseservertext.get(1.0, tkinter.END)
        dbdatabase = Settings.databasedbtext.get(1.0, tkinter.END)
        dbuser = Settings.databaseusertext.get(1.0, tkinter.END)
        dbpass = Settings.databasepasstext.get(1.0, tkinter.END)
        startjoins = Settings.startingjointext.get(1.0, tkinter.END)
        endjoins = Settings.endingjointext.get(1.0, tkinter.END)

        # Need to include this. Otherwise it completely ruins the formatting of the document.
        url = url.replace('\n', '')
        urluser = urluser.replace('\n', '')
        urlpass = urlpass.replace('\n', '')
        dbdriver = dbdriver.replace('\n', '')
        dbserver = dbserver.replace('\n', '')
        dbdatabase = dbdatabase.replace('\n', '')
        dbuser = dbuser.replace('\n', '')
        dbpass = dbpass.replace('\n', '')
        startjoins = startjoins.replace('\n', '')
        endjoins = endjoins.replace('\n', '')

        root = ET.parse('config.xml')
        root.find('./URLSettings/URL').text = url
        root.find('./URLSettings/URLuser').text = urluser
        root.find('./URLSettings/URLpass').text = urlpass
        root.find('./DatabaseSettings/Driver').text = dbdriver
        root.find('./DatabaseSettings/Server').text = dbserver
        root.find('./DatabaseSettings/Database').text = dbdatabase
        root.find('./DatabaseSettings/User').text = dbuser
        root.find('./DatabaseSettings/Password').text = dbpass
        root.find('./AdvancedSettings/StartingJoins').text = startjoins
        root.find('./AdvancedSettings/EndingJoins').text = endjoins
        root.write('config.xml')

        controller.show_frame(StartPage)


class RunFrame(tkinter.Frame):

    # Create a frame that will take note of progress as the tool runs.
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        controller.minsize(width=1100, height=700)

        # These room labels are to help with the gridding. They are not visible.-----------------------------------------------
        roomlabel1=tkinter.Label(self, width=30, height=18)
        roomlabel1.grid(row=0, column=0)

        roomlabel2=tkinter.Label(self, width=10, height=3)
        roomlabel2.grid(row=1, column=0)

        roomlabel3=tkinter.Label(self, width=10, height=3)
        roomlabel3.grid(row=2, column=0)

        roomlabel4=tkinter.Label(self, width=10, height=3)
        roomlabel4.grid(row=3, column=0)

        roomlabel5=tkinter.Label(self, width=10, height=10)
        roomlabel5.grid(row=4, column=0)
        # ----------------------------------------------------------------------------------------------------------------------

        RunFrame.progress1 = tkinter.StringVar()
        RunFrame.progress2 = tkinter.StringVar()

        RunFrame.progresslabel1 = tkinter.Label(self, width=100, textvariable=RunFrame.progress1, relief='groove')
        RunFrame.progresslabel1.grid(row=1, column=1)

        RunFrame.runbutton = tkinter.Button(self, text='Run', command=lambda: self.run(variables.removeddocs))
        RunFrame.runbutton.grid(row=2, column=1, ipadx=10, ipady=10)

        RunFrame.progresslabel2 = tkinter.Label(self, width=100, textvariable=RunFrame.progress2, relief='groove')
        RunFrame.progresslabel2.grid(row=3, column=1)

    def run(self, removeddocs):
        docresults = {}
        temp = ''

        # Remove the Run button-----------------------------
        RunFrame.runbutton.grid_forget()
        # Get the URL --------------------------------------
        file = open('config.xml', 'r')
        config = ''
        for i in file:
            config += i
        file.close()

        root = ET.fromstring(config)

        host = root.find('./URLSettings/URL').text
        # --------------------------------------------------

        for i in variables.valdocs:
            RunFrame.progress1.set('Now working on ' + str(variables.docnames[i]))
            RunFrame.progress2.set('Attempting to run in the database...')
            RunFrame.progresslabel1.update()
            RunFrame.progresslabel2.update()

            Log.writetolog(Log, 'Now attempting to run the query for ' + str(i) + ':')
            try:
                temp = database.Query.runquery(Confirmation, variables.finalqueries[i])
                docresults[i] = temp
                Log.writetolog(Log, 'Query successfully run. Here are the results:\n\t' + str(temp))
                RunFrame.progress2.set('Run Successful.')
                RunFrame.progresslabel2.update()
                time.sleep(3)
                temp = ''
            except pypyodbc.ProgrammingError:
                variables.errorcount += 1
                variables.errordocs.append(i)
                removeddocs.append(i)
                Log.writetolog(Log, 'An error has occurred in this query. Please run the query in SQL Server for more information.')
                RunFrame.progress2.set('Run Unsuccessful. Please see the log for details.')
                RunFrame.progresslabel2.update()
                time.sleep(3)

        for i in removeddocs:
            variables.valdocs.remove(i)

        Log.writetolog(Log, 'Queries completed with ' + str(variables.errorcount) + ' errors.\n\tErrored documents are: ' + str(variables.errordocs) + '.')

        RunFrame.progress1.set('Queries finished. Now setting up xlsx docs...')
        RunFrame.progresslabel1.update()
        RunFrame.progress2.set('')
        RunFrame.progresslabel2.update()
        time.sleep(2)

        workbook = xlsxwriter.Workbook('AutoDV' + str(time.localtime()) + '.xlsx')

        for i in variables.valdocs:
            Log.writetolog(Log, 'Attempting to create the excel sheet for ' + str(variables.docnames[i]))
            RunFrame.progress2.set('Creating doc for ' + str(i))
            RunFrame.progresslabel2.update()
            xlsxsheet.addsheet(xlsxsheet, workbook, variables.docnames[i], host + '/index.html?id=' + str(i), str(variables.docstartdate[i]) + ' - ' + str(variables.docenddate[i]), variables.doclastmodified[i], variables.docaggs[i], docresults[i], [], variables.finalqueries[i])
            webbrowser.open_new_tab(host + '/index.html?id=' + str(i))
            Log.writetolog(Log, 'Excel sheet for ' + str(i) + ' successful.')
            time.sleep(2)

        RunFrame.progress2.set('')
        RunFrame.progresslabel2.update()

        if variables.errorcount == 0:
            RunFrame.progress1.set('Documents completed with no errors.')
            RunFrame.progresslabel1.update()

        else:
            RunFrame.progress1.set('Documents completed with ' + str(variables.errorcount) + ' error(s). Please review the log for details.')
            RunFrame.progresslabel1.update()

# Run the program
app = ValidationMain()
app.mainloop()
