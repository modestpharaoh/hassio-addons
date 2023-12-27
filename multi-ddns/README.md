# Home Assistant Add-on: Multi-DDNS

Automatically update Home Assistant multiple DDNS IPs address with integrated HTTPS support via Let's Encrypt. it currently supports the following DDNS services:
 - [Duck DNS][duckdns]
 - [Dynu DNS][dynudns]

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

## About

This add-on includes support for Let’s Encrypt and automatically creates and renews your Home Assistant SSL certificates that will be valid for the multiple DDNS domains from the supported DDNS services.

Thanks for @Koying, as this code is inspired came from: https://github.com/koying/ha-addons/tree/main/dynudns-addon

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[dynudns]: https://www.dynu.com
[duckdns]: https://www.duckdns.org