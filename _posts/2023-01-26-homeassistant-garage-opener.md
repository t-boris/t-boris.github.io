---
layout: post
title: Garage door opener with Home Assistant
date: 2023-01-11
tags: smarthome home-assistant
categories: smarthome
excerpt: "Garage door opener with Shelly switch, sensors and Home Assistant "
---

# Problem definition

Recently I got a new interest - home automation. This is very broad topic that could require a whole book or a web site. Here I'd like to tell you only the story of automating my garage door.

I had the following requirement from this project:
- Add ability to open my garage with the phone. Don't like old remotes that I can forget.
- Ability to perform automations like open garage when my car arrives and automatically close it when it's left open
- It should be cheep and fun

# Research

First step was to search for existing solutions and I found really good sources:
- [Make Your Garage Door Opener Smart](https://savjee.be/blog/make-garage-door-opener-smart-shelly-esphome-home-assistant/)
- [How to create a Garage Door Opener in Home Assistant](https://leonardosmarthomemakers.com/how-to-create-a-garage-door-opener-in-home-assistant/)
  So my project was based on these materials.

I found out that:
1. [Home Assistant](https://www.home-assistant.io/) is the great platform for home automation and I decided to use it as a main controller
2. The cheapest and easiest way to run home assistant is on Raspberry Pi. Plus I already have Raspberry Pi with 12 inch touch screen. I'll use it for this project and for all following home automation endeavors
3. Door opener switch could be by Sonoff or Shelly. I decided to go with [Shelly 1](https://www.amazon.com/Shelly-Wireless-Automation-Android-Application/dp/B07NQNLDTD/ref=sr_1_2_sspa?keywords=shelly+1&qid=1673483956&sprefix=%2Caps%2C100&sr=8-2-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUExTlM4RzAzVUYyTzQ1JmVuY3J5cHRlZElkPUEwOTA0NzQyMjZQRlIzN1dOVkE0OCZlbmNyeXB0ZWRBZElkPUEwMjcxODU5SUJIVVRUWTRURlBXJndpZGdldE5hbWU9c3BfYXRmJmFjdGlvbj1jbGlja1JlZGlyZWN0JmRvTm90TG9nQ2xpY2s9dHJ1ZQ==) for 19$
4. There is wide range of door sensors, I thought to buy wireless (Zigbee) ones and stopped on [Aqara Door and Window Sensor](https://www.amazon.com/gp/product/B07D37VDM3/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1) for 18$

# Assembly

## Switch

Installation didn't take a lot of time. It looks like:
![](/assets/Pasted image 20230118164301.png)

After Shelly 1 installation, a new WiFi network `shelly-<id>` is available that you can connect and configure the device by opening URL http://192.168.33.1
I configured WiFi network on the device to use my home network and found new device in home assistant

## Sensors

Installation of these sensors where very easy:

1. Open the box
2. Press button for 3 seconds and wait for blinking blue light
3. Open Home assistant and open `ConBee II` -> `devices`
4. Click on "Add Device" button
5. Attach sensors to the garage door

![](/assets/Pasted image 20230114213212.png){: width="500" }
![](/assets/Pasted image 20230114213307.png)




# Home Assistant

## Setup

I setup home assistant on RaspberryPi according to instructions from  https://www.home-assistant.io/installation/raspberrypi/

In addition to the HA core I installed
- [Red Node AddOn](https://community.home-assistant.io/t/home-assistant-community-add-on-node-red/55023). I use it to create logic, flows in the home assistant.
- [Mosquitto broker](https://www.home-assistant.io/integrations/mqtt/) for MQTT protocol communication

Main dashboard looks like:

![](/assets/Pasted image 20230126194144.png)


## Automations

First I notice that when I enable the switch one time it disable the button in the garage that opens the door. It requires to toggle the Shelly switch one more time to enable the button on a wall.
So, I decided to create a button on main dashboard that toggle the switch twice with 1/2 second delay. In order to create the button I added helper button:
![](/assets/Pasted image 20230126193331.png)

The flow in Node Red looks like:

![](/assets/Pasted image 20230126193951.png)

1. Event:state node "Button was pressed" is associated with the created button
2. Call service node "Toggle garage door"
    - Domain: switch
    - Service: toggle
    - Device: < garage door switch >
    - Entity: < switch.garage_opener >
    - Data: on
3. Wait until node "Wait 1/2 second" wait 0.5 seconds and then
4. Call service node "Second switch" is copy of node #2

Second automation that I decided to create is inception of security system.

1. I created Helper Toggle switch in HA
2. Created flow that checks if the toggle is on and garage door got opened - i get the email

The flow looks like

![](/assets/Pasted image 20230126194438.png)

1. evant:state node "Garage door got opened" monitors if sensor detects open door
2. current state "Alarm system enabled" retrieves value of `input_boolean.enable_security` (the toggle that I created before)
3. Switch "Is On" checks that value that we retrieved from previous step is `on`
4. send email node send my an email...


# Conclusion

Not bad solution for under `40$`. Well, if we take into account also Raspberry Pi than whole project could cost bellow `200$`. However, I can imagine realm of possibility in home automation field based on single Home Assistant platform.

Also I decided to buy subscription https://www.home-assistant.io/cloud/ `65$` / year; it allows me to expose my home assistant to the internet. As a result I can use Home Assistant application on my phone anywhere:

![](/assets/Screenshot 2023-01-26 at 7.55.58 PM.jpeg){: width="300" }





