import time
from pico_lte.core import PicoLTE
from pico_lte.utils.debug import Debug
from pico_lte.utils.status import Status
from machine import RTC
import json
from config import *

rtc = RTC()
debug = Debug(channel=3, enabled=True, level=0)

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


def send_over_cell(device: PicoLTE,
                   payload: dict,
                   debugger: Debug = debug) -> dict:
    # send the payload over cell

    device.peripherals.adjust_neopixel(*SENDING_COLOR)

    # Go to WWAN prior mode and turn off GPS.
    device.gps.set_priority(1)
    device.gps.turn_off()

    debugger.info("Sending message over cell")
    debugger.info(f'getting network status')
    device.network.check_network_registration()
    debugger.info(f"Setting Context ID")
    device.http.set_context_id()

    result = device.http.post(data=json.dumps(payload))
    debugger.info(result)
    return result


# loop while power is on
# todo:  set up timer where light is only green if you've pushed a position in the last 5 minutes, for now just learning
last_fix_ingest = 0  # clean slate when we start up
point_buffer = []

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
            debug.info("GPS Fixed. Getting location data...")
            picoLTE.peripherals.adjust_neopixel(*FIXED_COLOR)

            loc = result.get("value")
            lat, lon = loc
            debug.info("results:", result)

            try:
                # try to reset the clock, if that works great, if that doesn't
                # the result was actually in error
                rtc.datetime(gps_time_to_rtc_time(result))
                # add to the front of the list
                point_buffer.insert(
                    {"asset": ASSET_NAME,
                     'password': pword,
                     "timestamp": time.time(),
                     "latitude": lat, "longitude": lon,
                     "data": result['response']}, 0)

                break

            except:
                # if that didn't work, just continue to the top of the loop again
                result["status"] = Status.ERROR
                picoLTE.peripherals.adjust_neopixel(*ERROR_COLOR)
        else:
            # if you have no fix, log it
            debug.info(result)
            debug.info(f'time since last ingest {time.time() - last_fix_ingest}')
            picoLTE.peripherals.adjust_neopixel(*NOT_FIXED_COLOR)

        time.sleep(2)

    if point_buffer:
        # if we've got points in the point_buffer
        debug.info(f'{len(point_buffer)} points to send...')

        if time.time() - last_fix_ingest >= MAX_TIME_BETWEEN_UPDATES // 2:
            results = [send_over_cell(picoLTE, packet) for packet in point_buffer]
            debug.info(f'collating results')
            debug.info(results)
            results_status = [r['status'] for r in results]

            if results_status[0] == Status.SUCCESS:
                picoLTE.peripherals.adjust_neopixel(*STATUS_GOOD_COLOR)
                debug.info(f"Message sent successfully.")
                last_fix_ingest = time.time()
                # now remove the most recent point from the points buffer
            else:
                # try wifi
                picoLTE.peripherals.adjust_neopixel(*STATUS_ERROR_COLOR)

            # now clean up
            debug.info(f'tidy up!')
            for i, status in enumerate(results_status):
                if status == Status.SUCCESS:
                    point_buffer.pop(i)

    # blink neopixel between error and red if you have exceeded the allowable time
    if time.time() - last_fix_ingest >= MAX_TIME_BETWEEN_UPDATES:
        debug.error("cannot send data!")
        blink_neopixel(STATUS_ERROR_COLOR, ALERT_COLOR)

    time.sleep(30)  # 30 seconds between each request.

