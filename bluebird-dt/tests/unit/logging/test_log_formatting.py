import logging

from bluebird_dt.logger import ContextFilter, CustomFormatter

def test_logger_context_filter_and_formatter():
    """
    Test the logger's context filter and formatter
    """
    record = logging.LogRecord(
        name="bluebird_dt",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )

    context = {"scenario_name": "SCEN", "scenario_category": "CAT", "timestamp": "T"}
    ContextFilter(context).filter(record)

    formatter = CustomFormatter()
    formatted = formatter.format(record)
    assert "hello" in formatted
    assert "CAT" in formatted
    assert "SCEN" in formatted
    assert "T" in formatted