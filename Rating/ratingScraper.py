from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
import re 

def rate(rating, volume):
    if rating == "N/A":
        return "N/A"
    elif rating == "DNE" or volume == "DNE":
        return "to redo"
    else:
        ratingN = float(rating)
        volumeN = float(volume)
        volumeR = pow(1.05, -0.5*volumeN)-0.5
        if volumeR < 0:
            volumeR = 0
    
    finalRate = 100*(ratingN-volumeR)/5
    return finalRate

#the more ratings the better, hence a professor with one 5 star review will have a lower rating than someone with twenty 4.8 star reviews
#makes it more real and reliable

#converts professor name to add %20 in the space to make it work in a link
def convert(name):
    midName = name.split(" ")
    prof = "%20".join(midName)
    return prof

#finds the professors link in rate my professor
async def getStats(name):
    try:
        prof = convert(name)
        link = "".join(["https://www.ratemyprofessors.com/search/teachers?query=", prof, "&sid=U2Nob29sLTEyMDUw"]) #only for John Abbott College
        #open browser
        browser = await launch()
        #open page
        page = await browser.newPage()
        #open link
        await page.goto(link)
        #get page content
        page_content = await page.content()
        #parse page content
        soup = BeautifulSoup(page_content, "html.parser")
        #checks if school is John Abbott College
        school = soup.find(class_ = "CardSchool__School-sc-19lmz2k-1 iDlVGM").text
        if school == "John Abbott College":
            #find link
            element = soup.find(class_="TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx")
            id = element['href']
            pLink = profLink(id)
            #open another page
            page1 = await browser.newPage()
            #open link
            await page1.goto(pLink)
            #get page content
            page1_content = await page1.content()
            #parse page content
            soup1 = BeautifulSoup(page1_content, "html.parser")
            #get stats needed
            rating = soup1.find(class_="RatingValue__Numerator-qw8sqy-2 liyUjw").get_text()
            volume = soup1.find(class_ = "RatingValue__NumRatings-qw8sqy-0 jMkisx").get_text()
            volumeN = re.sub('\D', '', volume)
            #close browser
            await browser.close()
            return [rating, volumeN]
        else:
            return ["N/A", "N/A"]
    except:
        try:
            print(pLink)
        except:
            return ["N/A", "N/A"]
        return ["DNE", "DNE"]


def profLink(extension):
    link = ''.join(["https://www.ratemyprofessors.com", extension])
    return link 

def getRating(name):
    if name == "":
        return "N/A"
    stats = asyncio.get_event_loop().run_until_complete(getStats(name))
    rating = rate(stats[0], stats[1])
    return rating
    
#print(getRating("Philippe Delage"))

async def getRatingLink(link):
    browser = await launch()
    page1 = await browser.newPage()
    #open link
    await page1.goto(link)
    #get page content
    page1_content = await page1.content()
    #parse page content
    soup1 = BeautifulSoup(page1_content, "html.parser")
    #get stats needed
    rating = soup1.find(class_="RatingValue__Numerator-qw8sqy-2 liyUjw").get_text()
    volume = soup1.find(class_ = "RatingValue__NumRatings-qw8sqy-0 jMkisx").get_text()
    volumeN = re.sub('\D', '', volume)
    #close browser
    await browser.close()
    return rate(rating, volumeN)
