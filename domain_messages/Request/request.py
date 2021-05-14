# -*- coding: utf-8 -*-

"""This module contains the message class for the simulation platform request messages."""

from __future__ import annotations
from typing import Union, List, Dict, Any, Tuple

from tools.exceptions.messages import MessageValueError
from tools.message.abstract import AbstractResultMessage
from tools.tools import FullLogger

import datetime
from tools.datetime_tools import to_iso_format_datetime_string
from tools.exceptions.messages import MessageDateError
from tools.message.block import QuantityBlock

LOGGER = FullLogger(__name__)


class RequestMessage(AbstractResultMessage):
    """Class containing all the attributes for a Request message."""

    # message type for these messages
    CLASS_MESSAGE_TYPE = "Request"
    MESSAGE_TYPE_CHECK = True

    # Mapping from message JSON attributes to class attributes
    MESSAGE_ATTRIBUTES = {
        "ActivationTime": "activation_time",
        "Duration": "duration",
        "Direction": "direction",
        "RealPowerMin": "real_power_min",
        "RealPowerRequest": "real_power_request",
        "CustomerIds": "customer_ids",
        "CongestionId": "congestion_id",
        "BidResolution": "bid_resolution"
    }
    OPTIONAL_ATTRIBUTES = ["BidResolution"]

    # Values accepted for direction
    ALLOWED_DIRECTION_VALUES = ["upregulation", "downregulation"]

    # attributes whose value should be a QuantityBlock and the expected unit of measure.
    QUANTITY_BLOCK_ATTRIBUTES = {
        "Duration": "Minute",
        "RealPowerMin": "kW",
        "RealPowerRequest": "kW",
        "BidResolution": "kW"
    }

    # attributes whose value should be a Array Block.
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES = {}

    # attributes whose value should be a Timeseries Block.
    TIMESERIES_BLOCK_ATTRIBUTES = []

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
    def activation_time(self) -> str:
        """The activation time in ISO 8601 format"""
        return self.__activation_time

    @activation_time.setter
    def activation_time(self, activation_time: Union[str, datetime.datetime]):
        if self._check_activation_time(activation_time):
            iso_format_string = to_iso_format_datetime_string(activation_time)
            if isinstance(iso_format_string, str):
                self.__activation_time = iso_format_string
                return

        raise MessageDateError("'{:s}' is an invalid datetime".format(str(activation_time)))

    @classmethod
    def _check_activation_time(cls, activation_time: Union[str, datetime.datetime]) -> bool:
        return cls._check_datetime(activation_time)

    @property
    def duration(self) -> QuantityBlock:
        """The duration of the request"""
        return self.__duration

    @duration.setter
    def duration(self, duration: Union[str, float, int, Dict[str, Any], QuantityBlock]):
        if self._check_duration(duration):
            self._set_quantity_block_value('Duration', duration)
            return

        raise MessageValueError("'{:s}' is an invalid value for duration.".format(str(duration)))

    @classmethod
    def _check_duration(cls, duration: Union[str, float, int, Dict, QuantityBlock]) -> bool:
        return cls._check_quantity_block(duration, cls.QUANTITY_BLOCK_ATTRIBUTES_FULL["Duration"],
                                         False, lambda value: value >= 0.0)

    @property
    def direction(self) -> str:
        """The direction of the request"""
        return self.__direction

    @direction.setter
    def direction(self, direction: str):
        if self._check_direction(direction):
            self.__direction = direction
            return

        raise MessageValueError("'{:s}' is an invalid value for direction".format(str(direction)))

    @classmethod
    def _check_direction(cls, direction: str) -> bool:
        if isinstance(direction, str) and direction in cls.ALLOWED_DIRECTION_VALUES:
            return True
        return False

    @property
    def real_power_min(self) -> QuantityBlock:
        """Minimum bid in kW"""
        return self.__real_power_min

    @real_power_min.setter
    def real_power_min(self, real_power_min: Union[str, float, int, Dict, QuantityBlock]):
        if self._check_real_power_min(real_power_min):
            self._set_quantity_block_value('RealPowerMin', real_power_min)
            return

        raise MessageValueError("'{:s}' is an invalid value for RealPowerMin.".format(str(real_power_min)))

    @classmethod
    def _check_real_power_min(cls, real_power_min: Union[str, float, int, Dict, QuantityBlock]) -> bool:
        return cls._check_quantity_block(real_power_min, cls.QUANTITY_BLOCK_ATTRIBUTES_FULL["RealPowerMin"],
                                         False, lambda value: value >= 0.0)

    @property
    def real_power_request(self) -> QuantityBlock:
        """Maximum bid in kW"""
        return self.__real_power_request

    @real_power_request.setter
    def real_power_request(self, real_power_request: Union[str, float, int, Dict, QuantityBlock]):
        if self._check_real_power_request(real_power_request):
            self._set_quantity_block_value('RealPowerRequest', real_power_request)
            return

        raise MessageValueError("'{:s}' is an invalid value for RealPowerRequest.".format(str(real_power_request)))

    @classmethod
    def _check_real_power_request(cls, real_power_request: Union[str, float, int, Dict, QuantityBlock]) -> bool:
        return cls._check_quantity_block(real_power_request, cls.QUANTITY_BLOCK_ATTRIBUTES_FULL["RealPowerRequest"],
                                         False, lambda value: value >= 0.0)

    @property
    def customer_ids(self) -> List[str]:
        """List of customer ids request is targeted at"""
        return self.__customer_ids

    @customer_ids.setter
    def customer_ids(self, customer_ids: Union[str, List[str], Tuple[str]]):
        if self._check_customer_ids(customer_ids):
            self.__customer_ids = list(customer_ids)
            return

        MessageValueError("'{:s}' is an invalid value for CustomerIds.".format(str(customer_ids)))

    @classmethod
    def _check_customer_ids(cls, customer_ids: Union[str, List[str], Tuple[str]]) -> bool:
        if (customer_ids is None or
                not isinstance(customer_ids, (str, list, tuple)) or
                len(customer_ids) == 0):
            return False
        if not isinstance(customer_ids, str):
            for customer_id in customer_ids:
                if not isinstance(customer_id, str):
                    return False
        return True

    @property
    def congestion_id(self) -> str:
        """Identifier for the congestion area / specific congestion problem"""
        return self.__congestion_id

    @congestion_id.setter
    def congestion_id(self, congestion_id: str):
        if self._check_congestion_id(congestion_id):
            self.__congestion_id = congestion_id
            return

        raise MessageValueError("Invalid value, {}, for attribute: congestion_id".format(congestion_id))

    @classmethod
    def _check_congestion_id(cls, congestion_id: str) -> bool:
        return isinstance(congestion_id, str)

    @property
    def bid_resolution(self) -> QuantityBlock:
        """Resolution for the bids"""
        return self.__bid_resolution

    @bid_resolution.setter
    def bid_resolution(self, bid_resolution: Union[str, float, int, Dict, QuantityBlock, None]):
        if self._check_bid_resolution(bid_resolution):
            if bid_resolution is None:
                self.__bid_resolution = None
                return
            self._set_quantity_block_value('BidResolution', bid_resolution)
            return

        raise MessageValueError("'{:s}' is an invalid value for BidResolution.".format(str(bid_resolution)))

    @classmethod
    def _check_bid_resolution(cls, bid_resolution: Union[str, float, int, Dict, QuantityBlock, None]) -> bool:
        return bid_resolution is None or \
               cls._check_quantity_block(bid_resolution, cls.QUANTITY_BLOCK_ATTRIBUTES_FULL["BidResolution"],
                                         True, lambda value: value >= 0.0)

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Union[RequestMessage, None]:
        if cls.validate_json(json_message):
            return RequestMessage(**json_message)
        return None


RequestMessage.register_to_factory()
