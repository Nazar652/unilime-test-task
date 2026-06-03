import json
import logging
from types import SimpleNamespace

from extensions import logging as app_logging


def make_record(**extra) -> logging.LogRecord:
    record = logging.LogRecord(
        name='tempmail.test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='hello %s',
        args=('world',),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_expected_fields():
    record = make_record(request_id='abc123')

    payload = json.loads(app_logging.JsonFormatter().format(record))

    assert payload['level'] == 'INFO'
    assert payload['logger'] == 'tempmail.test'
    assert payload['message'] == 'hello world'
    assert payload['request_id'] == 'abc123'


def test_json_formatter_defaults_request_id_when_absent():
    payload = json.loads(app_logging.JsonFormatter().format(make_record()))

    assert payload['request_id'] == '-'


def test_request_id_filter_sets_dash_outside_request(monkeypatch):
    monkeypatch.setattr(app_logging, 'has_request_context', lambda: False)
    record = make_record()

    assert app_logging.RequestIdFilter().filter(record) is True
    assert record.request_id == '-'


def test_current_request_id_reads_from_context(monkeypatch):
    monkeypatch.setattr(app_logging, 'has_request_context', lambda: True)
    monkeypatch.setattr(app_logging, 'g', SimpleNamespace(request_id='req-7'))

    assert app_logging.current_request_id() == 'req-7'


def test_new_request_id_is_short_hex():
    request_id = app_logging.new_request_id()

    assert len(request_id) == 8
    assert app_logging.new_request_id() != request_id


def test_elapsed_ms_zero_without_start(monkeypatch):
    monkeypatch.setattr(app_logging, 'g', SimpleNamespace())

    assert app_logging.elapsed_ms() == 0


def test_elapsed_ms_computes_from_start(monkeypatch):
    monkeypatch.setattr(app_logging, 'time', SimpleNamespace(perf_counter=lambda: 5.0))
    monkeypatch.setattr(app_logging, 'g', SimpleNamespace(request_started=4.5))

    assert app_logging.elapsed_ms() == 500
