#!/usr/bin/python3

import datetime
import exiftool
import ffmpeg
import glob
import time
import json
import os
import subprocess
import sys
import re
import requests
from flask import Flask,request,send_file
import urllib.request
import pygame
app = Flask(__name__)

defaultNotifyMusic = 'default_notify_music.mp3'
scriptDir = os.path.dirname(os.path.abspath(__file__))
soundDir = os.path.join(scriptDir, 'sounds')

AudioSources = {}
CurrentSource = 'Intiated'
MediaDuration = 0.0
MediaOffset = 0.0
MediaPosition = 0.0 + MediaOffset

defaultVolume = 1
defaultLoops = 0
defaultNotifyMusicPath = os.path.join(soundDir, defaultNotifyMusic)
audioMessageConfig = os.path.join('/app', '.audioMessageConfig')
hassTTSDir = '/usr/share/hassio/homeassistant/tts/'
cachedDir = '/dev/shm/remoteSpeaker'

audioURLFileReg = re.compile(r'^https?\:\/\/.*.(mp3|wav|MP3|WAV)')
localMediaFileReg = re.compile(r'^\/.*.(mp3|wav|MP3|WAV)')
ttsAudioFileReg = re.compile(r'TTS-.*\.mp3')
announceMusicVolumeFactor = 0.5

# mediaState should return the current state of the media player, wether it is playing, paused or
# stopped. The reason to create custom, that pygame doesn't have a discrete status for paused status
MediaState = "STATE_STOP"
# Available State STATE_PAUSED STATE_PLAYING STATE_STOP


# MediaPriority should return the current priority of the running media.
# it is a number between 0-100
# Lower number is lower priority
# For each request to play media, media player will compare the priority of the new media against
# the current running media. Only if the new media has higher priority, the new media will preempt
# the current one.
MediaPriority = 0
# Priority Categories #
# 0  - 10   : Low Priority Notifications
# 11 - 40   : Medium Priority Notifications
# 41 - 60   : High Priority Notifications
# 60 - 100  : Alerts



ffmpegTmpDir = '/dev/shm/'
homeDir = os.path.expanduser("/app/")
#audioMessageConfig = os.path.join(homeDir, '.audioMessageConfig')
notifyMsg = '/app/sounds/announcement_message.mp3'

def loadConfig(configFile):
    f = open(configFile, 'r')
    config = json.load(f)
    f.close()
    return config

def play_file(audio_file, volume=defaultVolume, loopNum=defaultLoops):
    try:
        pygame.mixer.music.set_volume(float(volume))
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play(loopNum)
        global MediaState
        if get_busy() == True:
            MediaState = 'STATE_PLAYING'
            return('successful')
        else:
            MediaState = 'STATE_STOP'
            return('Failed to play:' + audio_file)
    except Exception as e:
        return('Error playing ' + audio_file + ' ' + str(e))

def deleteCachedAudioFiles():
    oldTmpAudioFiles = glob.glob(os.path.join(cachedDir,'*'))
    for filePath in oldTmpAudioFiles:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)

def loadURLAudioFile(audioURL):
    audioFileName = audioURL.split("/")[-1]
    audioFilePath = os.path.join(cachedDir, audioFileName)
    urllib.request.urlretrieve(audioURL, audioFilePath)
    return audioFilePath

@app.route('/media_pause', methods=['GET'])
def media_pause():
    global MediaPriority
    try:
        pygame.mixer.music.pause()
        global MediaState
        if get_busy() == False and getPos() > 0:
            MediaState = 'STATE_PAUSED'
            return('successful')
        elif get_busy() == False and getPos() < 0:
            MediaState = 'STATE_STOP'
            return('failed to pause, current state: STOP')
        elif get_busy() == True:
            MediaState = 'STATE_PLAYING'
            return('failed to pause, current state: Playing')
    except Exception as e:
        return('failed to pause'+str(e))

@app.route('/media_play', methods=['GET'])
def media_play():
    global MediaState
    if MediaState == 'STATE_PAUSED':
        try:
            pygame.mixer.music.unpause()
            if get_busy() == True:
                MediaState = 'STATE_PLAYING'
                return('successful')
            else:
                MediaState = 'STATE_STOP'
                return('failed to play')
        except Exception as e:
            return(str(e))
    if MediaState == 'STATE_STOP':
        print("Try Play Audio again")
        return playAudioFile()
    return('successful')

def get_duration(filepath):
    try:
        #with exiftool.ExifTool() as et:
        #    duration = et.get_tag('Composite:Duration', filepath)
        #    et.terminate()
        duration = float(ffmpeg.probe(filepath)['format']['duration'])
        print(duration)
        return duration
    except:
        print('Failed to get the duration')
        return 300.0

