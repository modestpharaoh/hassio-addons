# Home Assistant Add-on: Remote Speaker

Allow Home Assistant to use your local audio device as audio media player via a simple Rest-API.

## WARNING!!!!
* Code is not perfect, it is only for my used cases.
* It is only tested on Raspberry Pi 4.
* You may need to suspend hassio_audio on start up, a work around to install [Alsa & PulseAudio Fix Container](https://github.com/OPHoperHPO/hassio-addons/tree/master/pulseaudio_fix) and run it at start up

## Install with Hass.io
1. Add this url to your hass.io addons repos: \
`https://github.com/modestpharaoh/hassio-addons`
2. Update addons list.
3. Install Remote Speaker add-on.

## Install with Docker from host.
Run the following as root, this will create remotespeaker docker container that will always run on start up unless you stop it manually.

**NOTED: It required that alsa-utils to be installed and running on the host.**

```
docker run -d --restart unless-stopped \
    -v /dev/snd:/dev/snd \
    -v /dev/shm:/dev/shm \
    -v /usr/share/hassio/media:/media \
     --privileged \
    -p 5005:5005 \
    --name remotespeaker flask/remotespeaker
```
## Predefined audio sources
I added predifined audio sources in the
[sounds directory](https://github.com/modestpharaoh/hassio-addons/tree/master/remote_speaker/sounds).
You add whatever frequently used audio files, but you will need to include them in json format in
[.audioMessageConfig file](https://github.com/modestpharaoh/hassio-addons/blob/master/remote_speaker/.audioMessageConfig).


## How to use
1. Install the add-on.
2. Run it on start up.
3. Check add-on logs that gunicron started and running.
4. Install my custom media player componant [Remote Speaker](https://github.com/modestpharaoh/hassio-custom-components/tree/main/tts_remote_speaker) to be able to communicate with this add-on.

## Supported Features
* Home assistant local media browser.
* Play local media.
* Play certain media come with the containers such as alarm sounds and azan prayer.
* Play, pause, seek and stop current audio selected.
* Volume set.


## Tips
A simple way of multiple speakers not directly attache to home assistant, get Aux to bluetooth transmitter that supports connecting to two bluetooth speaker and connect it to your hass.io host. 

## Urls
[Add-on link](https://github.com/modestpharaoh/hassio-addons/tree/master/remote_speaker)

## 👪 Credits
Developed by [modestpharaoh](https://github.com/modestpharaoh)



![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]


[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
