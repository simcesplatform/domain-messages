# -*- coding: utf-8 -*-

"""This module contains the message class for the simulation platform offer messages."""

from __future__ import annotations
from typing import Union, Dict, Any

from tools.exceptions.messages import MessageValueError
from tools.message.abstract import AbstractResultMessage
from tools.tools import FullLogger

import datetime
from tools.datetime_tools import to_iso_format_datetime_string
from tools.exceptions.messages import MessageDateError
from tools.message.block import QuantityBlock, TimeSeriesBlock

LOGGER = FullLogger(__name__)

# Example:
# TimeSeriesBlock for RealPower:
#
# time_tmp = datetime.datetime.now()
# time_index_list = [to_iso_format_datetime_string(time_tmp),
#                    to_iso_format_datetime_string(time_tmp + datetime.timedelta(hours=1))]
# time_series_block_tmp = TimeSeriesBlock(time_index_list,
#                                         {"customer1": ValueArrayBlock([2.0, 3.0],
#                                                                       "kW")})
#
# newMessage2 = OfferMessage(**{
#     "Type": "Offer",
#     "SimulationId": to_iso_format_datetime_string(datetime.datetime.now()),
#     "SourceProcessId": "source1",
#     "MessageId": "messageid1",
#     "EpochNumber": 1,
#     "TriggeringMessageIds": ["messageid1.1", "messageid1.2"],
#     "ActivationTime": to_iso_format_datetime_string(datetime.datetime.now()),
#     "Duration": 1.0,
#     "Direction": "upregulation",
#     "RealPower": time_series_block_tmp,
#     "Price": 2.0,
#     "CongestionId": "congestionId1",
#     "OfferId": "offerid1",
#     "OfferCount": 1
# })


