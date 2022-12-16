"""Integrate with deSEC Dynamic DNS service at desec.io"""
import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.const import CONF_ACCESS_TOKEN, CONF_DOMAIN, CONF_PROTOCOL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "desec_dedyn"

UPDATE_INTERVAL = timedelta(minutes=10)

TIMEOUT = 10

# https://desec.readthedocs.io/en/latest/dyndns/update-api.html

#UPDATE_URL = "https://update6.dedyn.io"
UPDATE_URL = "https://update.dedyn.io"
CHECK_V4 = "https://checkipv4.dedyn.io"
CHECK_V6 = "https://checkipv6.dedyn.io"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DOMAIN): cv.string,
                vol.Required(CONF_ACCESS_TOKEN): cv.string,
                vol.Optional(CONF_PROTOCOL): vol.All(
                  cv.ensure_list, [cv.string]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    
    conf = config[DOMAIN]
    
    dom = conf.get(CONF_DOMAIN)
    
    auth_token = conf.get(CONF_ACCESS_TOKEN)
    
    ipv = conf.get(CONF_PROTOCOL)
    # _LOGGER.debug("IPs: %s", ipv)
    
    session = async_get_clientsession(hass)

    result = await _update_desec(hass, session, dom, auth_token, ipv)

    if result is False:
        return False

    async def update_domain_callback(now):
    
        await _update_desec(hass, session, dom, auth_token, ipv)

    async_track_time_interval(hass, update_domain_callback, UPDATE_INTERVAL)

    return True


async def _update_desec(hass, session, dom, auth_token, ipv):

    headers = {"Authorization": "Token " + auth_token}
    params = {"hostname": dom}
    
    if "ipv4" in ipv:
        resp4 = await session.get(CHECK_V4)
        params ["myipv4"] = await resp4.text()
    
    if "ipv6" in ipv:
        resp6 = await session.get(CHECK_V6)
        params ["myipv6"] = await resp6.text()  
    
    try:
        async with async_timeout.timeout(TIMEOUT):
          
            resp = await session.get(UPDATE_URL, params = params, headers = headers)
            body = await resp.text()

            if "good" in body:
                _LOGGER.debug("IP updated")
                return True
         
            if "throttl" in body:
                _LOGGER.warning("Request was throttled")
            
            if "Invalid token" in body:
                _LOGGER.error("Token is invalid")
            
            if "nohost" in body:
                _LOGGER.error("Domain is invalid")
            
    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to desec API")

    except asyncio.TimeoutError:
        _LOGGER.warning("Timeout from deSEC API at %s", dom)

    return False