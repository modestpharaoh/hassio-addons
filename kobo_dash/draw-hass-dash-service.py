#!/usr/bin/python3

from datetime import date, datetime, timedelta
from flask import Flask,request,send_file
from subprocess import call

import os
import pygame
import requests
app = Flask(__name__)

workDir = os.path.dirname(os.path.abspath(__file__))
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



curTempIn = "22.2"
curHumdIn = "50"
curTempOut = "25.2"
curHumdOut = "90"

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

hrTwoRain = 0
hrForRain = 1
tomrwRain = 2
twDayRain = 3
trDayRain = 7

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

    


screen = pygame.Surface((screenWidth, screenLength))
white = (255, 255, 255)
black = (0, 0, 0)
gray = (125, 125, 125)
@app.route('/genKoboDash', methods=['GET'])
def genKoboDash():
    pygame.font.init()

    screen.fill(white)

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






    global textX, textY, textFontSize, fontName

    ########################### Draw forecast symbols
    textFontSize = 0 # This reference in drawImg
    textX = 270; textY = 140; drawImg(getWeatherSymbol(todayForecast))
    textX = 185; textY = 420; drawImg(getWeatherSymbol(hrTwoForecast))
    textX = 565; textY = 420; drawImg(getWeatherSymbol(hrForForecast))
    textX = 270; textY = 670; drawImg(getWeatherSymbol(tomrwForecast))
    textX = 185; textY = 950; drawImg(getWeatherSymbol(twDayForecast))
    textX = 565; textY = 950; drawImg(getWeatherSymbol(trDayForecast))

    ########################### Draw headers
    tomorrow = (datetime.now() + timedelta(hours=24)).strftime("%a")
    twoDays = (datetime.now() + timedelta(hours=48)).strftime("%a")
    threeDays = (datetime.now() + timedelta(hours=72)).strftime("%a")
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 30 ; drawText('Today')
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 290; drawText('2 Hrs')
    fontName = fontBld; textFontSize = 50; textX = 387; textY = 290; drawText('4 Hrs')
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 560; drawText(tomorrow)
    fontName = fontBld; textFontSize = 50; textX = 10 ; textY = 830; drawText(twoDays)
    fontName = fontBld; textFontSize = 50; textX = 387; textY = 830; drawText(threeDays)

    ########################### Draw High Temp
    #fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 150; drawText("H:")
    fontName = fontBld; textFontSize = 90 ; textX = 45 ; textY = 130; drawText(str(todayHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 215; textY = 120; drawText("°C")
    
    #fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 380; drawText("H:")
    fontName = fontBld; textFontSize = 70 ; textX = 10 ; textY = 370; drawText(str(hrTwoHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 140; textY = 365; drawText("°C")

    #fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 380; drawText("H:")
    fontName = fontBld; textFontSize = 70 ; textX = 390; textY = 370; drawText(str(hrForHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 512; textY = 365; drawText("°C")


    fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 680; drawText("H:")
    fontName = fontBld; textFontSize = 90 ; textX = 45 ; textY = 660; drawText(str(tomrwHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 215; textY = 650; drawText("°C")
    
    #fontName = fontBld; textFontSize = 40 ; textX = 10 ; textY = 930; drawText(str(twDayHighT))

    fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 910; drawText("H:")
    fontName = fontBld; textFontSize = 50 ; textX = 45 ; textY = 900; drawText(str(twDayHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 140; textY = 895; drawText("°C")

    fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 910; drawText("H:")
    fontName = fontBld; textFontSize = 50 ; textX = 420; textY = 900; drawText(str(trDayHighT))
    fontName = fontBld; textFontSize = 30 ; textX = 512; textY = 895; drawText("°C")

    ########################### Draw Low Temp
    fontName = fontBld; textFontSize = 70 ; textX = 480; textY = 130; drawText(str(todayPressure))
    fontName = fontBld; textFontSize = 30 ; textX = 700; textY = 120; drawText("hPa")
    
    fontName = fontBld; textFontSize = 30 ; textX = 510; textY = 680; drawText("L:")
    fontName = fontBld; textFontSize = 90 ; textX = 545; textY = 660; drawText(str(tomrwLowT))
    fontName = fontBld; textFontSize = 30 ; textX = 715; textY = 650; drawText("°C")

    fontName = fontBld; textFontSize = 30 ; textX = 10 ; textY = 970; drawText("L:")
    fontName = fontBld; textFontSize = 50 ; textX = 45 ; textY = 960; drawText(str(twDayLowT))
    fontName = fontBld; textFontSize = 30 ; textX = 140; textY = 955; drawText("°C")
    
    fontName = fontBld; textFontSize = 30 ; textX = 390; textY = 970; drawText("L:")
    fontName = fontBld; textFontSize = 50 ; textX = 420; textY = 960; drawText(str(trDayLowT))
    fontName = fontBld; textFontSize = 30 ; textX = 512; textY = 955; drawText("°C")


    ########################### Draw Wind Speed
    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 75 ; textY = 260; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 135; textY = 220; drawText(str(todayWind))
    fontName = fontBld; textFontSize = 30 ; textX = 290; textY = 210; drawText("km/h")

    textFontSize = 0;                       textX = 130; textY = 540; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 200; textY = 510; drawText(str(hrTwoWind))
    fontName = fontBld; textFontSize = 30 ; textX = 300; textY = 500; drawText("km/h")

    textFontSize = 0;                       textX = 520; textY = 540; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 590; textY = 510; drawText(str(hrForWind))
    fontName = fontBld; textFontSize = 30 ; textX = 690; textY = 500; drawText("km/h")

    textFontSize = 0;                       textX = 75 ; textY = 800; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 135; textY = 760; drawText(str(tomrwWind))
    fontName = fontBld; textFontSize = 30 ; textX = 290; textY = 750; drawText("km/h")

    textFontSize = 0;                       textX = 130; textY = 1060; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 200; textY = 1030; drawText(str(twDayWind))
    fontName = fontBld; textFontSize = 30 ; textX = 300; textY = 1020; drawText("km/h")
                                                                 
    textFontSize = 0;                       textX = 520; textY = 1060; drawImg(windSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 590; textY = 1030; drawText(str(trDayWind))
    fontName = fontBld; textFontSize = 30 ; textX = 690; textY = 1020; drawText("km/h")

    ########################### Draw forecast humidity
    textFontSize = 0 # This reference in drawImg
    textFontSize = 0;                       textX = 425; textY = 260; drawImg(humiSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 485; textY = 220; drawText(str(todayHumid))
    fontName = fontBld; textFontSize = 30 ; textX = 580; textY = 210; drawText("%")

    textFontSize = 0;                       textX = 180; textY = 485; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 250; textY = 455; drawText(str(hrTwoRain))
    fontName = fontBld; textFontSize = 30 ; textX = 330; textY = 445; drawText("mm")

    textFontSize = 0;                       textX = 570; textY = 485; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 640; textY = 455; drawText(str(hrForRain))
    fontName = fontBld; textFontSize = 30 ; textX = 720; textY = 445; drawText("mm")

    textFontSize = 0;                       textX = 425; textY = 800; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 80 ; textX = 500; textY = 760; drawText(str(tomrwRain))
    fontName = fontBld; textFontSize = 30 ; textX = 610; textY = 750; drawText("mm")

    textFontSize = 0;                       textX = 180; textY = 1000; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 250; textY = 970; drawText(str(twDayRain))
    fontName = fontBld; textFontSize = 30 ; textX = 330; textY = 960; drawText("mm")
                                                                 
    textFontSize = 0;                       textX = 570; textY = 1000; drawImg(rainSymbol)
    fontName = fontBld; textFontSize = 50 ; textX = 640; textY = 970; drawText(str(trDayRain))
    fontName = fontBld; textFontSize = 30 ; textX = 720; textY = 960; drawText("mm")





    ##################### Draw Indoor/outdoor mesurements
    # Draw measured Indoor/Outdoor symbols
    textFontSize = 0 # This reference in drawImg



    # Draw outdoor humidity/temp in the top right corner
    fontName = fontBld; textFontSize = 50; textX = 770 ; textY = 300; drawText('OUT')
    
    textFontSize = 0;                      textX = 900 ; textY = 340; drawImg(humiSymbol)
    fontName = fontReg; textFontSize = 80; textX = 940 ; textY = 300; drawText(curHumdOut)
    fontName = fontReg; textFontSize = 30; textX = 1030; textY = 290; drawText("%")
    
    textFontSize = 0;                      textX = 820 ; textY = 435; drawImg(tempSymbol)
    fontName = fontReg; textFontSize = 80; textX = 870 ; textY = 400; drawText(curTempOut)
    fontName = fontReg; textFontSize = 30; textX = 1015; textY = 390; drawText("°C")

    # Draw Indoor humidity/temp in the top right corner
    fontName = fontBld; textFontSize = 50; textX = 1070; textY = 300; drawText('IN')
    
    textFontSize = 0;                      textX = 1190; textY = 340; drawImg(humiSymbol)
    fontName = fontReg; textFontSize = 80; textX = 1230; textY = 300; drawText(curHumdIn)
    fontName = fontReg; textFontSize = 30; textX = 1320; textY = 290; drawText("%")
                                                                 
    textFontSize = 0;                      textX = 1115; textY = 435; drawImg(tempSymbol)
    fontName = fontReg; textFontSize = 80; textX = 1165; textY = 400; drawText(curTempIn)
    fontName = fontReg; textFontSize = 30; textX = 1310; textY = 390; drawText("°C")

    ######################### Draw Prayer section
    # Draw prayer arabic names from photos
    fontName = fontReg
    textFontSize = 100; textX = 1070; textY = 450
    drawImg('images/fajr.png')
    drawImg('images/sunrise.png')
    drawImg('images/dhuhr.png')
    drawImg('images/asr.png')
    drawImg('images/mghrb.png')
    drawImg('images/isha.png')

    # Draw prayer times
    fontName = fontBld; textFontSize = 100; textX = 770; textY = 500
    drawText(fajr_time     + " :")
    drawText(sunrise_time  + " :")
    drawText(dhuhr_time    + " :")
    drawText(asr_time      + " :")
    drawText(mghrb_time    + " :")
    drawText(isha_time     + " :")

    ######################### Line Drawing
    # Draw Time in the top right corner
    fontName = fontBld; textFontSize = 230; textX = 770; textY = 160; drawText(curTime)
    
    # Draw date in the top right corner
    fontName = fontReg; textFontSize = 100; textX = 800; textY = 40; drawText(curDate)

    # Draw rect frame
    pygame.draw.line(screen, black, (0, 2), (screenWidth, 2), 5)
    pygame.draw.line(screen, black, (0, screenLength-2), (screenWidth, screenLength-2), 5)
    pygame.draw.line(screen, black, (2, 0), (2, screenLength), 5)
    pygame.draw.line(screen, black, (screenWidth-2, 0), (screenWidth-2, screenLength), 5)
    
    # Draw Vert. line before prayers
    pygame.draw.line(screen, black, (765, 0), (765, screenLength), 5)
    # Draw Hor. lines divide right dashboard
    pygame.draw.line(screen, black, (765, 270), (screenWidth, 270), 5)
    pygame.draw.line(screen, black, (765, 440), (screenWidth, 440), 5)
    # Draw ver. lines divide right dashboard
    pygame.draw.line(screen, black, (1059, 270), (1059, 440), 5)
    
    ###### Right handside Dashboard horizontal lines
    pygame.draw.line(screen, black, (0, 270), (765, 270), 5)
    pygame.draw.line(screen, black, (0, 540), (765, 540), 5)
    pygame.draw.line(screen, black, (0, 810), (765, 810), 5)

    ###### Right handside Dashboard vertical lines
    pygame.draw.line(screen, black, (382, 270), (382, 540), 5)
    #pygame.draw.line(screen, black, (382, 540), (382, 810), 5)
    pygame.draw.line(screen, black, (382, 810), (382, screenLength), 5)


    #pygame.image.save(screen, "image.png")
    rotated= pygame.transform.rotate(screen, 90)
    pygame.image.save(rotated, "/config/koboGloDash.png")
    #pygame.image.save(rotated, "/usr/share/hassio/homeassistant/koboGloDash.png")
    return('successful')

if __name__ == "__main__":
    app.run(host='0.0.0.0',port='5006')
