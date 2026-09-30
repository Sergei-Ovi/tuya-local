"""Tests for the lock entity."""

from unittest.mock import AsyncMock, Mock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tuya_local.const import (
    CONF_DEVICE_ID,
    CONF_PROTOCOL_VERSION,
    CONF_TYPE,
    DOMAIN,
)
from custom_components.tuya_local.helpers.device_config import get_config
from custom_components.tuya_local.lock import TuyaLocalLock, async_setup_entry

from .helpers import assert_device_properties_set, mock_device

RAYKUBE_DPS = {"9": "high", "46": True, "47": False}


def _make_raykube_lock(mocker):
    """Create a lock with both a lock dp and a code_unlock dp."""
    config = get_config("raykube_a1promax_lock")
    entity_config = next(
        entity for entity in config.all_entities() if entity.entity == "lock"
    )
    device = mock_device(RAYKUBE_DPS, mocker)
    return TuyaLocalLock(device, entity_config), device


@pytest.mark.asyncio
async def test_unlock_with_code_uses_code_unlock(mocker):
    """A supplied code is sent with code_unlock rather than the lock dp."""
    lock, device = _make_raykube_lock(mocker)

    # action 1, member 1, code "12345678", source 0
    async with assert_device_properties_set(device, {"61": "AQABMTIzNDU2NzgAAA=="}):
        await lock.async_unlock(code="12345678")


@pytest.mark.asyncio
async def test_unlock_without_code_uses_lock_dp(mocker):
    """Without a code, the lock dp is still used to unlock."""
    lock, device = _make_raykube_lock(mocker)

    async with assert_device_properties_set(device, {"46": False}):
        await lock.async_unlock()


PRIMEBRAS_DPS = {"46": True, "47": False}


@pytest.mark.asyncio
async def test_unlock_with_code_ignores_set_unlock_code(mocker):
    """A supplied code is sent with code_unlock even if set_unlock_code exists."""
    config = get_config("primebras_athenas_lock")
    entity_config = next(
        entity for entity in config.all_entities() if entity.entity == "lock"
    )
    device = mock_device(PRIMEBRAS_DPS, mocker)
    lock = TuyaLocalLock(device, entity_config)

    async with assert_device_properties_set(device, {"61": "AQABMTIzNDU2NzgAAA=="}):
        await lock.async_unlock(code="12345678")


@pytest.mark.asyncio
async def test_init_entry(hass):
    """Test the initialisation."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_TYPE: "goldair_gpph_heater",
            CONF_DEVICE_ID: "dummy",
            CONF_PROTOCOL_VERSION: "auto",
        },
    )
    # although async, the async_add_entities function passed to
    # async_setup_entry is called truly asynchronously. If we use
    # AsyncMock, it expects us to await the result.
    m_add_entities = Mock()
    m_device = AsyncMock()

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["dummy"] = {}
    hass.data[DOMAIN]["dummy"]["device"] = m_device

    await async_setup_entry(hass, entry, m_add_entities)
    assert type(hass.data[DOMAIN]["dummy"]["lock_child_lock"]) is TuyaLocalLock
    m_add_entities.assert_called_once()


@pytest.mark.asyncio
async def test_init_entry_fails_if_device_has_no_lock(hass):
    """Test initialisation when device has no matching entity"""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_TYPE: "smartplugv1",
            CONF_DEVICE_ID: "dummy",
            CONF_PROTOCOL_VERSION: "auto",
        },
    )
    # although async, the async_add_entities function passed to
    # async_setup_entry is called truly asynchronously. If we use
    # AsyncMock, it expects us to await the result.
    m_add_entities = Mock()
    m_device = AsyncMock()

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["dummy"] = {}
    hass.data[DOMAIN]["dummy"]["device"] = m_device
    try:
        await async_setup_entry(hass, entry, m_add_entities)
        assert False
    except ValueError:
        pass
    m_add_entities.assert_not_called()


@pytest.mark.asyncio
async def test_init_entry_fails_if_config_is_missing(hass):
    """Test initialisation when device has no matching entity"""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_TYPE: "non_existing",
            CONF_DEVICE_ID: "dummy",
            CONF_PROTOCOL_VERSION: "auto",
        },
    )
    # although async, the async_add_entities function passed to
    # async_setup_entry is called truly asynchronously. If we use
    # AsyncMock, it expects us to await the result.
    m_add_entities = Mock()
    m_device = AsyncMock()

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["dummy"] = {}
    hass.data[DOMAIN]["dummy"]["device"] = m_device
    try:
        await async_setup_entry(hass, entry, m_add_entities)
        assert False
    except ValueError:
        pass
    m_add_entities.assert_not_called()
