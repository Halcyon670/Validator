import xlsxwriter
import other
import sqlparse


class xlsxsheet:

    xlsxcount = 0
    dropcount = 1

    def addsheet(self, workbook, name, url, daterange, lastmodified, metricnames, steps, datagrid, sql, image):

        xlsxsheet.xlsxcount += 1

        worksheet = workbook.add_worksheet(str(xlsxsheet.xlsxcount) + '-' + name[:27].replace('[', '').replace(']', '').replace(':', '').replace('*', '').replace('?', '').replace('\\', '').replace('/', ''))

        nameformat = workbook.add_format({'bold': True, 'underline': True, 'font_color': 'blue', 'font_size': 11})
        lastmodifiedformat = workbook.add_format({'font_color': 'purple', 'num_format': 'yyyy-mm-dd hh:mm:ss'})
        metricnameformat = workbook.add_format({'fg_color': '#ddebf7', 'underline': True, 'bold': True, 'border': 1})
        stepformat = workbook.add_format({'fg_color': '#ededed', 'border': 1})
        datagridformat = workbook.add_format({'fg_color': '#e2efda', 'border': 1, 'bold': True})
        interludeformat = workbook.add_format({'underline': True, 'bold': True})
        concatstepformat = workbook.add_format({'fg_color': '#E2EFDA', 'bold': True, 'border': 2})
        subtractcellformat = workbook.add_format({'fg_color': '#FFF2CC', 'border': 2})
        resultsexplanationformat = workbook.add_format({'fg_color': '#B4C6E7', 'bold': True, 'border': 2})
        concatdatagridformat = workbook.add_format({'fg_color': '#C6E0B4', 'bold': True, 'border': 2})
        subtractdatagridformat = workbook.add_format({'fg_color': '#C6E0B4', 'border': 2})
        textboxoption = {'width': 1000, 'height': 20000}

        width = len(metricnames) + 1

        worksheet.set_column(0, width, 20)
        worksheet.set_column(width, width, 40)
        worksheet.write(0, 0, name, nameformat)
        worksheet.write(0, 3, url)
        worksheet.write(1, 0, daterange)
        worksheet.write(1, 3, lastmodified, lastmodifiedformat)

        worksheet.write(2, 0, 'Step', metricnameformat)
        j = 1
        for i in metricnames:
            worksheet.write(2, j, i, metricnameformat)
            j += 1
        worksheet.write(2, j, 'StepInfo', metricnameformat)

        m = 0
        n = 3

        for i in steps:
            for k in i:
                worksheet.write(n, m, k, stepformat)
                m += 1
            n += 1
            m = 0

        worksheet.write(n, m, 'Datagrid', datagridformat)
        m += 1
        for i in datagrid:
            worksheet.write(n, m, i, datagridformat)
            m += 1
        worksheet.write(n, m, 'Datagrid', datagridformat)

        noofrows = n - 3
        noofcolumns = len(metricnames) + 1

        n += 2

        worksheet.write(n, 0, 'Differences', interludeformat)
        worksheet.write(n, noofcolumns, 'Results/Explanation', interludeformat)

        n += 1

        for i in range(noofrows - 1):
            for j in range(noofcolumns + 1):
                if j == 0:
                    worksheet.write(n, j, '=CONCATENATE(A' + str(i + 4) + '," to ",A' + str(i + 5) + ')', concatstepformat)
                elif j == noofcolumns:
                    worksheet.write(n, j, '', resultsexplanationformat)
                else:
                    worksheet.write(n, j, '=' + other.Other.alphanumupper(other, j) + str(i + 5) + '-' + other.Other.alphanumupper(other, j) + str(i + 4), subtractcellformat)
            n += 1
        for j in range(noofcolumns + 1):
                if j == 0:
                    worksheet.write(n, 0, '=CONCATENATE(A' + str(noofrows + 3) + '," to ",A' + str(noofrows + 4) + ')', concatdatagridformat)
                elif j == noofcolumns:
                    worksheet.write(n, j, '', resultsexplanationformat)
                else:
                    worksheet.write(n, j, '=' + other.Other.alphanumupper(other, j) + str(noofrows + 4) + '-' + other.Other.alphanumupper(other, j) + str(noofrows + 3), subtractdatagridformat)

        n += 2

        worksheet.insert_textbox(n, 0, sqlparse.format(sql, reindent=True, keyword_case='upper'), textboxoption)

        if image != '':
            worksheet.insert_image(1, width + 3, image, {'x_scale': 0.25, 'y_scale': 0.25})

    # Drop investigation xlsx sheet
    def adddropinvest(self, workbook, columns, drop, sql, docname, steps):

        worksheet = workbook.add_worksheet('Drop Investigation ' + str(xlsxsheet.dropcount))
        xlsxsheet.dropcount += 1

        stepformat = workbook.add_format({'fg_color': '#ededed', 'border': 1})
        metricnameformat = workbook.add_format({'fg_color': '#ddebf7', 'underline': True, 'bold': True, 'border': 1})
        datagridformat = workbook.add_format({'fg_color': '#e2efda', 'border': 1, 'bold': True})
        textboxoption = {'width': 1000, 'height': 20000}
        nameformat = workbook.add_format({'bold': True, 'underline': True, 'font_color': 'blue', 'font_size': 11})

        worksheet.write(0, 1, docname, nameformat)
        worksheet.write(1, 1, 'Steps ' + steps, nameformat)

        # Add in the column names --------------------------------------------------------------------
        n = 3
        m = 1

        for i in columns:
            worksheet.write(n, m, i, metricnameformat)
            m += 1
        # --------------------------------------------------------------------------------------------
        # Add in the query results -------------------------------------------------------------------
        m = 1
        n += 1
        maxlen = 0

        for i in drop:
            for j in i:
                worksheet.write(n, m, j, stepformat)
                m += 1
            if maxlen == 0:
                maxlen = m
            m = 1
            n += 1
        # ---------------------------------------------------------------------------------------------
        # Add in the sum totals -----------------------------------------------------------------------
        n += 1

        worksheet.write(n, 0, 'Totals:')
        for i in range(maxlen-1):
            worksheet.write(n, m, '=SUM(' + str(other.Other.alphanumupper(other, m)) + '3:' + str(other.Other.alphanumupper(other, m)) + str(n-1) + ')', datagridformat)
            m += 1
        # ---------------------------------------------------------------------------------------------
        # Add in the query ----------------------------------------------------------------------------
        n += 2
        worksheet.insert_textbox(n, 1, sqlparse.format(sql, reindent=True, keyword_case='upper'), textboxoption)
