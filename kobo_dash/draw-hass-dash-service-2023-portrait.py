#!/usr/bin/python3

from datetime import date, datetime, timedelta
from flask import Flask,request,send_file
from subprocess import call

import os
import pygame
import requests
app = Flask(__name__)

workDir = os.path.dirname(os.path.abspath(__file__))
bgImage = os.path.join(workDir, 'images' ,"kobo-bg-TransTimeAndNotify.png")
tempSymbol = os.path.join(workDir, 'images' ,"temp.png")
humiSymbol = os.path.join(workDir, 'images' ,"humidity.png")
windSymbol = os.path.join(workDir, 'images' ,"wind.png")
rainSymbol = os.path.join(workDir, 'images' ,"rain.png")

# original Width for Glo HD is 1448, however I wanted to observe native kobo battery and wifi
# status, so I left 95px from top, this the kobo status bar, it is the only thing that will be
# updated by kobo system, without changing the rest of the screen, unless someone touch the
# screen.
screenWidth=1353
screenLength=1072

# New Upright
screenWidth=1072
screenLength=1353

# ~ screen = pygame.Surface((screenWidth, screenLength))
screen = pygame.Surface([screenWidth, screenLength], pygame.SRCALPHA, 32)

white = (255, 255, 255)
black = (0, 0, 0)
gray = (125, 125, 125)
#img_dash_path = "/dev/shm/koboGloDash.png"
#img_dash_path = "/media/koboGloDash.png"
img_dash_path = "./koboGloDash.png"


curTime = datetime.now().strftime("%H:%M")
curDate = datetime.now().strftime("%a   %h %d") #"Fri     Feb 25"

curTempIn = "22.2"
curHumdIn = "50"
curTempOut = "25.2"
curHumdOut = "90"
todayPressure= 1002.2

fajr_time    = "05:41"
sunrise_time = "07:21"
dhuhr_time   = "12:40"
asr_time     = "15:19"
mghrb_time   = "17:56"
isha_time    = "19:31"

todayForecast = "cloudy"
hrTwoForecast = "partlycloudy"
hrForForecast = "rainy"
tomrwForecast = "sunny"
twDayForecast = "lightning"
trDayForecast = "fog"

todayHighT = 30.2
hrTwoHighT = 32.2
hrForHighT = 34.2
tomrwHighT = 36.2
twDayHighT = 38.2
trDayHighT = 39.2

todayLowT = 20.2
hrTwoLowT = 22.2
hrForLowT = 24.2
tomrwLowT = 26.2
twDayLowT = 28.2
trDayLowT = 29.2

todayHumid = 40

hrTwoRain = 0.1
hrForRain = 1.0
tomrwRain = 2.0
twDayRain = 3.0
trDayRain = 7.0

todayWind = 22.2
hrTwoWind = 22.4
hrForWind = 23.5
tomrwWind = 25.7
twDayWind = 27.8
trDayWind = 29.7



textX = 1000
textY = 50
textFontSize = 100
fontReg = "fonts/Cairo-Regular.ttf"
fontBld = "fonts/Cairo-Bold.ttf"
fontMdi = "fonts/materialdesignicons-webfont.ttf"
fontName = fontReg

def drawText(prayerTime):
    global textX, textY, textFontSize, fontName, fontReg
    prayername_font = pygame.font.Font(fontName, textFontSize)
    prayerNameImg = prayername_font.render(prayerTime, True, black)
    prayerName_rect = prayerNameImg.get_rect()
    textY = textY + textFontSize
    prayerName_rect.bottomleft = (textX, textY)
    screen.blit(prayerNameImg, prayerName_rect)

def drawImg(imgPath):
    global textX, textY, textFontSize, fontName, fontReg
    prayImage = pygame.image.load(imgPath)
    prayerImage_rect = prayImage.get_rect()
    textY = textY + textFontSize
    prayerImage_rect.bottomleft = (textX, textY)
    screen.blit(prayImage, prayerImage_rect)

def getWeatherSymbol(forecast):
    weatherSymbolPath = os.path.join(workDir, 'images' ,forecast + ".png")
    if not os.path.exists(weatherSymbolPath):
        weatherSymbolPath = os.path.join(workDir, 'images' ,"unknown.png") 
    #print(weatherSymbolPath)
    return weatherSymbolPath

