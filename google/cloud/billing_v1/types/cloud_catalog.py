# -*- coding: utf-8 -*-

# Copyright (C) 2019  Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import proto  # type: ignore


from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.type import money_pb2 as money  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.billing.v1",
    manifest={
        "Service",
        "Sku",
        "Category",
        "PricingInfo",
        "PricingExpression",
        "AggregationInfo",
        "ListServicesRequest",
        "ListServicesResponse",
        "ListSkusRequest",
        "ListSkusResponse",
    },
)


class Service(proto.Message):
    r"""Encapsulates a single service in Google Cloud Platform.

    Attributes:
        name (str):
            The resource name for the service.
            Example: "services/DA34-426B-A397".
        service_id (str):
            The identifier for the service.
            Example: "DA34-426B-A397".
        display_name (str):
            A human readable display name for this
            service.
        business_entity_name (str):
            The business under which the service is
            offered. Ex. "businessEntities/GCP",
            "businessEntities/Maps".
    """

    name = proto.Field(proto.STRING, number=1)
    service_id = proto.Field(proto.STRING, number=2)
    display_name = proto.Field(proto.STRING, number=3)
    business_entity_name = proto.Field(proto.STRING, number=4)


class Sku(proto.Message):
    r"""Encapsulates a single SKU in Google Cloud Platform

    Attributes:
        name (str):
            The resource name for the SKU.
            Example:
            "services/DA34-426B-A397/skus/AA95-CD31-42FE".
        sku_id (str):
            The identifier for the SKU.
            Example: "AA95-CD31-42FE".
        description (str):
            A human readable description of the SKU, has
            a maximum length of 256 characters.
        category (~.cloud_catalog.Category):
            The category hierarchy of this SKU, purely
            for organizational purpose.
        service_regions (Sequence[str]):
            List of service regions this SKU is offered
            at. Example: "asia-east1"
            Service regions can be found at
            https://cloud.google.com/about/locations/
        pricing_info (Sequence[~.cloud_catalog.PricingInfo]):
            A timeline of pricing info for this SKU in
            chronological order.
        service_provider_name (str):
            Identifies the service provider.
            This is 'Google' for first party services in
            Google Cloud Platform.
    """

    name = proto.Field(proto.STRING, number=1)
    sku_id = proto.Field(proto.STRING, number=2)
    description = proto.Field(proto.STRING, number=3)
    category = proto.Field(proto.MESSAGE, number=4, message="Category")
    service_regions = proto.RepeatedField(proto.STRING, number=5)
    pricing_info = proto.RepeatedField(proto.MESSAGE, number=6, message="PricingInfo")
    service_provider_name = proto.Field(proto.STRING, number=7)


class Category(proto.Message):
    r"""Represents the category hierarchy of a SKU.

    Attributes:
        service_display_name (str):
            The display name of the service this SKU
            belongs to.
        resource_family (str):
            The type of product the SKU refers to.
            Example: "Compute", "Storage", "Network",
            "ApplicationServices" etc.
        resource_group (str):
            A group classification for related SKUs.
            Example: "RAM", "GPU", "Prediction", "Ops",
            "GoogleEgress" etc.
        usage_type (str):
            Represents how the SKU is consumed.
            Example: "OnDemand", "Preemptible", "Commit1Mo",
            "Commit1Yr" etc.
    """

    service_display_name = proto.Field(proto.STRING, number=1)
    resource_family = proto.Field(proto.STRING, number=2)
    resource_group = proto.Field(proto.STRING, number=3)
    usage_type = proto.Field(proto.STRING, number=4)


class PricingInfo(proto.Message):
    r"""Represents the pricing information for a SKU at a single
    point of time.

    Attributes:
        effective_time (~.timestamp.Timestamp):
            The timestamp from which this pricing was effective within
            the requested time range. This is guaranteed to be greater
            than or equal to the start_time field in the request and
            less than the end_time field in the request. If a time range
            was not specified in the request this field will be
            equivalent to a time within the last 12 hours, indicating
            the latest pricing info.
        summary (str):
            An optional human readable summary of the
            pricing information, has a maximum length of 256
            characters.
        pricing_expression (~.cloud_catalog.PricingExpression):
            Expresses the pricing formula. See ``PricingExpression`` for
            an example.
        aggregation_info (~.cloud_catalog.AggregationInfo):
            Aggregation Info. This can be left
            unspecified if the pricing expression doesn't
            require aggregation.
        currency_conversion_rate (float):
            Conversion rate used for currency conversion, from USD to
            the currency specified in the request. This includes any
            surcharge collected for billing in non USD currency. If a
            currency is not specified in the request this defaults to
            1.0. Example: USD \* currency_conversion_rate = JPY
    """

    effective_time = proto.Field(proto.MESSAGE, number=1, message=timestamp.Timestamp)
    summary = proto.Field(proto.STRING, number=2)
    pricing_expression = proto.Field(
        proto.MESSAGE, number=3, message="PricingExpression"
    )
    aggregation_info = proto.Field(proto.MESSAGE, number=4, message="AggregationInfo")
    currency_conversion_rate = proto.Field(proto.DOUBLE, number=5)


