"""Tests for 20260720_5 — website health check core functions."""

import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_core = __import__("20260720_5")
CheckResult = _core.CheckResult
check_website_core = _core.check_website_core
validate_timeout = _core.validate_timeout
validate_url = _core.validate_url


class TestValidateUrl:
    def test_valid_https(self) -> None:
        assert validate_url("https://example.com/") == "https://example.com/"

    def test_valid_http(self) -> None:
        assert validate_url("http://example.com") == "http://example.com"

    def test_strips_whitespace(self) -> None:
        assert validate_url("  https://example.com/  ") == "https://example.com/"

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="不能空白"):
            validate_url("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="不能空白"):
            validate_url("   ")

    def test_no_scheme_raises(self) -> None:
        with pytest.raises(ValueError, match="http:// 或 https://"):
            validate_url("example.com")

    def test_ftp_scheme_raises(self) -> None:
        with pytest.raises(ValueError, match="http:// 或 https://"):
            validate_url("ftp://example.com/")


class TestValidateTimeout:
    def test_valid_timeout(self) -> None:
        assert validate_timeout("30000") == 30000

    def test_strips_whitespace(self) -> None:
        assert validate_timeout("  15000  ") == 15000

    def test_minimum_boundary(self) -> None:
        assert validate_timeout("1000") == 1000

    def test_maximum_boundary(self) -> None:
        assert validate_timeout("120000") == 120000

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="必須是整數"):
            validate_timeout("")

    def test_non_numeric_raises(self) -> None:
        with pytest.raises(ValueError, match="必須是整數"):
            validate_timeout("thirty")

    def test_too_low_raises(self) -> None:
        with pytest.raises(ValueError, match="至少需要 1000"):
            validate_timeout("999")

    def test_too_high_raises(self) -> None:
        with pytest.raises(ValueError, match="不能超過 120000"):
            validate_timeout("120001")


class TestCheckResult:
    def test_defaults(self) -> None:
        r = CheckResult(url="https://example.com/")
        assert r.url == "https://example.com/"
        assert r.http_status is None
        assert r.success is True
        assert r.error_message == ""

    def test_success_false_sets_error(self) -> None:
        r = CheckResult(url="https://example.com/", success=False, error_message="timeout")
        assert not r.success
        assert r.error_message == "timeout"


class TestCheckWebsiteCore:
    def test_successful_check(self, tmp_path: Path) -> None:
        mock_page = MagicMock()
        mock_page.title.return_value = "Test Title"
        mock_page.url = "https://example.com/"

        mock_heading = MagicMock()
        mock_heading.inner_text.return_value = "Test Heading"
        mock_page.get_by_role.return_value.first = mock_heading

        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response

        mock_browser = MagicMock()
        mock_browser.new_page.return_value = mock_page

        mock_browser_type = MagicMock()
        mock_browser_type.launch.return_value = mock_browser

        mock_playwright = MagicMock()
        mock_playwright.chromium = mock_browser_type

        with (
            patch.object(_core, "sync_playwright") as mock_sp,
            patch.object(_core, "OUTPUT_DIR", tmp_path),
            patch.object(_core.time, "strftime", return_value="20260720_120000"),
            patch.object(_core.time, "monotonic", side_effect=[100.0, 102.5]),
        ):
            mock_sp.return_value.__enter__.return_value = mock_playwright
            result = check_website_core(
                url="https://example.com/",
                browser_name="chromium",
                headless=True,
                timeout_ms=30000,
            )

        assert result.success is True
        assert result.http_status == 200
        assert result.response_time_ms == 2500.0
        assert result.page_title == "Test Title"
        assert result.main_heading == "Test Heading"
        assert result.final_url == "https://example.com/"
        assert result.screenshot_path is not None
        assert "check_20260720_120000_chromium.png" in result.screenshot_path

    def test_failed_check_returns_error(self, tmp_path: Path) -> None:
        with (
            patch.object(_core, "sync_playwright") as mock_sp,
            patch.object(_core, "OUTPUT_DIR", tmp_path),
        ):
            mock_sp.return_value.__enter__.side_effect = Exception("Connection refused")
            result = check_website_core(
                url="https://invalid.local/",
                browser_name="chromium",
                headless=True,
                timeout_ms=5000,
            )

        assert result.success is False
        assert "Connection refused" in result.error_message
        assert result.http_status is None