@app.route('/getKoboDash', methods=['GET'])
def getKoboDash():
    #drawDash()
    global img_dash_path
    return send_file(img_dash_path, mimetype="image/png")

@app.route('/genKoboDash', methods=['GET'])
def genKoboDash():
    global curTime, curDate, curTempIn, curHumdIn, curTempOut, curHumdOut, fajr_time, sunrise_time, dhuhr_time, asr_time, mghrb_time, isha_time, todayForecast, hrTwoForecast, hrForForecast, tomrwForecast, twDayForecast, trDayForecast, todayHighT, hrTwoHighT, hrForHighT, tomrwHighT, twDayHighT, trDayHighT, todayPressure, tomrwLowT, twDayLowT, trDayLowT, todayHumid, hrTwoRain, hrForRain, tomrwRain, twDayRain, trDayRain, todayWind, hrTwoWind, hrForWind, tomrwWind, twDayWind, trDayWind

    curTime = datetime.now().strftime("%H:%M")
    curDate = datetime.now().strftime("%a   %h %d") #"Fri     Feb 25"

    curTempIn     = request.args.get('curTempIn')
    curHumdIn     = request.args.get('curHumdIn')
    curTempOut    = request.args.get('curTempOut')
    curHumdOut    = request.args.get('curHumdOut')
    fajr_time     = request.args.get('fajr_time')
    sunrise_time  = request.args.get('sunrise_time')
    dhuhr_time    = request.args.get('dhuhr_time')
    asr_time      = request.args.get('asr_time')
    mghrb_time    = request.args.get('mghrb_time')
    isha_time     = request.args.get('isha_time')
    todayForecast = request.args.get('todayForecast')
    hrTwoForecast = request.args.get('hrTwoForecast')
    hrForForecast = request.args.get('hrForForecast')
    tomrwForecast = request.args.get('tomrwForecast')
    twDayForecast = request.args.get('twDayForecast')
    trDayForecast = request.args.get('trDayForecast')
    todayHighT    = request.args.get('todayHighT')
    hrTwoHighT    = request.args.get('hrTwoHighT')
    hrForHighT    = request.args.get('hrForHighT')
    tomrwHighT    = request.args.get('tomrwHighT')
    twDayHighT    = request.args.get('twDayHighT')
    trDayHighT    = request.args.get('trDayHighT')

    todayPressure     = request.args.get('todayPressure')

    tomrwLowT     = request.args.get('tomrwLowT')
    twDayLowT     = request.args.get('twDayLowT')
    trDayLowT     = request.args.get('trDayLowT')
    todayHumid    = request.args.get('todayHumid')
    hrTwoRain     = request.args.get('hrTwoRain')
    hrForRain     = request.args.get('hrForRain')
    tomrwRain     = request.args.get('tomrwRain')
    twDayRain     = request.args.get('twDayRain')
    trDayRain     = request.args.get('trDayRain')
    todayWind     = request.args.get('todayWind')
    hrTwoWind     = request.args.get('hrTwoWind')
    hrForWind     = request.args.get('hrForWind')
    tomrwWind     = request.args.get('tomrwWind')
    twDayWind     = request.args.get('twDayWind')
    trDayWind     = request.args.get('trDayWind')

    drawDash()
    
    return('successful')



