import pdfplumber
import re
import json
import pprint

#### FIX FOR DAYS ON DIFFERENT LINES

with open("./Rating/ratingList.json", "r") as ratingListJson:
    ratingList = json.loads(ratingListJson.read())

class daytime():
    def __init__(self, M, T, W, R, F):
        self.M = M
        self.T = T
        self.W = W
        self.R = R
        self.F = F

def splitDay(days, time, schedule):
    daysList = list(days)
    for day in daysList:
        try:
            if schedule[day] == "":
                schedule[day] = time
            else:
                schedule[day] = ", " + time
        except:
            pass
    return schedule

class classSchedule():
    def __init__(self, section, subject, title, schedule, teacher, lab, rating, extra):
        self.section = section
        self.subject = subject
        self.title = title
        self.schedule = schedule
        self.teacher = teacher
        self.lab = lab
        self.rating = rating
        self.extra = extra

    def __str__(self):
        return f"Subject: {self.subject}, Course: {self.course}, section: {self.section}, teacher: {self.teacher}, schedule: {self.schedule}"

    def __repr__(self):
        return str(self)

class labSchedule():
    def __init__(self, teacher, rating):
        self.teacher = teacher
        self.rating = rating

pdf = pdfplumber.open("./Pdf Reader/classList.pdf")

def splitCourse(courseLine):
    #gets all information from course line
    r = courseLine.split(" ")
    if re.match("[0-9][0-9][0-9][0-9][0-9]", r[0]):
        section = r[0]
        subject = r[1]
        course = r[2]
        title = " ".join(r[3:-2])
        time = r[-1]
        days = r[-2]
        return [section, subject, course, title, days, time]
    else: #if it's a lab, do not include section
        subject = r[0]
        course = r[1]
        time = r[-1]
        days = r[-2]
        return [subject, course, days, time]

def splitTeacher(teacherLine):
    #gets teacher name from line
    try:
        r = teacherLine.split(", ")
        last = r[0].split(" ")
        first = r[1].split(" ")
        name = first[0] + " " + last[-1]
        return name
    except:
        return ""

def classParse(pdf, ratingList):
    prevCourse = ""
    i=0
    courseList = {}
    #list of all courses and objects
    for page in pdf.pages:
        #Goes through all the pdf
        page = page.extract_text()
        specLines = page.split("\n")
        #speclines as in spectator lines (spectator ions)
        lines = specLines[5:-1]
        #removes the title along with the page number
        for line in lines:
            #Goes through each line
            splitted = line.split(" ")
            if re.match("[0-9][0-9][0-9][0-9][0-9]", splitted[0]):
                #checks if line is a course line
                lectureList = splitCourse(line)
                course = lectureList[2]
                if course not in courseList:
                    courseList[course] = []
                lecture = classSchedule(lectureList[0], lectureList[1], lectureList[3],"", "", "", "", "")
                courseList[course].append(lecture.__dict__)
                i = len(courseList[course])-1
                prevCourse = course
                specSchedule = daytime("", "", "", "", "")
                schedule = splitDay(splitted[-2], splitted[-1], specSchedule.__dict__)
                courseList[prevCourse][i]["schedule"] = schedule
                
            elif re.match("[A-Z][A-Z][A-Z][A-Z] [A-Z0-9][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9]", " ".join(splitted[0:2])):
                #checks if this is a lab
                labo = labSchedule("", "")
                courseList[prevCourse][i]["lab"] = labo.__dict__
                schedule = courseList[prevCourse][i]["schedule"]
                courseList[prevCourse][i]["schedule"] = splitDay(splitted[-2], splitted[-1], schedule)

            elif splitted[0] == "Lecture":
                #checks if teacher should be associated with the course
                courseList[prevCourse][i]["teacher"] = splitTeacher(line)
                courseList[prevCourse][i]["rating"] = ratingList[courseList[prevCourse][i]["teacher"]]
                if re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", splitted[-1]):
                    schedule = courseList[prevCourse][i]["schedule"]
                    courseList[prevCourse][i]["schedule"] = splitDay(splitted[-2], splitted[-1], schedule)
            elif splitted[0] == "Laboratory":
                #checks if teacher should be associated with the lab
                courseList[prevCourse][i]["lab"]["teacher"] = splitTeacher(line)
                courseList[prevCourse][i]["lab"]["rating"] = ratingList[courseList[prevCourse][i]["lab"]["teacher"]]
                if re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", splitted[-1]):
                    schedule = courseList[prevCourse][i]["schedule"]
                    courseList[prevCourse][i]["schedule"] = splitDay(splitted[-2], splitted[-1], schedule)

            elif re.match("[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]", splitted[-1]):
                    schedule = courseList[prevCourse][i]["schedule"]
                    courseList[prevCourse][i]["schedule"] = splitDay(splitted[-2], splitted[-1], schedule)

            else:
                if line != "SECTION DISC COURSE NUMBER COURSE TITLE/TEACHER DAY/TIMES":
                    #anything else goes to the extra variable in courseList object
                    courseList[prevCourse][i]["extra"] += line
                if not re.match("[A-Z0-9][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9][A-Z0-9][-][A-Z0-9][A-Z0-9]", splitted[0]):
                    courseList[prevCourse][i]["extra"] += line
    return courseList

def run(pdf, ratingList):
    courseList = classParse(pdf, ratingList)

    jsonCourse = json.dumps(courseList, indent=4)

    with open("./Pdf Reader/classList_by_course.json", "w") as file:
        file.write(jsonCourse)

run(pdf, ratingList) #I don't want to run it anymore (already parsed all I need)