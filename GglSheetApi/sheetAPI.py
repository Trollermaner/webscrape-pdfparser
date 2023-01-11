import pygsheets
import pandas
import json

with open("./Pdf Reader/classList_with_rating.json", "r") as classListJson:
    classListRead = classListJson.read()

csv = "./Google Sheet API/test.csv"

classList = json.loads(classListRead)
print(classList[0]["schedule"])

googleAPI = pygsheets.authorize(service_file='./GglSheetApi/krabbyPattyFormula.json')

dataf_schedule = pandas.json_normalize(classList)

sheet = googleAPI.open('Test sheet')


worksheet = sheet[0]

worksheet.set_dataframe(dataf_schedule,(1,1))
