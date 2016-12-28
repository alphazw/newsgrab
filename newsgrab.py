#
# Update:
#
# 2016-12-20
# + New

from openpyxl import load_workbook
import datetime
RuleFN = 'rulelist.xlsx'


#Build file name with today's date
def get_todayFN():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

#get the rule list from a given excel workbook, return the value of the value into a dict
def get_rulelist(FN):
    wb = load_workbook(filename=FN, read_only=True)
    ws = wb['Sheet1']
    (RL,RW) = ([],[])

    for row in ws.rows:
        for cell in row:
            RW.append(cell.value)

        RL.append(RW)
        RW = []

    return RL
