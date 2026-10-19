from __future__ import annotations

from datetime import date

import pytest

from contract_reviewer.tools import date_calculator, interest_calculator


def test_as_days_handles_missing_value():
    assert date_calculator.as_days(None) == 0
    assert date_calculator.as_days('') == 0
    assert date_calculator.as_days(90) == 90


def test_working_days_between_excludes_start_and_weekends():
    monday = date(2026, 10, 19)
    friday = date(2026, 10, 23)
    assert date_calculator.working_days_between(monday, friday) == 4
    assert date_calculator.working_days_between(friday, monday) == -4


def test_annualized_rate_and_lpr_cap():
    rate = interest_calculator.annualized_rate(100000, 5000, 365)
    assert rate == pytest.approx(0.05)
    assert interest_calculator.lpr_cap(0.0345) == pytest.approx(0.138)
    assert interest_calculator.exceeds_lpr_cap(rate, 0.0345) is False
    assert interest_calculator.exceeds_lpr_cap(0.2, 0.0345) is True


def test_annualized_rate_rejects_invalid_input():
    with pytest.raises(ValueError):
        interest_calculator.annualized_rate(0, 1000, 30)
