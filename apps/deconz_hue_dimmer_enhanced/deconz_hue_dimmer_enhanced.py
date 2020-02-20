import appdaemon.plugins.hass.hassapi as hass
import logging
import time

#
# App that allow flexible configuration of the hue dimmer as well as multiple button press
#
# Args:
#
#  delay_for_modes: 1500
#
#  light_ids:
#    - light.some_light
#
#  button_on_short_press_actions:
#    - service: light/turn_on
#      args:
#        color_name: blue
#    - service: light/turn_on
#      args:
#        color_name: orange
#    - service: light/turn_on
#      args:
#        color_name: green
#    - service: light/turn_on
#      args:
#        color_name: red
#    - service: light/turn_on
#      args:
#        color_name: yellow
#    
#  button_off_short_press_actions:
#    - service: light/turn_off
#    - service: light/turn_off
#      args:
#        entity_id: all
#
#  dim_up_short_press_actions:
#    - service: light/turn_on
#      args:
#        transition: 1
#        brightness_delta: 25
#  dim_up_long_press_actions:
#    - service: light/turn_on
#      args:
#        transition: 1
#        brightness_delta: 25
#
#  dim_down_short_press_actions:
#    - service: light/turn_on
#      args:
#        transition: 1
#        brightness_delta: -25
#  dim_down_long_press_actions:
#    - service: light/turn_on
#      args:
#        transition: 1
#        brightness_delta: -25

current_time = lambda: int(round(time.time() * 1000))

class SwitchButton():
    def __init__(self, delay, log):
        self.log = log
        self.state = 0
        self.last_short_press = None
        self.last_long_press = None
        self.delay = delay

    def debug(self, message):
        self.log(message, level='DEBUG')

    def short_press(self):
        press_time = current_time()
        if self.last_short_press is None:
            self.state += 1
            self.debug('+state {0}'.format(self.state))
        else:
            delay = press_time - self.last_short_press
            self.debug('delay since last press {0}'.format(delay))
            if delay > self.delay:
                self.state = 1
                self.debug('=state {0}'.format(self.state))
            else:
                self.state += 1
                self.debug('+state {0}'.format(self.state))
        self.last_short_press = press_time

    def long_press(self):
        self.log('long_press', level='DEBUG')


class DeconzHueDimmerEnhanced(hass.Hass):

    def initialize(self):
        self.log('Hello from DeconzHueDimmerEnhanced')

        # Args parsing
        self.switch_id = self.args['switch_id']
        self.light_ids = self.args.get('light_ids', [])
        self.delay_for_modes = self.args.get('delay_for_modes', 1500)
        self.button_on_short_press_actions= self.args.get('button_on_short_press_actions', [])
        self.button_on_long_press_actions= self.args.get('button_on_long_press_actions', [])
        self.button_off_short_press_actions= self.args.get('button_off_short_press_actions', [])
        self.button_off_long_press_actions= self.args.get('button_off_long_press_actions', [])
        self.dim_up_short_press_actions= self.args.get('dim_up_short_press_actions', [])
        self.dim_up_long_press_actions= self.args.get('dim_up_long_press_actions', [])
        self.dim_down_short_press_actions= self.args.get('dim_down_short_press_actions', [])
        self.dim_down_long_press_actions= self.args.get('dim_down_long_press_actions', [])

        self.log('switch_id: {0}'.format(self.switch_id))
        self.log('light_ids : {0}'.format(self.light_ids))

        # Listener using deconz_event
        # TODO : make this dynamic ?
        self.listen_event(self.deconz_event, 'deconz_event', id=self.switch_id)

        # Create our button
        self.button = []
        self.button.append(SwitchButton(delay=self.delay_for_modes, log=self.log))
        self.button.append(SwitchButton(delay=self.delay_for_modes, log=self.log))
        self.button.append(SwitchButton(delay=self.delay_for_modes, log=self.log))
        self.button.append(SwitchButton(delay=self.delay_for_modes, log=self.log))

    def debug(self, message):
        self.log(message, level='DEBUG')


    def trigger_action(self, action, entity_id):
        """Call the correct service on the current entity_id."""
        service = action['service']
        self.debug('service: {0}'.format(service))

        # Copy is important, we will manipulate those args later on
        service_args = action.get('args', {}).copy()
        self.debug('init args: {0}'.format(service_args))
        self.debug('init entity_id: {0}'.format(entity_id))

        # Additionnal keywords check
        if service == 'light/turn_on':
            if 'brightness_delta' in service_args:
                brightness_delta = service_args['brightness_delta']
                actual_brightness = self.get_state(entity_id, 'brightness')
                if actual_brightness is None:
                    actual_brightness = 0
                self.debug('brightness for {0} is {1}'.format(entity_id, actual_brightness))
                new_brightness = actual_brightness + brightness_delta
                if new_brightness < 0:
                    new_brightness = 0
                elif new_brightness > 255:
                    new_brightness = 255
                del service_args['brightness_delta']
                service_args['brightness'] = new_brightness

        if 'entity_id' in service_args:
            entity_id = service_args['entity_id']
            del service_args['entity_id']

        self.debug('final args: {0}'.format(service_args))
        self.debug('final entity_id: {0}'.format(entity_id))
        self.call_service(service, entity_id=entity_id, **service_args)



    def deconz_event(self, event_id, payload_event, *args):
        """Called on every event received from the switch."""
        # Get the event
        event = payload_event['event']

        # Extract button and code
        # Code
        # 0 : short_press
        # 1 : long_press
        # 2, 3 : short_press_stop, long_press_stop : unsed here
        button_index = int(str(event)[0]) - 1
        code = int(str(event)[1:4])

        # Handle the press to compute state of the button
        if code == 0:
            self.button[button_index].short_press()
        elif code == 1:
            self.button[button_index].long_press()

        # We only handle action on press
        if code not in [0, 1]:
            return

        button_actions = []
        if button_index == 0:
            if code == 0:
                button_actions = self.button_on_short_press_actions
            elif code == 1:
                button_actions = self.button_on_long_press_actions
        elif button_index == 1:
            if code == 0:
                button_actions = self.dim_up_short_press_actions
            elif code == 1:
                button_actions = self.dim_up_long_press_actions
        elif button_index == 2:
            if code == 0:
                button_actions = self.dim_down_short_press_actions
            elif code == 1:
                button_actions = self.dim_down_long_press_actions
        elif button_index == 3:
            if code == 0:
                button_actions = self.button_off_short_press_actions
            elif code == 1:
                button_actions = self.button_off_long_press_actions

        number_of_actions = len(button_actions)
        if number_of_actions == 0:
            self.debug('No action defined')
            return

        state = self.button[button_index].state
        action_index = (state % number_of_actions) - 1
        if action_index < 0:
            action_index = number_of_actions - 1

        action = button_actions[action_index]
        self.debug('Current action to trigger: {0}'.format(action))
        
        # Additionnal check to recover last state
        # TODO: add parameter ?
        if button_index == 0 and action_index == 0:
            for light_id in self.light_ids:
                light_state = self.get_state(light_id)
                if light_state == 'off':
                    self.turn_on(light_id)
                else:
                    self.trigger_action(action, light_id)
        else:
            for light_id in self.light_ids:
                self.trigger_action(action, light_id)
        return