@app.route('/get_busy', methods=['GET'])
def get_busy():
    return pygame.mixer.music.get_busy()

@app.route('/getUpdate', methods=['GET'])
def getUpdate():
    update = {}
    global MediaState, CurrentSource
    position = getPos()
    busy = get_busy()
    update['busy'] = busy
    print(MediaDuration)
    print(position)
    print(busy)
    try:
        # If Mixer not busy, while state still playing, a work around
        # is to call media_stop to fix the status
        if busy == False and MediaState == 'STATE_PLAYING':
            print('mixer is not busy, while state is playing, initiate stop')
            media_stop()
        if position <= 0 :
            print('music stopped, as position is -1')
            MediaState = 'STATE_STOP'
        update['state'] = MediaState
        update['volume'] = str(getVolume())
        update['duration'] = str(MediaDuration)
        update['sources'] = AudioSources
        update['current_source'] = CurrentSource
        update['current_priority'] = MediaPriority
    except:
        update['state'] = '0'
        update['volume'] = '0.5'
        update['duration'] = str(MediaDuration)
        update['sources'] = AudioSources
        update['current_source'] = CurrentSource
        update['current_priority'] = MediaPriority
    if MediaState != 'STATE_STOP':
        update['position'] = str(position)
    else:
        update['position'] = str(0.0)
    return update

@app.route('/media_stop', methods=['GET'])
def media_stop():
    global MediaPriority, MediaOffset
    # MediaPriority = 0
    try:
        #pygame.mixer.music.rewind()
        pygame.mixer.music.stop()
        global MediaState
        if get_busy() == False:
            MediaState = 'STATE_STOP'
            MediaOffset = 0.0
            return('successful')
        else:
            # MediaState = 'STATE_PLAYING'
            return('failed to stop')
    except Exception as e:
        return(str(e))


@app.route('/select_source', methods=['GET'])
def selectSource():
    source = request.args.get('source')
    global CurrentSource, MediaPriority
    if source is not None:
        CurrentSource = source

    # Update priority to zero. This will make sure manual selecting new source won't override import
    # automated announcement
    MediaPriority = 0
    return "successful"

@app.route('/getVolume', methods=['GET'])
def getVolume():
    return pygame.mixer.music.get_volume()

@app.route('/getPos', methods=['GET'])
def getPos():
    return (pygame.mixer.music.get_pos() / 1000.0 + MediaOffset )

def setVolumeLevel(vol):
    try:
        pygame.mixer.music.set_volume(float(vol))
        return("Volume set")
    except:
        return('Failed to set volume')

def setPosition(position):
    #pygame.mixer.music.pause()
    #pygame.mixer.music.play(0, int(float(position)))
    #print(int(float(position)))
    #pygame.mixer.music.rewind()
    #pygame.mixer.music.set_pos(int(float(position)))
    #pygame.mixer.music.play()
    #print(getPos())
    try:
        pygame.mixer.music.play(0, int(float( 
        position)))
        global MediaOffset
        MediaOffset = float(position)
        #pygame.mixer.music.rewind()
        #pygame.mixer.music.set_pos(int(float(position)))
        return("Position set")
    except:
        return('Failed to set Position')

@app.route('/setVolume', methods=['GET'])
def setVolume():
    volume = request.args.get('volume')
    return setVolumeLevel(volume)

@app.route('/setPos', methods=['GET'])
def setPos():
    position = request.args.get('position')
    return setPosition(position)

def mediaPriorityTestFailed(newPriority):
    global MediaState, MediaPriority
    # if not get_busy():
    #     return False
    if MediaState == "STATE_PLAYING":
        if newPriority < MediaPriority:
            return True
    return False

@app.route('/playHassTTS', methods=['GET'])
def playHassTTS():
    # Delete old TTS file in memory
    deleteCachedAudioFiles()
    priority = request.args.get('priority')
    try:
        priority = int(float(priority))
    except:
        priority = 0
    if mediaPriorityTestFailed(priority):
        return("FAILED: Can not preemt the current playing media")
    # Stop any audio running
    media_stop()
    # get http parameters
    repeatNum = request.args.get('repeatNum')
    audioFile = request.args.get('audioFile')
    volume = request.args.get('volume')
    announcement_music = request.args.get('announcement_music')
    print('announcement_music: '+ str(announcement_music) + ' ' + str(type(announcement_music)))

    audioFilePath = os.path.join(hassTTSDir, audioFile)
    # Amplfy the TTS audio file to 7 times 
    tempAudioFile = audioFilePath
    #tempAudioFile = os.path.join(cachedDir, audioFile)
    #ffmpeg.input(audioFilePath).filter('volume', '6.34dB').output(tempAudioFile ).overwrite_output().global_args('-loglevel', 'quiet').run()
    if volume is None:
        volume = getVolume()
    if repeatNum is None:
        repeatNum = defaultLoops
    else:
        repeatNum = int(float(repeatNum))
    if announcement_music is not None and announcement_music == 'True':
        announcement_music = True
    else:
        announcement_music = False

    if announcement_music:
        print('Playing announcement music!')
        try:
            play_file(defaultNotifyMusicPath, round(float(volume)*announceMusicVolumeFactor,2), 0)
            time.sleep(2)
        except:
            return('Failed to play default Notify Music')
    global CurrentSource
    CurrentSource = "TTS-" + audioFile
    # Play the actual audio 
    global MediaDuration, MediaOffset
    MediaOffset = 0.0
    try:
        if float(repeatNum) < 2.0:
            MediaDuration = float(ffmpeg.probe(tempAudioFile)['format']['duration'])
        else:
            MediaDuration = float(ffmpeg.probe(tempAudioFile)['format']['duration']) * ( float(repeatNum) + 1.0)
        resp = play_file(tempAudioFile, volume, repeatNum)
        global MediaPriority
        MediaPriority = priority
    except:
        return('failed to play the audio file') 
    return resp

