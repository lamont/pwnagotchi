# Based on ups_lite.py from https://github.com/evilsocket/pwnagotchi
#
# Assumes the lifepo4wered-cli (and daemon) have been installed via
# https://github.com/xorbit/lifepo4wered-Pi
#
# For more details on the powered UPS plus basic RTC:
# https://lifepo4wered.com/lifepo4wered-pi.html
import logging
import struct
import subprocess

from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi


# TODO: add enable switch in config.yml an cleanup all to the best place
class UPS:
    def __init__(self):
        # There's not really anything to do here but I'm keeping the structure from the plugin I copied
        self.ready = True

    def voltage(self):
        try:
            process = subprocess.run(['/usr/local/bin/lifepo4wered-cli', 'get', 'vbat'],
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
            millivolts = int(process.stdout.rstrip())
            return millivolts / 1000
        except:
            return 0.0

    def shutdown_threshold_voltage(self):
        try:
            process = subprocess.run(['/usr/local/bin/lifepo4wered-cli', 'get', 'vbat_shdn'],
                                     stdout=subprocess.PIPE,
                                     universal_newlines=True)
            millivolts = int(process.stdout.rstrip())
            return millivolts / 1000
        except:
            return 0.0


class LiFePO4wered(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that will add a voltage indicator for the LiFePO4wered Pi+'

    def __init__(self):
        self.ups = None

    def on_loaded(self):
        self.ups = UPS()

    def on_ui_setup(self, ui):
        ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='0%/0V', position=(ui.width() / 2 + 10, 0),
                                           label_font=fonts.Bold, text_font=fonts.Small))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('ups')

    def on_ui_update(self, ui):
        voltage = self.ups.voltage()
        ui.set('ups', format(voltage, '.3f'))
        if voltage <= self.ups.shutdown_threshold_voltage():
            logging.info('[LiFePO4wered] Empty battery (<= %s%%): shutting down' % self.ups.shutdown_threshold_voltage())
            ui.update(force=True, new_data={'status': 'Battery exhausted, bye ...'})
            # pwnagotchi.shutdown()