class PricingExpression(proto.Message):
    r"""Expresses a mathematical pricing formula. For Example:-

    ``usage_unit: GBy`` ``tiered_rates:``
    ``[start_usage_amount: 20, unit_price: $10]``
    ``[start_usage_amount: 100, unit_price: $5]``

    The above expresses a pricing formula where the first 20GB is free,
    the next 80GB is priced at $10 per GB followed by $5 per GB for
    additional usage.

    Attributes:
        usage_unit (str):
            The short hand for unit of usage this pricing is specified
            in. Example: usage_unit of "GiBy" means that usage is
            specified in "Gibi Byte".
        usage_unit_description (str):
            The unit of usage in human readable form.
            Example: "gibi byte".
        base_unit (str):
            The base unit for the SKU which is the unit
            used in usage exports. Example: "By".
        base_unit_description (str):
            The base unit in human readable form.
            Example: "byte".
        base_unit_conversion_factor (float):
            Conversion factor for converting from price per usage_unit
            to price per base_unit, and start_usage_amount to
            start_usage_amount in base_unit. unit_price /
            base_unit_conversion_factor = price per base_unit.
            start_usage_amount \* base_unit_conversion_factor =
            start_usage_amount in base_unit.
        display_quantity (float):
            The recommended quantity of units for displaying pricing
            info. When displaying pricing info it is recommended to
            display: (unit_price \* display_quantity) per
            display_quantity usage_unit. This field does not affect the
            pricing formula and is for display purposes only. Example:
            If the unit_price is "0.0001 USD", the usage_unit is "GB"
            and the display_quantity is "1000" then the recommended way
            of displaying the pricing info is "0.10 USD per 1000 GB".
        tiered_rates (Sequence[~.cloud_catalog.PricingExpression.TierRate]):
            The list of tiered rates for this pricing. The total cost is
            computed by applying each of the tiered rates on usage. This
            repeated list is sorted by ascending order of
            start_usage_amount.
    """

    class TierRate(proto.Message):
        r"""The price rate indicating starting usage and its
        corresponding price.

        Attributes:
            start_usage_amount (float):
                Usage is priced at this rate only after this amount.
                Example: start_usage_amount of 10 indicates that the usage
                will be priced at the unit_price after the first 10
                usage_units.
            unit_price (~.money.Money):
                The price per unit of usage. Example: unit_price of amount
                $10 indicates that each unit will cost $10.
        """

        start_usage_amount = proto.Field(proto.DOUBLE, number=1)
        unit_price = proto.Field(proto.MESSAGE, number=2, message=money.Money)

    usage_unit = proto.Field(proto.STRING, number=1)
    usage_unit_description = proto.Field(proto.STRING, number=4)
    base_unit = proto.Field(proto.STRING, number=5)
    base_unit_description = proto.Field(proto.STRING, number=6)
    base_unit_conversion_factor = proto.Field(proto.DOUBLE, number=7)
    display_quantity = proto.Field(proto.DOUBLE, number=2)
    tiered_rates = proto.RepeatedField(proto.MESSAGE, number=3, message=TierRate)


