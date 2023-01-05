import  csv
with open('enemys.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    a = [i for i in list(reader)[1:]]
    print(a)