"""
Control pixel ring on ReSpeaker V2

sudo apt install python-mraa libmraa1
pip install pixel-ring

"""

import time

from pixel_ring import pixel_ring
import os

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


    pixel_ring.off()
    time.sleep(1)
