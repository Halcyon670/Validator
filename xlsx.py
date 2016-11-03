import xlsxwriter
import other
import sqlparse


class xlsxsheet:

    xlsxcount = 0

    def addsheet(self, workbook, name, url, daterange, lastmodified, metricnames, steps, datagrid, sql, image):

        xlsxsheet.xlsxcount += 1

        if xlsxsheet.xlsxcount < 10:
            worksheet = workbook.add_worksheet(str(xlsxsheet.xlsxcount) + '-' + name[:29].replace('[', '').replace(']', '').replace(':', '').replace('*', '').replace('?', '').replace('\\', '').replace('/', ''))
        elif xlsxsheet.xlsxcount >= 10:
            worksheet = workbook.add_worksheet(str(xlsxsheet.xlsxcount) + '-' + name[:28].replace('[', '').replace(']', '').replace(':', '').replace('*', '').replace('?', '').replace('\\', '').replace('/', ''))

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

    def adddropinvest(self, workbook, drop, query):

        xlsxsheet.xlsxcount += 1
        worksheet = workbook.add_worksheet('Drop Investigation')