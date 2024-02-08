import time
from pico_lte.core import PicoLTE
from pico_lte.common import debug
from pico_lte.utils.status import Status
from machine import RTC
import json
from config import *

rtc = RTC()

# get access credentials
with open('access.txt', 'r') as access_file:
    pword = access_file.read()


def gps_time_to_rtc_time(result):
    # now we have to process the date time to get UNIX epoch
    # this is very fragile and breaks if you don't get exactly the right GPS signal - to do:  make robust

    # convert GPS time stamp into UTC epoch time
    gps_time = result['response'][0].replace('+QGPSLOC: ', "").split(",")
    # parse the date time
    hhmmss_str = gps_time[0].split(".")[0]
    hours, minutes, seconds = [int(hhmmss_str[i:i + 2]) for i in range(0, len(hhmmss_str), 2)]
    ddmoyy_str = gps_time[-2]
    day, month, year = [int(ddmoyy_str[i:i + 2]) for i in range(0, len(ddmoyy_str), 2)]
    year = year + 2000
    return (year, month, day, 0, hours, minutes, seconds, 0)


def blink_neopixel(colorOne, colorTwo):
    for i in range(100):
        if i % 10 == 0:
            picoLTE.peripherals.adjust_neopixel(*colorOne)
        else:
            picoLTE.peripherals.adjust_neopixel(*colorTwo)
        time.sleep_ms(25)


# loop while power is on
# todo:  set up timer where light is only green if you've pushed a position in the last 5 minutes, for now just learning
last_fix_ingest = 0  # clean slate when we start up

picoLTE = PicoLTE()
picoLTE.http.set_server_url(POINT_INGEST_URL)
picoLTE.http.set_content_type(4)

blink_neopixel(STATUS_ERROR_COLOR, ALERT_COLOR)
picoLTE.peripherals.adjust_neopixel(*ALERT_COLOR)
while True:

    # First turn on GPS, be patient this takes a little bit
    picoLTE.gps.set_priority(0)
    time.sleep(3)
    picoLTE.gps.turn_on()

    debug.info("Trying to fix GPS...")
    for _ in range(0, 45):
        result = picoLTE.gps.get_location()

        if result["status"] == Status.SUCCESS:
            debug.debug("GPS Fixed. Getting location data...")
            loc = result.get("value")
            lat, lon = loc
            debug.info(result)
            break
        else:
            # if you have no fix, make the light red
            debug.info(result)
            debug.info(f'time since last ingest {time.time() - last_fix_ingest}')

        time.sleep(2)

    # if time since the last
    if time.time() - last_fix_ingest >= MAX_TIME_BETWEEN_UPDATES // 2:
        # turn the smart pixel blue to indicate you have a fix, but it hasn't sent yet
        picoLTE.peripherals.adjust_neopixel(*SENDING_COLOR)

        # reset the clock with
        try:
            rtc.datetime(gps_time_to_rtc_time(result))
        except:
            # if that didn't work, just continue to the top of the loop again
            continue

        data = {
            "asset": ASSET_NAME,
            'password': pword,
            "timestamp": time.time(),
            "latitude": lat, "longitude": lon,
            "data": result['response']
        }

        # Go to WWAN prior mode and turn off GPS.
        picoLTE.gps.set_priority(1)
        picoLTE.gps.turn_off()

        # something may be going wrong in here... not sure what - debugs.info for information as I'm running it
        debug.info("Sending message to the server...")
        debug.info("Connecting to Cell Network:")
        debug.info(f'getting network status: {picoLTE.network.check_network_registration()}')
        debug.info(f"Setting Context ID: {picoLTE.http.set_context_id()}")

        result = picoLTE.http.post(data=json.dumps(data))
        debug.info(result)

        if result["status"] == Status.SUCCESS:
            # turn the neopixel to green!  cool
            picoLTE.peripherals.adjust_neopixel(*STATUS_GOOD_COLOR)

            debug.info("Message sent successfully.")
            last_fix_ingest = time.time()
        else:
            picoLTE.peripherals.adjust_neopixel(*STATUS_ERROR_COLOR)
            debug.error(result["status"])

    # blink neopixel between error and red if you have exceeded the allowable time
    if time.time() - last_fix_ingest >= MAX_TIME_BETWEEN_UPDATES:
        blink_neopixel(STATUS_ERROR_COLOR, ALERT_COLOR)

    time.sleep(30)  # 30 seconds between each request.