@app.route('/drawDash', methods=['GET'])
def drawDash():
    global curTime, curDate, curTempIn, curHumdIn, curTempOut, curHumdOut, fajr_time, sunrise_time, dhuhr_time, asr_time, mghrb_time, isha_time, todayForecast, hrTwoForecast, hrForForecast, tomrwForecast, twDayForecast, trDayForecast, todayHighT, hrTwoHighT, hrForHighT, tomrwHighT, twDayHighT, trDayHighT, todayPressure, tomrwLowT, twDayLowT, trDayLowT, todayHumid, hrTwoRain, hrForRain, tomrwRain, twDayRain, trDayRain, todayWind, hrTwoWind, hrForWind, tomrwWind, twDayWind, trDayWind
    
    pygame.font.init()
    
    # last digit mast be 0 to be completely transparent
    screen.fill((100,100,255,0))
    
    global textX, textY, textFontSize, fontName
    textFontSize = 0 # This reference in drawImg
    textX = 0 ; textY = screenLength; drawImg(bgImage)


    ######################### frame Drawing

    # Draw rect frame
    pygame.draw.line(screen, black, (0, 2), (screenWidth, 2), 5)
    pygame.draw.line(screen, black, (0, screenLength-2), (screenWidth, screenLength-2), 5)
    pygame.draw.line(screen, black, (2, 0), (2, screenLength), 5)
    pygame.draw.line(screen, black, (screenWidth-2, 0), (screenWidth-2, screenLength), 5)

    # Draw Vert. line divide screen to two right and hand sides
    pygame.draw.line(screen, black, (484, 0), (484, 1070), 5)

    ######## $$$$$$$$$$$$$$$$$$$$$$$ Drawing Right handsides
    # ~ # Draw Time in the top right corner
    # ~ fontName = fontBld; textFontSize = 230; textX = 489; textY = 175; drawText(curTime)
    # ~ # Draw date in the top right corner
    # ~ fontName = fontReg; textFontSize = 100; textX = 509; textY = 55; drawText(curDate)

    # Draw Hor. lines divide right dashboard
    pygame.draw.line(screen, black, (484, 280), (screenWidth, 280), 5)

    ######################### Draw Prayer section
    # Draw prayer arabic names from photos
    fontName = fontReg
    textFontSize = 100; textX = 789; textY = 290
    drawImg('images/fajr.png')
    drawImg('images/sunrise.png')
    drawImg('images/dhuhr.png')
    drawImg('images/asr.png')
    drawImg('images/mghrb.png')
    drawImg('images/isha.png')

    # Draw prayer times
    fontName = fontBld; textFontSize = 100; textX = 489; textY = 340
    drawText(fajr_time     + " :")
    drawText(sunrise_time  + " :")
    drawText(dhuhr_time    + " :")
    drawText(asr_time      + " :")
    drawText(mghrb_time    + " :")
    drawText(isha_time     + " :")

    # draw line under prayer
    pygame.draw.line(screen, black, (484, 900), (screenWidth, 900), 5)

    # Draw ver. lines divide right dashboard for indoor/external temp/humidity 
    pygame.draw.line(screen, black, (778, 900), (778, 1070), 5)

    ##################### Draw Indoor/outdoor mesurements
    # Draw measured Indoor/Outdoor symbols
    textFontSize = 0 # This reference in drawImg



    # Draw outdoor humidity/temp in the top right corner
    fontName = fontBld; textFontSize = 50; textX = 489 ; textY = 920; drawText('OUT')
    
    textFontSize = 0;                      textX = 590 ; textY = 980; drawImg(humiSymbol)
    fontName = fontReg; textFontSize = 80; textX = 640 ; textY = 940; drawText(curHumdOut)
    fontName = fontReg; textFontSize = 30; textX = 749; textY = 920; drawText("%")
    
    textFontSize = 0;                      textX = 490 ; textY = 1065; drawImg(tempSymbol)
    fontName = fontReg; textFontSize = 80; textX = 540 ; textY = 1030; drawText(curTempOut)
    fontName = fontReg; textFontSize = 30; textX = 710; textY = 1010; drawText("°C")

    # Draw Indoor humidity/temp in the top right corner
    fontName = fontBld; textFontSize = 50; textX = 789; textY = 920; drawText('IN')
    
    textFontSize = 0;                      textX = 890; textY = 980; drawImg(humiSymbol)
    fontName = fontReg; textFontSize = 80; textX = 940; textY = 940; drawText(curHumdIn)
    fontName = fontReg; textFontSize = 30; textX = 1049; textY = 920; drawText("%")
                                                                 
    textFontSize = 0;                      textX = 790; textY = 1065; drawImg(tempSymbol)
    fontName = fontReg; textFontSize = 80; textX = 840; textY = 1030; drawText(curTempIn)
    fontName = fontReg; textFontSize = 30; textX = 1010; textY = 1010; drawText("°C")


    # draw line under indoor/external temp/humidity
    pygame.draw.line(screen, black, (484, 1070), (screenWidth, 1070), 5)

    ######## $$$$$$$$$$$$$$$$$$$$$$$ Drawing Left handsides

    # $$$$$$$$$$$$$$$$$$$$$  Now
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 30 ; drawText('Now')
    textX = 270; textY = 140; drawImg(getWeatherSymbol(todayForecast))

    fontName = fontBld; textFontSize = 70 ; textX = 215; textY = 30; drawText(str(todayPressure))
    fontName = fontBld; textFontSize = 30 ; textX = 430; textY = 20; drawText("hPa")
    textFontSize = 0 # This reference in drawImg
    
    #fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 150; drawText("H:")
    fontName = fontBld; textFontSize = 90 ; textX = 15 ; textY = 100; drawText(str(todayHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 160; textY = 55; drawText("°C")

    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 10; textY = 270; drawImg(humiSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 65; textY = 240; drawText(str(todayHumid))
    fontName = fontBld; textFontSize = 30 ; textX = 170; textY = 195; drawText("%")

    textFontSize = 0;                       textX = 250 ; textY = 270; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 300; textY = 240; drawText(str(todayWind))
    fontName = fontBld; textFontSize = 30 ; textX = 400; textY = 195; drawText("km/h")
    
    # Draw Hor. lines after Weather Now
    pygame.draw.line(screen, black, (0, 280), (484, 280), 5)

    # $$$$$$$$$$$$$$$$$$$$$  2 Hrs
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 300 ; drawText('2 Hrs')
    textX = 270; textY = 355; drawImg(getWeatherSymbol(hrTwoForecast))

    #fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 150; drawText("H:")
    fontName = fontBld; textFontSize = 90 ; textX = 15 ; textY = 370; drawText(str(hrTwoHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 160; textY = 320; drawText("°C")

    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 10; textY = 535; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 75; textY = 500; drawText(str(hrTwoRain))
    fontName = fontBld; textFontSize = 30 ; textX = 170; textY = 460; drawText("mm")

    textFontSize = 0;                       textX = 250 ; textY = 535; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 310; textY = 500; drawText(str(hrTwoWind))
    fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 460; drawText("km/h")

    # Draw Hor. lines after Weather 2 Hrs
    pygame.draw.line(screen, black, (0, 543), (484, 543), 5)




    # $$$$$$$$$$$$$$$$$$$$$  4 Hrs
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 565 ; drawText('4 Hrs')
    textX = 270; textY = 635; drawImg(getWeatherSymbol(hrForForecast))

    #fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 150; drawText("H:")
    fontName = fontBld; textFontSize = 90 ; textX = 15 ; textY = 635; drawText(str(hrForHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 160; textY = 585; drawText("°C")

    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 10; textY = 800; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 75; textY = 765; drawText(str(hrForRain))
    fontName = fontBld; textFontSize = 30 ; textX = 170; textY= 715; drawText("mm")

    textFontSize = 0;                       textX = 250 ; textY = 800; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 310; textY = 760; drawText(str(hrForWind))
    fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 710; drawText("km/h")

    # Draw Hor. lines after Weather 4 Hrs
    pygame.draw.line(screen, black, (0, 806), (484, 806), 5)





    # $$$$$$$$$$$$$$$$$$$$$  Tomorrow
    tomorrow = (datetime.now() + timedelta(hours=24)).strftime("%a")
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 830 ; drawText(tomorrow)
    textX = 270; textY = 910; drawImg(getWeatherSymbol(tomrwForecast))

    fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 890; drawText("H:")
    fontName = fontBld; textFontSize = 60 ; textX = 45 ; textY = 890; drawText(str(tomrwHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 165; textY = 890; drawText("°C")

    fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 950; drawText("L:")
    fontName = fontBld; textFontSize = 60 ; textX = 45 ; textY = 950; drawText(str(tomrwLowT))
    fontName = fontBld; textFontSize = 30 ; textX = 165; textY = 950; drawText("°C")

    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 10; textY = 1065; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 75; textY = 1030; drawText(str(tomrwRain))
    fontName = fontBld; textFontSize = 30 ; textX = 170; textY= 995; drawText("mm")

    textFontSize = 0;                       textX = 250 ; textY =1065; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 310; textY = 1030; drawText(str(tomrwWind))
    fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 990; drawText("km/h")


    # Draw Hor. lines after Weather Now
    pygame.draw.line(screen, black, (0, 1070), (484, 1070), 5)

   


    #pygame.image.save(screen, "image.png")
    rotated= pygame.transform.rotate(screen, 0)
    pygame.image.save(rotated, img_dash_path)
    return('successful')



if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5006')
