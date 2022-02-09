# Home Assistant Add-on: Remote Speaker

Allow Home Assistant to use your local audio device as Media Player via a simple Rest-API.

## WARNING!!!!
* Code is not perfect, it is only for my used cases.
* It is only tested on Raspberry Pi 4.
* You may need to suspend hassio_audio on start up, a work around to install [Alsa & PulseAudio Fix Container](https://github.com/OPHoperHPO/hassio-addons/tree/master/pulseaudio_fix) and run it at start up

## Install
1. Add this url to your hass.io addons repos: \
`https://github.com/modestpharaoh/hassio-addons`
2. Update addons list.
3. Install Remote Speaker add-on.

## How to use
1. Install the add-on.
2. Run it on start up.
3. Check add-on logs that gunicron started and running.

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
