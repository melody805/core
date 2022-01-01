"""Tests for the CPU Speed config flow."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.cpuspeed.const import DOMAIN
from homeassistant.config_entries import SOURCE_IMPORT, SOURCE_USER
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import (
    RESULT_TYPE_ABORT,
    RESULT_TYPE_CREATE_ENTRY,
    RESULT_TYPE_FORM,
)

from tests.common import MockConfigEntry


async def test_full_user_flow(
    hass: HomeAssistant,
    mock_cpuinfo_config_flow: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the full user configuration flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("step_id") == SOURCE_USER
    assert "flow_id" in result

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )

    assert result2.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result2.get("title") == "CPU Speed"
    assert result2.get("data") == {}

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_cpuinfo_config_flow.mock_calls) == 1


async def test_already_configured(
    hass: HomeAssistant,
    mock_cpuinfo_config_flow: MagicMock,
    mock_setup_entry: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test we abort if already configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result.get("type") == RESULT_TYPE_ABORT
    assert result.get("reason") == "already_configured"

    assert len(mock_setup_entry.mock_calls) == 0
    assert len(mock_cpuinfo_config_flow.mock_calls) == 0


async def test_import_flow(
    hass: HomeAssistant,
    mock_cpuinfo_config_flow: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test the import configuration flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_IMPORT},
        data={CONF_NAME: "Frenck's CPU"},
    )

    assert result.get("type") == RESULT_TYPE_CREATE_ENTRY
    assert result.get("title") == "Frenck's CPU"
    assert result.get("data") == {}

    assert len(mock_setup_entry.mock_calls) == 1
    assert len(mock_cpuinfo_config_flow.mock_calls) == 1


async def test_not_compatible(
    hass: HomeAssistant,
    mock_cpuinfo_config_flow: MagicMock,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test we abort the configuration flow when incompatible."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result.get("type") == RESULT_TYPE_FORM
    assert result.get("step_id") == SOURCE_USER
    assert "flow_id" in result

    mock_cpuinfo_config_flow.return_value = {}
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )

    assert result2.get("type") == RESULT_TYPE_ABORT
    assert result2.get("reason") == "not_compatible"

    assert len(mock_setup_entry.mock_calls) == 0
    assert len(mock_cpuinfo_config_flow.mock_calls) == 1