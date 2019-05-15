from textwrap import dedent

from overwatch_ping_agent.target_check import parse_ping_output


def test_parse_macos_ping_output():
    output = dedent('''\
        PING ip4.messa.cz (37.157.193.242): 56 data bytes
        64 bytes from 37.157.193.242: icmp_seq=0 ttl=55 time=9.916 ms
        64 bytes from 37.157.193.242: icmp_seq=1 ttl=55 time=9.307 ms
        64 bytes from 37.157.193.242: icmp_seq=2 ttl=55 time=9.511 ms

        --- ip4.messa.cz ping statistics ---
        3 packets transmitted, 3 packets received, 0.0% packet loss
        round-trip min/avg/max/stddev = 9.307/9.578/9.916/0.253 ms
    ''')
    assert parse_ping_output(output) == {
        'packet_loss': {
            '__check': {'state': 'green'},
            '__unit': 'percents',
            '__value': 0.0},
        'rtt': {
            'avg': {
                '__value': 9.578,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'max': {
                '__value': 9.916,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'min': {
                '__value': 9.307,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'stddev': 0.253}}


def test_parse_debian_ping_output():
    output = dedent('''\
        PING ip4.messa.cz (37.157.193.242) 56(84) bytes of data.
        64 bytes from 37.157.193.242: icmp_seq=1 ttl=59 time=11.7 ms
        64 bytes from 37.157.193.242: icmp_seq=2 ttl=59 time=11.4 ms
        64 bytes from 37.157.193.242: icmp_seq=3 ttl=59 time=11.3 ms

        --- ip4.messa.cz ping statistics ---
        3 packets transmitted, 3 received, 0% packet loss, time 2003ms
        rtt min/avg/max/mdev = 11.365/11.513/11.738/0.183 ms
    ''')
    assert parse_ping_output(output) == {
        'packet_loss': {
            '__check': {'state': 'green'},
            '__unit': 'percents',
            '__value': 0.0},
        'rtt': {
            'avg': {
                '__value': 11.513,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'max': {
                '__value': 11.738,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'min': {
                '__value': 11.365,
                '__unit': 'milliseconds',
                '__check': {'state': 'green'}},
            'stddev': 0.183}}
