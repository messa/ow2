from overwatch_http_check_agent.target_check import check_target_once

from datetime import timedelta
from pprint import pprint
from pytest import fixture, mark


@fixture
def sent_reports():
    return []


@fixture
def send_report(sent_reports):
    async def do_send_report(report):
        sent_reports.append(report)
    return do_send_report


@mark.asyncio
async def test_check_example_com(send_report, sent_reports):
    class Conf:
        default_label = {'dlkey': 'dlvalue'}
    class Target:
        url = 'https://example.com/'
        label = {'tlkey': 'tlvalue'}
        duration_threshold = timedelta(seconds=10)
        check_response_contains = None
    await check_target_once(
        conf=Conf(),
        target=Target(),
        interval_s=60,
        send_report=send_report)
    pprint(sent_reports, width=250)
    report, = sent_reports
    assert report['label'] == {
        'agent': 'http_check',
        'dlkey': 'dlvalue',
        'host': 'pm-mb.local',
        'tlkey': 'tlvalue',
        'url': 'https://example.com/',
    }
    assert not deep_contains(report, lambda obj: obj.get('state') == 'red')


def deep_contains(obj, check):
    if isinstance(obj, dict):
        if check(obj):
            return True
        for v in obj.values():
            if deep_contains(v, check):
                return True
    if isinstance(obj, list):
        for v in obj:
            if deep_contains(v, check):
                return True
    return False
