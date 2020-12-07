# -*- coding: utf-8 -*-

"""This module contains the message class for the simulation platform resource state messages."""

from __future__ import annotations
from typing import Any, Dict, Union

from tools.exceptions.messages import MessageValueError
from tools.message.abstract import AbstractResultMessage
from tools.message.block import QuantityBlock
from tools.message.block import TimeSeriesBlock
from tools.message.block import ValueArrayBlock
from tools.tools import FullLogger

LOGGER = FullLogger(__name__)


class ResourceForecastPowerMessage(AbstractResultMessage):
    """Class containing all the attributes for a ResourceForecastPower message."""

    # message type for these messages
    CLASS_MESSAGE_TYPE = "ResourceForecast.Power"
    MESSAGE_TYPE_CHECK = True
    
    FORECAST_ATTRIBUTE = "Forecast"
    REAL_POWER_SERIES_NAMES = ["RealPower"]
    REAL_POWER_SERIES_UNIT = "kW"

    # Mapping from message JSON attributes to class attributes
    MESSAGE_ATTRIBUTES = {
        "Forecast": "real_power",
        "ResourceName": "resource_name"
    }
    OPTIONAL_ATTRIBUTES = []

    # attributes whose value should be a QuantityBlock and the expected unit of measure.
    QUANTITY_BLOCK_ATTRIBUTES = {}
    
    # attributes whose value should be a Array Block.
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES = {}
    
    # attributes whose value should be a Timeseries Block.
    TIMESERIES_BLOCK_ATTRIBUTES = ["Forecast",]

    MESSAGE_ATTRIBUTES_FULL = {
        **AbstractResultMessage.MESSAGE_ATTRIBUTES_FULL,
        **MESSAGE_ATTRIBUTES
    }
    OPTIONAL_ATTRIBUTES_FULL = AbstractResultMessage.OPTIONAL_ATTRIBUTES_FULL + OPTIONAL_ATTRIBUTES
    QUANTITY_BLOCK_ATTRIBUTES_FULL = {
        **AbstractResultMessage.QUANTITY_BLOCK_ATTRIBUTES_FULL,
        **QUANTITY_BLOCK_ATTRIBUTES
    }
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES_FULL = {
        **AbstractResultMessage.QUANTITY_ARRAY_BLOCK_ATTRIBUTES_FULL,
        **QUANTITY_ARRAY_BLOCK_ATTRIBUTES
    }
    
    TIMESERIES_BLOCK_ATTRIBUTES_FULL = (
        AbstractResultMessage.TIMESERIES_BLOCK_ATTRIBUTES_FULL +
        TIMESERIES_BLOCK_ATTRIBUTES
    )

    @property
    def resource_name(self) -> str:
        """The attribute for the name of resource that is forecasted."""
        return self.__resource_name

    @property
    def real_power(self) -> TimeSeriesBlock:
        """The attribute for real power of the resource."""
        return self.__real_power

    @resource_name.setter
    def resource_name(self, resource_name: str):
        """Set value for resource name that is forecasted."""
        if self._check_resource_name(resource_name):
            self.__resource_name = resource_name
        else:
            raise MessageValueError("Invalid value, {}, for attribute: resource_name".format(resource_name))

    @real_power.setter
    def real_power(self, real_power: Union[TimeSeriesBlock, Dict[str, Any]]):
        """Set value for real power.
        A string value is converted to a float. A float value is converted into a QuantityBlock with the default unit.
        A dict is converted to a QuantityBlock.
        Raises MessageValueError if value is missing or invalid: a QuantityBlock has the wrong unit, dict cannot be converted  or
        a string cannot be converted to float"""

        if self._check_real_power(real_power):
            self._set_timeseries_block_value(self.FORECAST_ATTRIBUTE, real_power)
            return
        else:
            raise MessageValueError("Invalid value, {}, for attribute: real_power".format(real_power))

    def __eq__(self, other: Any) -> bool:
        """Check that two ResourceForecastPowerMessages represent the same message."""
        return (
            super().__eq__(other) and
            isinstance(other, ResourceForecastPowerMessage) and
            self.resource_name == other.resource_name and
            self.real_power == other.real_power
        )

    @classmethod
    def _check_resource_name(cls, resource_name: str) -> bool:
        """Check that value for resource_name is valid i.e. a string."""
        return isinstance(resource_name, str)

    @classmethod
    def _check_real_power(cls, real_power: Union[TimeSeriesBlock, Dict[str, Any]]) -> bool:
        """Check that value for real power is valid."""
        return cls._check_timeseries_block(
            value=real_power, block_check=cls._check_real_power_block)
        
    @classmethod
    def _check_real_power_block(cls, real_power_block: TimeSeriesBlock) -> bool:
        block_series = real_power_block.series
        if len(block_series) != 1 or len(real_power_block.time_index) < 3:
            return False
        for real_power_series_name in cls.REAL_POWER_SERIES_NAMES:
            if real_power_series_name not in block_series:
                return False
            current_series = block_series[real_power_series_name]
            if current_series.unit_of_measure != cls.REAL_POWER_SERIES_UNIT or len(current_series.values) < 3:
                return False
        return True

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Union[ResourceForecastPowerMessage, None]:
        """Returns a class object created based on the given JSON attributes.
           If the given JSON is not validated returns None."""
        if cls.validate_json(json_message):
            return cls(**json_message)
        return None

ResourceForecastPowerMessage.register_to_factory()