class OfferMessage(AbstractResultMessage):
    """Class containing all the attributes for an Offer message."""

    # message type for these messages
    CLASS_MESSAGE_TYPE = "Offer"
    MESSAGE_TYPE_CHECK = True

    # Mapping from message JSON attributes to class attributes
    MESSAGE_ATTRIBUTES = {
        "ActivationTime": "activation_time",
        "Duration": "duration",
        "Direction": "direction",
        "RealPower": "real_power",
        "Price": "price",
        "CongestionId": "congestion_id",
        "OfferId": "offer_id",
        "OfferCount": "offer_count"
    }
    OPTIONAL_ATTRIBUTES = []

    # Values accepted for direction
    ALLOWED_DIRECTION_VALUES = ["upregulation", "downregulation"]
    # Units accepted for price
    ALLOWED_PRICE_UNITS = ["{EUR}/(kW.h)", "{EUR}/(MW.h)"]
    # ( Defaults to EUR/kW.h (Defaults to first value in this list) )
    # ( Anything else should be given as a QuantityBlock )
    # RealPower units:
    REAL_POWER_UNIT = "kW"

    # Attribute names
    ATTRIBUTE_REALPOWER = "RealPower"
    ATTRIBUTE_PRICE = "Price"
    ATTRIBUTE_DURATION = "Duration"

    # attributes whose value should be a QuantityBlock and the expected unit of measure.
    QUANTITY_BLOCK_ATTRIBUTES = {
        ATTRIBUTE_DURATION: "Minute",
        ATTRIBUTE_PRICE: "{EUR}/(kW.h)"
    }

    # attributes whose value should be a Array Block.
    QUANTITY_ARRAY_BLOCK_ATTRIBUTES = {}

    # attributes whose value should be a Timeseries Block.
    TIMESERIES_BLOCK_ATTRIBUTES = [ATTRIBUTE_REALPOWER]

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

        raise MessageDateError("'{:s}' is an invalid ActivationTime".format(str(activation_time)))

    @classmethod
    def _check_activation_time(cls, activation_time: Union[str, datetime.datetime]) -> bool:
        return cls._check_datetime(activation_time)

    @property
    def duration(self) -> QuantityBlock:
        """The duration of the request"""
        return self.__duration

    @duration.setter
    def duration(self, duration: Union[str, float, int, Dict[str, Any], QuantityBlock]):
        if type(duration) == int:
            duration = float(duration)
        if self._check_duration(duration):
            self._set_quantity_block_value(self.ATTRIBUTE_DURATION, duration)
            return

        raise MessageValueError("'{:s}' is an invalid value for {}.".format(str(duration),
                                                                            self.ATTRIBUTE_DURATION))

    @classmethod
    def _check_duration(cls, duration: Union[str, float, int, Dict[str, Any], QuantityBlock]) -> bool:
        return cls._check_quantity_block(value=duration,
                                         unit=cls.QUANTITY_BLOCK_ATTRIBUTES_FULL[cls.ATTRIBUTE_DURATION],
                                         can_be_none=False,
                                         float_value_check=lambda value: value >= 0.0)

    @property
    def direction(self) -> str:
        """The direction of the request"""
        return self.__direction

    @direction.setter
    def direction(self, direction: str):
        if self._check_direction(direction):
            self.__direction = direction
            return

        raise MessageValueError("'{:s}' is an invalid value for Direction".format(str(direction)))

    @classmethod
    def _check_direction(cls, direction: str) -> bool:
        if isinstance(direction, str) and direction in cls.ALLOWED_DIRECTION_VALUES:
            return True
        return False

    @property
    def real_power(self) -> TimeSeriesBlock:
        """Offered regulation as a TimeSeriesBlock"""
        return self.__real_power

    @real_power.setter
    def real_power(self, real_power: Union[TimeSeriesBlock, Dict[str, Any]]):
        if self._check_real_power(real_power):
            self._set_timeseries_block_value(self.ATTRIBUTE_REALPOWER, real_power)
            return

        raise MessageValueError("'{:s}' is an invalid value for {}".format(str(real_power),
                                                                           self.ATTRIBUTE_REALPOWER))

    @classmethod
    def _check_real_power(cls, real_power: Union[TimeSeriesBlock, Dict[str, Any]]) -> bool:
        return cls._check_timeseries_block(value=real_power,
                                           can_be_none=False,
                                           block_check=cls._check_real_power_block)

    @classmethod
    def _check_real_power_block(cls, real_power_block: TimeSeriesBlock) -> bool:
        block_series = real_power_block.series
        if len(block_series) < 1 or len(real_power_block.time_index) < 1:
            return False
        for value_array in block_series.values():
            if value_array.unit_of_measure != cls.REAL_POWER_UNIT:
                return False
        return True

    @property
    def price(self) -> QuantityBlock:
        """
        Price of the offered regulation.
        Units EUR/kWh (Or EUR/MWh)
        ( If EUR/MWh has to be given as QuantityBlock )
        """
        return self.__price

    @price.setter
    def price(self, price: Union[str, float, int, QuantityBlock]):
        """
        Sets the price for the offer. Sets the input price to a QuantityBlock.
        If the price is given as a QuantityBlock, uses its unit of measure.
        """
        if type(price) == int:
            price = float(price)
        if self._check_price(price):
            self._set_quantity_block_value(message_attribute=self.ATTRIBUTE_PRICE,
                                           quantity_value=price)
            if isinstance(price, QuantityBlock):
                self.price.unit_of_measure = price.unit_of_measure
            return

        raise MessageValueError("'{:s}' is an invalid value for {}".format(str(price),
                                                                           self.ATTRIBUTE_PRICE))

    @classmethod
    def _check_price(cls, price) -> bool:
        if isinstance(price, QuantityBlock):
            if price.unit_of_measure not in cls.ALLOWED_PRICE_UNITS:
                return False
            return cls._check_quantity_block(value=price.value,
                                             unit=price.unit_of_measure,
                                             can_be_none=False,
                                             float_value_check=lambda value: value >= 0.0)
        return cls._check_quantity_block(value=price,
                                         unit=cls.ALLOWED_PRICE_UNITS[0],
                                         can_be_none=False,
                                         float_value_check=lambda value: value >= 0.0)

    @property
    def congestion_id(self) -> str:
        """Identifier for the congestion area / specific congestion problem"""
        return self.__congestion_id

    @congestion_id.setter
    def congestion_id(self, congestion_id: str):
        if self._check_congestion_id(congestion_id):
            self.__congestion_id = congestion_id
            return

        raise MessageValueError("'{:s}' is an invalid value for CongestionId".format(str(congestion_id)))

    @classmethod
    def _check_congestion_id(cls, congestion_id: str) -> bool:
        return isinstance(congestion_id, str) and len(congestion_id) > 0

    @property
    def offer_id(self) -> str:
        """Identifier for this specific offer"""
        return self.__offer_id

    @offer_id.setter
    def offer_id(self, offer_id: str):
        if self._check_offer_id(offer_id):
            self.__offer_id = offer_id
            return

        raise MessageValueError("'{:s}' is an invalid value for OfferId".format(str(offer_id)))

    @classmethod
    def _check_offer_id(cls, offer_id: str) -> bool:
        return isinstance(offer_id, str) and len(offer_id) > 0

    @property
    def offer_count(self) -> int:
        """
        Total number of offers the provider is going to send to the running epoch related to this
        congestion id.
        """
        return self.__offer_count

    @offer_count.setter
    def offer_count(self, offer_count: Union[str, float, int]):
        if self._check_offer_count(offer_count):
            self.__offer_count = int(offer_count)
            return

        raise MessageValueError("'{:s}' is an invalid value for OfferCount".format(offer_count))

    @classmethod
    def _check_offer_count(cls, offer_count: Union[str, float, int]) -> bool:
        if offer_count is None or \
                not (isinstance(offer_count, str) or
                     isinstance(offer_count, float) or
                     isinstance(offer_count, int)):
            return False
        if float(offer_count).is_integer() and int(offer_count) >= 0:
            return True
        return False

    @classmethod
    def from_json(cls, json_message: Dict[str, Any]) -> Union[OfferMessage, None]:
        if cls.validate_json(json_message):
            return OfferMessage(**json_message)
        return None


OfferMessage.register_to_factory()
