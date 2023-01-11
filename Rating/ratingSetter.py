from ratingScraper import getRating
import json

with open("./Pdf Reader/classList.json", "r") as classFileJson:
    classListJson = classFileJson.read()

classList = json.loads(classListJson)

def rate(classList, teacherRating):
    i = 0
    for course in classList:
        print(i)
        i+=1
        teacher = course["teacher"]
        if(course["lab"] != ""):
            labTeacher = course["lab"]["teacher"]
            if labTeacher not in teacherRating:
                teacherRating[labTeacher] = getRating(labTeacher)
        if teacher not in teacherRating:
            teacherRating[teacher] = getRating(teacher)

    return json.dumps(teacherRating)

with open("./Rating/ratingList.json", "w") as jsonFileW:
    jsonFileW.write(rate(classList, teacherRating = {}))