class AggregationInfo(proto.Message):
    r"""Represents the aggregation level and interval for pricing of
    a single SKU.

    Attributes:
        aggregation_level (~.cloud_catalog.AggregationInfo.AggregationLevel):

        aggregation_interval (~.cloud_catalog.AggregationInfo.AggregationInterval):

        aggregation_count (int):
            The number of intervals to aggregate over. Example: If
            aggregation_level is "DAILY" and aggregation_count is 14,
            aggregation will be over 14 days.
    """

    class AggregationLevel(proto.Enum):
        r"""The level at which usage is aggregated to compute cost.
        Example: "ACCOUNT" aggregation level indicates that usage for
        tiered pricing is aggregated across all projects in a single
        account.
        """
        AGGREGATION_LEVEL_UNSPECIFIED = 0
        ACCOUNT = 1
        PROJECT = 2

    class AggregationInterval(proto.Enum):
        r"""The interval at which usage is aggregated to compute cost.
        Example: "MONTHLY" aggregation interval indicates that usage for
        tiered pricing is aggregated every month.
        """
        AGGREGATION_INTERVAL_UNSPECIFIED = 0
        DAILY = 1
        MONTHLY = 2

    aggregation_level = proto.Field(proto.ENUM, number=1, enum=AggregationLevel)
    aggregation_interval = proto.Field(proto.ENUM, number=2, enum=AggregationInterval)
    aggregation_count = proto.Field(proto.INT32, number=3)


class ListServicesRequest(proto.Message):
    r"""Request message for ``ListServices``.

    Attributes:
        page_size (int):
            Requested page size. Defaults to 5000.
        page_token (str):
            A token identifying a page of results to return. This should
            be a ``next_page_token`` value returned from a previous
            ``ListServices`` call. If unspecified, the first page of
            results is returned.
    """

    page_size = proto.Field(proto.INT32, number=1)
    page_token = proto.Field(proto.STRING, number=2)


class ListServicesResponse(proto.Message):
    r"""Response message for ``ListServices``.

    Attributes:
        services (Sequence[~.cloud_catalog.Service]):
            A list of services.
        next_page_token (str):
            A token to retrieve the next page of results. To retrieve
            the next page, call ``ListServices`` again with the
            ``page_token`` field set to this value. This field is empty
            if there are no more results to retrieve.
    """

    @property
    def raw_page(self):
        return self

    services = proto.RepeatedField(proto.MESSAGE, number=1, message=Service)
    next_page_token = proto.Field(proto.STRING, number=2)


class ListSkusRequest(proto.Message):
    r"""Request message for ``ListSkus``.

    Attributes:
        parent (str):
            Required. The name of the service.
            Example: "services/DA34-426B-A397".
        start_time (~.timestamp.Timestamp):
            Optional inclusive start time of the time range for which
            the pricing versions will be returned. Timestamps in the
            future are not allowed. The time range has to be within a
            single calendar month in America/Los_Angeles timezone. Time
            range as a whole is optional. If not specified, the latest
            pricing will be returned (up to 12 hours old at most).
        end_time (~.timestamp.Timestamp):
            Optional exclusive end time of the time range for which the
            pricing versions will be returned. Timestamps in the future
            are not allowed. The time range has to be within a single
            calendar month in America/Los_Angeles timezone. Time range
            as a whole is optional. If not specified, the latest pricing
            will be returned (up to 12 hours old at most).
        currency_code (str):
            The ISO 4217 currency code for the pricing info in the
            response proto. Will use the conversion rate as of
            start_time. Optional. If not specified USD will be used.
        page_size (int):
            Requested page size. Defaults to 5000.
        page_token (str):
            A token identifying a page of results to return. This should
            be a ``next_page_token`` value returned from a previous
            ``ListSkus`` call. If unspecified, the first page of results
            is returned.
    """

    parent = proto.Field(proto.STRING, number=1)
    start_time = proto.Field(proto.MESSAGE, number=2, message=timestamp.Timestamp)
    end_time = proto.Field(proto.MESSAGE, number=3, message=timestamp.Timestamp)
    currency_code = proto.Field(proto.STRING, number=4)
    page_size = proto.Field(proto.INT32, number=5)
    page_token = proto.Field(proto.STRING, number=6)


class ListSkusResponse(proto.Message):
    r"""Response message for ``ListSkus``.

    Attributes:
        skus (Sequence[~.cloud_catalog.Sku]):
            The list of public SKUs of the given service.
        next_page_token (str):
            A token to retrieve the next page of results. To retrieve
            the next page, call ``ListSkus`` again with the
            ``page_token`` field set to this value. This field is empty
            if there are no more results to retrieve.
    """

    @property
    def raw_page(self):
        return self

    skus = proto.RepeatedField(proto.MESSAGE, number=1, message=Sku)
    next_page_token = proto.Field(proto.STRING, number=2)


__all__ = tuple(sorted(__protobuf__.manifest))