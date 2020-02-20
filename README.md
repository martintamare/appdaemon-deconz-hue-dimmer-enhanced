# appdaemon-deconz-hue-dimmer-enhanced

AppDaemon app to control hue dimmer switch in a very flexible way.

First intend was to be able to detect multiple press so as to play different action.
Code is rought and very generic, it works for my use case ;)

## Installation

Download the `deconz_hue_dimmer_enhanced` directory from inside the `apps` directory here to your local `apps` directory, then add the configuration to enable the `deconz_hue_dimmer_enhanced` module.

## App configuration

```yaml
hue_dimmer:
  module: deconz_hue_dimmer_enhanced
  class: DeconzHueDimmerEnhanced
  switch_id: id_of_the_switch_in_deconz
  delay_for_modes: 1500  {# Delay for detection of multiple press #}

  light_ids:
    - light.light_1
    - light.light_2

  {# Multiple press will cycle actions #}
  {# If light is off, last state is restore #}
  button_on_short_press_actions:
    - service: light/turn_on
      args:
        color_name: blue
    - service: light/turn_on
      args:
        color_name: orange
    - service: light/turn_on
      args:
        color_name: green
    - service: light/turn_on
      args:
        color_name: red
    - service: light/turn_on
      args:
        color_name: yellow
    
  {# entity_id params in args override the default one #}
  {# In this case, first press will turn off light.light_1 and 2, second press all the lights #}
  button_off_short_press_actions:
    - service: light/turn_off
    - service: light/turn_off
      args:
        entity_id: all

  {# brightness_delta is a special keyword to smoothly managed brightness #}
  dim_up_short_press_actions:
    - service: light/turn_on
      args:
        transition: 1
        brightness_delta: 25
  dim_up_long_press_actions:
    - service: light/turn_on
      args:
        transition: 1
        brightness_delta: 25

  dim_down_short_press_actions:
    - service: light/turn_on
      args:
        transition: 1
        brightness_delta: -25
  dim_down_long_press_actions:
    - service: light/turn_on
      args:
        transition: 1
        brightness_delta: -25
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | The module name of the app.
`class` | False | string | | The name of the Class.
`delay_for_modes` | True | int | 1500 | The delay for multiple press detection.
`light_ids` | True | array | [] | Array for light to control.
`button_on_short_press_actions` | True | array | [] | Configuration the action for the button.
`button_on_long_press_actions` | True | array | [] | Configuration the action for the button.
`dim_up_short_press_actions` | True | array | [] | Configuration the action for the button.
`dim_up_long_press_actions` | True | array | [] | Configuration the action for the button.
`dim_down_short_press_actions` | True | array | [] | Configuration the action for the button.
`dim_down_long_press_actions` | True | array | [] | Configuration the action for the button.
`button_off_short_press_actions` | True | array | [] | Configuration the action for the button.
`button_off_long_press_actions` | True | array | [] | Configuration the action for the button.
