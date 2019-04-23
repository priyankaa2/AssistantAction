#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import requests
import time

from pixel_ring import pixel_ring
import os

from hermes_python.hermes import Hermes
from hermes_python.ontology import *

pixel_ring.set_brightness(20)

if __name__ == '__main__':
    while True:

        try:
	        pixel_ring.set_color_palette(0x9900ff, 0xff00ff)
            pixel_ring.wakeup()
            time.sleep(3)
            pixel_ring.think()
	        pixel_ring.spin()
	        time.sleep(3)
            pixel_ring.speak()
            time.sleep(3)
            pixel_ring.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break

class SnipsMPU(object):
    def __init__(self, i18n, mqtt_addr, site_id, relay, sht31):
        self.THRESHOLD_INTENT_CONFSCORE_DROP = 0.3
        self.THRESHOLD_INTENT_CONFSCORE_TAKE = 0.6

        self.__i18n = i18n
        self.__site_id = site_id
        self.__relay = relay
        self.__sht31 = sht31

        self.__mqtt_addr = mqtt_addr

    def check_site_id(handler):
        @functools.wraps(handler)
        def wrapper(self, hermes, intent_message):
            if intent_message.site_id != self.__site_id:
                return None
            else:
                return handler(self, hermes, intent_message)
        return wrapper

    def check_confidence_score(handler):
        @functools.wraps(handler)
        def wrapper(self, hermes, intent_message):
            if handler is None:
                return None
            if intent_message.intent.confidence_score < self.THRESHOLD_INTENT_CONFSCORE_DROP:
                hermes.publish_end_session(
                    intent_message.session_id,
                    ''
                )
                return None
            elif intent_message.intent.confidence_score <= self.THRESHOLD_INTENT_CONFSCORE_TAKE:
                hermes.publish_end_session(
                    intent_message.session_id,
                    self.__i18n.get('error.doNotUnderstand')
                )
                return None
            return handler(self, hermes, intent_message)
        return wrapper

    @check_confidence_score
    @check_site_id
    def handler_relay_turn_on(self, hermes, intent_message):
        print("Light Turned On")
        self.__relay.turn_on()
        hermes.publish_end_session(intent_message.session_id,self.__i18n.get('relayTurnOn'))
        response_lightson = requests.get('http://192.168.87.24:8081/sunits/lights_on')
        print(response_lightson)

    @check_confidence_score
    @check_site_id
    def handler_relay_turn_off(self, hermes, intent_message):
        print("Light Turned Off")
        self.__relay.turn_off()
        hermes.publish_end_session(intent_message.session_id,self.__i18n.get('relayTurnOff'))
        response_lightsoff = requests.get('http://192.168.87.24:8081/sunits/lights_off')
        print(response_lightsoff)

    @check_confidence_score
    @check_site_id
    def handler_get_unit(self, hermes, intent_message):
        print("Get Unit")
        self.__relay.unit_get()
        hermes.publish_end_session(intent_message.session_id, "Getting the bed")
        response_get_bed = requests.post('http://192.168.87.24:8081/sunits/switch_mode', json={'mode':'night', 'safety_mode':0})
        json_response_get_bed = response_get_bed.json()
        print(json_response_get_bed)
        #house_room = intent_message.slots.house_room.first().value # We extract the value from the slot "house_room"

    @check_confidence_score
    @check_site_id
    def handler_take_unit(self, hermes, intent_message):
        print("Take Unit")
        self.__relay.unit_take()
        hermes.publish_end_session(intent_message.session_id,"Okay.")
        response_raise_all = requests.post('http://192.168.87.24:8081/sunits/raise_all')
        #json_response_raise_all = response_raise_all.json()
        print(response_raise_all)

    @check_confidence_score
    @check_site_id
    def handler_check_humidity(self, hermes, intent_message):
        print("Humidity Check")
        humidity = self.__sht31.get_humidity_string()
        hermes.publish_end_session(intent_message.session_id,self.__i18n.get('checkHumidity', {"humidity": humidity}))

    @check_confidence_score
    @check_site_id
    def handler_check_temperature(self, hermes, intent_message):
        print("Temperature Check")
        temperature = self.__sht31.get_temperature_string()
        hermes.publish_end_session(intent_message.session_id,self.__i18n.get('checkTemperature', {"temperature": temperature}))

    def start_block(self):
        with Hermes(self.__mqtt_addr) as h:
            h.subscribe_intent(
                'pri2:relayTurnOn',
                self.handler_relay_turn_on
            ) \
             .subscribe_intent(
                'pri2:relayTurnOff',
                self.handler_relay_turn_off
            ) \
             .subscribe_intent(
                'pri2:getUnit',
                self.handler_get_unit
            ) \
            .subscribe_intent(
               'pri2:takeUnit',
               self.handler_take_unit
           ) \
             .subscribe_intent(
                'pri2:checkHumidity',
                self.handler_check_humidity
            ) \
             .subscribe_intent(
                'pri2:checkTemperature',
                self.handler_check_temperature
            ) \
             .start()
