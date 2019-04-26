from textwrap import dedent
from yaml import safe_dump as yaml_dump

from overwatch_hub.model.helpers import parse_state


def test_parse_simple_state():
    state = '''
        {
            "cpu": {
                "count": {
                    "logical": 4,
                    "physical": 2
                },
                "times": {
                    "user": 21979.35,
                    "system": 11476.59,
                    "idle": 220918.71
                },
                "stats": {
                    "ctx_switches": 280052,
                    "interrupts": 700105,
                    "soft_interrupts": 143144019,
                    "syscalls": 1472139
                }
            },
            "load": {
                "01m": 1.67,
                "05m": 1.85,
                "15m": 1.94
            },
            "uptime": null
        }
    '''
    parsed = parse_state(state)
    assert yaml_dump(parsed) == dedent('''\
        - items:
          - items:
            - key: logical
              value: 4
            - key: physical
              value: 2
            key: count
          - items:
            - key: user
              value: 21979.35
            - key: system
              value: 11476.59
            - key: idle
              value: 220918.71
            key: times
          - items:
            - key: ctx_switches
              value: 280052
            - key: interrupts
              value: 700105
            - key: soft_interrupts
              value: 143144019
            - key: syscalls
              value: 1472139
            key: stats
          key: cpu
        - items:
          - key: 01m
            value: 1.67
          - key: 05m
            value: 1.85
          - key: 15m
            value: 1.94
          key: load
        - key: uptime
          value: null
    ''')


def test_parse_complex_state_value():
    state = '''
        {
            "free_bytes": {
                "__value": 65315635200,
                "__check": {
                    "state": "green"
                }
            }
        }
    '''
    parsed = parse_state(state)
    assert yaml_dump(parsed) == dedent('''\
      - check:
          state: green
        counter: null
        key: free_bytes
        unit: null
        value: 65315635200
        watchdog: null
    ''')


def test_parse_complex_state_value_with_metadata():
    state = '''
        {
            "user": {
                "__value": 65315635200,
                "__unit": "seconds",
                "__counter": true,
                "__check": {
                    "state": "green"
                }
            }
        }
    '''
    parsed = parse_state(state)
    assert yaml_dump(parsed) == dedent('''\
      - check:
          state: green
        counter: true
        key: user
        unit: seconds
        value: 65315635200
        watchdog: null
    ''')