@app.route('/playAudioFile', methods=['GET'])
def playAudioFile():
    deleteCachedAudioFiles()
    priority = request.args.get('priority')
    try:
        priority = int(float(priority))
    except:
        priority = 0
    if mediaPriorityTestFailed(priority):
        return("FAILED: Can not preemt the current playing media")
    media_stop()
    announcement_music = request.args.get('announcement_music')
    print('announcement_music: '+ str(announcement_music) + ' ' + str(type(announcement_music)))
    audioFile = request.args.get('audioFile')
    print('audioFile: '+ str(audioFile) + ' ' + str(type(audioFile)))
    repeatNum = request.args.get('repeatNum')
    print('repeatNum: '+ str(repeatNum) + ' ' + str(type(repeatNum)))
    volume = request.args.get('volume')
    print('volume: '+ str(volume) + ' ' + str(type(volume)))
    if volume is None:
        volume = getVolume()
    if repeatNum is None:
        repeatNum = defaultLoops
    else:
        repeatNum = int(float(repeatNum))

    if announcement_music is not None and announcement_music == 'True':
        announcement_music = True
    else:
        announcement_music = False
    global CurrentSource
    print('CurrentSource: '+ str(CurrentSource))
    if audioFile is not None:
        CurrentSource = audioFile
    else:
        audioFile = CurrentSource
    print('audioFile: '+ str(audioFile) + ' ' + str(type(audioFile)))
    audioFilePath = ''
    if audioURLFileReg.match(audioFile):
        # If file is URL, cache the file first
        audioFilePath = loadURLAudioFile(audioFile)
        print(audioFilePath)
    elif localMediaFileReg.match(audioFile):
        audioFilePath = audioFile
    elif ttsAudioFileReg.match(audioFile):
        audioFilePath = os.path.join(hassTTSDir, audioFile.replace('TTS-', ''))
    else:
        # if file not URL, consider it as known file 
        AudioSources = loadConfig(audioMessageConfig)
        try:
            audioFile = AudioSources[audioFile]
            audioFilePath = os.path.join(soundDir, audioFile)
        except:
            return('Known file is not exist')
    print('audioFilePath: '+ str(audioFilePath))
    if announcement_music:
        print('Playing announcement music!')
        try:
            play_file(defaultNotifyMusicPath, round(float(volume)*announceMusicVolumeFactor,2), 0)
            time.sleep(2) 
        except:
            return('Failed to play default Notify Music')
    global MediaDuration, MediaOffset
    MediaOffset = 0.0
    try:
        MediaDuration = get_duration(audioFilePath)
        resp = play_file(audioFilePath, volume, repeatNum)
        global MediaPriority
        MediaPriority = priority
    except:
        return('failed to play the audio file') 
    return resp




AudioSources = loadConfig(audioMessageConfig)
pygame.mixer.init(44100, 32, 2, 4096)
try:
    os.makedirs(cachedDir)
except:
    print('cached Directory is already exist.')
play_file(defaultNotifyMusicPath, 0.0, 0)
if __name__ == '__main__':
    #pygame.mixer.init()
    #pygame.mixer.init(44100, -16, 2, 1024)
    #pygame.mixer.init(44100, 32, 2, 4096)
    #global AudioSources
    #AudioSources = loadConfig(audioMessageConfig)
    #try:
    #    os.makedirs(cachedDir)
    #except:
    #    print('cached Directory is already exist.')
    #AudioSources = loadConfig(audioMessageConfig)
    #play_file(defaultNotifyMusicPath, 0.5, 0)
    #app.run(host='172.17.0.1',port='5005')
    app.run(host='0.0.0.0',port='5005')
    
