#!/usr/local/bin/python3
# coding: utf-8

from . import DOMAIN, SIGNAL_UPDATE_DATA
from homeassistant.const import CONF_MAC
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

ATTR_WATTS = 'energy_alltime_kwh'
ATTR_WORK_ALLTIME = 'working_time_h'
ATTR_TIMES = 'number_starts'
ATTR_SYNC = 'last_sync'

async def async_setup_entry(hass, config_entry, async_add_entities):
    kettler = hass.data[DOMAIN][config_entry.entry_id]

    if kettler._type in [0, 1, 2, 3, 4]:
        async_add_entities([RedmondSensor(kettler)], True)

    elif kettler._type == 5:
        async_add_entities([RedmondCooker(kettler)], True)

class RedmondSensor(Entity):
    def __init__(self, kettler):
        self._kettler = kettler
        self._name = 'Status ' + self._kettler._name
        self._icon = 'mdi:toggle-switch-off'
        self._state = ''
        self._sync = ''

    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, SIGNAL_UPDATE_DATA, self._handle_update))

    def _handle_update(self):
        self._state = 'OFF'

        if self._kettler._status == '02':
            if self._kettler._type in [3, 4]:
                self._state = 'ON'
            elif self._kettler._mode == '00':
                self._state = 'BOIL'
            elif self._kettler._mode == '01':
                self._state = 'HEAT'
            elif self._kettler._mode == '03':
                self._state = 'LIGHT'

        self._sync = str(self._kettler._time_upd)
        self.schedule_update_ha_state()

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return 'mdi:toggle-switch' if self._state != 'OFF' else self._icon

    @property
    def available(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            ATTR_TIMES: self._kettler._times,
            ATTR_WATTS: round(self._kettler._Watts / 1000, 2),
            ATTR_WORK_ALLTIME: self._kettler._alltime,
            ATTR_SYNC: self._sync
        }

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'


class RedmondCooker(Entity):

    def __init__(self, kettler):
        self._icon = 'mdi:book-open'
        self._kettler = kettler
        self._name = 'Status ' + kettler._name
        self._state = ''
        self._sync = ''
        self._timer_prog = ''
        self._timer_curr = ''

    async def async_added_to_hass(self):
        self._handle_update()
        self.async_on_remove(async_dispatcher_connect(self._kettler.hass, SIGNAL_UPDATE_DATA, self._handle_update))

    def _handle_update(self):
        self._state = 'OFF'

        if self._kettler._status == '01':
            self._state = 'PROGRAM'
        elif self._kettler._status == '02':
            self._state = 'ON'
        elif self._kettler._status == '04':
            self._state = 'HEAT'
        elif self._kettler._status == '05':
            self._state = 'DELAYED START'

        self._sync = str(self._kettler._time_upd)
        self._timer_prog = str(self._kettler._ph) + ':' + str(self._kettler._pm)
        self._timer_curr = str(self._kettler._th) + ':' + str(self._kettler._tm)

        self.schedule_update_ha_state()

    @property
    def device_info(self):
        return {
            "connections": {
                ("mac", self._kettler._mac)
            }
        }

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def available(self):
        return True

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        attributes = {
            'sync':str(self._sync),
            'Timer PROG':self._timer_prog,
            'Timer CURR':self._timer_curr}
        return attributes

    @property
    def unique_id(self):
        return f'{DOMAIN}[{self._kettler._mac}][{self._name}]'
