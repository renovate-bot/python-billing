# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import os
import mock

import grpc
from grpc.experimental import aio
import math
import pytest
from proto.marshal.rules.dates import DurationRule, TimestampRule

from google import auth
from google.api_core import client_options
from google.api_core import exceptions
from google.api_core import gapic_v1
from google.api_core import grpc_helpers
from google.api_core import grpc_helpers_async
from google.auth import credentials
from google.auth.exceptions import MutualTLSChannelError
from google.cloud.billing_v1.services.cloud_billing import CloudBillingAsyncClient
from google.cloud.billing_v1.services.cloud_billing import CloudBillingClient
from google.cloud.billing_v1.services.cloud_billing import pagers
from google.cloud.billing_v1.services.cloud_billing import transports
from google.cloud.billing_v1.types import cloud_billing
from google.iam.v1 import iam_policy_pb2 as iam_policy  # type: ignore
from google.iam.v1 import options_pb2 as options  # type: ignore
from google.iam.v1 import policy_pb2 as policy  # type: ignore
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.type import expr_pb2 as expr  # type: ignore


def client_cert_source_callback():
    return b"cert bytes", b"key bytes"


# If default endpoint is localhost, then default mtls endpoint will be the same.
# This method modifies the default endpoint so the client can produce a different
# mtls endpoint for endpoint testing purposes.
def modify_default_endpoint(client):
    return (
        "foo.googleapis.com"
        if ("localhost" in client.DEFAULT_ENDPOINT)
        else client.DEFAULT_ENDPOINT
    )


def test__get_default_mtls_endpoint():
    api_endpoint = "example.googleapis.com"
    api_mtls_endpoint = "example.mtls.googleapis.com"
    sandbox_endpoint = "example.sandbox.googleapis.com"
    sandbox_mtls_endpoint = "example.mtls.sandbox.googleapis.com"
    non_googleapi = "api.example.com"

    assert CloudBillingClient._get_default_mtls_endpoint(None) is None
    assert (
        CloudBillingClient._get_default_mtls_endpoint(api_endpoint) == api_mtls_endpoint
    )
    assert (
        CloudBillingClient._get_default_mtls_endpoint(api_mtls_endpoint)
        == api_mtls_endpoint
    )
    assert (
        CloudBillingClient._get_default_mtls_endpoint(sandbox_endpoint)
        == sandbox_mtls_endpoint
    )
    assert (
        CloudBillingClient._get_default_mtls_endpoint(sandbox_mtls_endpoint)
        == sandbox_mtls_endpoint
    )
    assert CloudBillingClient._get_default_mtls_endpoint(non_googleapi) == non_googleapi


@pytest.mark.parametrize("client_class", [CloudBillingClient, CloudBillingAsyncClient])
def test_cloud_billing_client_from_service_account_file(client_class):
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = client_class.from_service_account_file("dummy/file/path.json")
        assert client.transport._credentials == creds

        client = client_class.from_service_account_json("dummy/file/path.json")
        assert client.transport._credentials == creds

        assert client.transport._host == "cloudbilling.googleapis.com:443"


def test_cloud_billing_client_get_transport_class():
    transport = CloudBillingClient.get_transport_class()
    assert transport == transports.CloudBillingGrpcTransport

    transport = CloudBillingClient.get_transport_class("grpc")
    assert transport == transports.CloudBillingGrpcTransport


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (CloudBillingClient, transports.CloudBillingGrpcTransport, "grpc"),
        (
            CloudBillingAsyncClient,
            transports.CloudBillingGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
@mock.patch.object(
    CloudBillingClient, "DEFAULT_ENDPOINT", modify_default_endpoint(CloudBillingClient)
)
@mock.patch.object(
    CloudBillingAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(CloudBillingAsyncClient),
)
def test_cloud_billing_client_client_options(
    client_class, transport_class, transport_name
):
    # Check that if channel is provided we won't create a new one.
    with mock.patch.object(CloudBillingClient, "get_transport_class") as gtc:
        transport = transport_class(credentials=credentials.AnonymousCredentials())
        client = client_class(transport=transport)
        gtc.assert_not_called()

    # Check that if channel is provided via str we will create a new one.
    with mock.patch.object(CloudBillingClient, "get_transport_class") as gtc:
        client = client_class(transport=transport_name)
        gtc.assert_called()

    # Check the case api_endpoint is provided.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "never".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT is
    # "always".
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}):
        with mock.patch.object(transport_class, "__init__") as patched:
            patched.return_value = None
            client = client_class()
            patched.assert_called_once_with(
                credentials=None,
                credentials_file=None,
                host=client.DEFAULT_MTLS_ENDPOINT,
                scopes=None,
                ssl_channel_credentials=None,
                quota_project_id=None,
                client_info=transports.base.DEFAULT_CLIENT_INFO,
            )

    # Check the case api_endpoint is not provided and GOOGLE_API_USE_MTLS_ENDPOINT has
    # unsupported value.
    with mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "Unsupported"}):
        with pytest.raises(MutualTLSChannelError):
            client = client_class()

    # Check the case GOOGLE_API_USE_CLIENT_CERTIFICATE has unsupported value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": "Unsupported"}
    ):
        with pytest.raises(ValueError):
            client = client_class()

    # Check the case quota_project_id is provided
    options = client_options.ClientOptions(quota_project_id="octopus")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id="octopus",
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name,use_client_cert_env",
    [
        (CloudBillingClient, transports.CloudBillingGrpcTransport, "grpc", "true"),
        (
            CloudBillingAsyncClient,
            transports.CloudBillingGrpcAsyncIOTransport,
            "grpc_asyncio",
            "true",
        ),
        (CloudBillingClient, transports.CloudBillingGrpcTransport, "grpc", "false"),
        (
            CloudBillingAsyncClient,
            transports.CloudBillingGrpcAsyncIOTransport,
            "grpc_asyncio",
            "false",
        ),
    ],
)
@mock.patch.object(
    CloudBillingClient, "DEFAULT_ENDPOINT", modify_default_endpoint(CloudBillingClient)
)
@mock.patch.object(
    CloudBillingAsyncClient,
    "DEFAULT_ENDPOINT",
    modify_default_endpoint(CloudBillingAsyncClient),
)
@mock.patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "auto"})
def test_cloud_billing_client_mtls_env_auto(
    client_class, transport_class, transport_name, use_client_cert_env
):
    # This tests the endpoint autoswitch behavior. Endpoint is autoswitched to the default
    # mtls endpoint, if GOOGLE_API_USE_CLIENT_CERTIFICATE is "true" and client cert exists.

    # Check the case client_cert_source is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        options = client_options.ClientOptions(
            client_cert_source=client_cert_source_callback
        )
        with mock.patch.object(transport_class, "__init__") as patched:
            ssl_channel_creds = mock.Mock()
            with mock.patch(
                "grpc.ssl_channel_credentials", return_value=ssl_channel_creds
            ):
                patched.return_value = None
                client = client_class(client_options=options)

                if use_client_cert_env == "false":
                    expected_ssl_channel_creds = None
                    expected_host = client.DEFAULT_ENDPOINT
                else:
                    expected_ssl_channel_creds = ssl_channel_creds
                    expected_host = client.DEFAULT_MTLS_ENDPOINT

                patched.assert_called_once_with(
                    credentials=None,
                    credentials_file=None,
                    host=expected_host,
                    scopes=None,
                    ssl_channel_credentials=expected_ssl_channel_creds,
                    quota_project_id=None,
                    client_info=transports.base.DEFAULT_CLIENT_INFO,
                )

    # Check the case ADC client cert is provided. Whether client cert is used depends on
    # GOOGLE_API_USE_CLIENT_CERTIFICATE value.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    with mock.patch(
                        "google.auth.transport.grpc.SslCredentials.ssl_credentials",
                        new_callable=mock.PropertyMock,
                    ) as ssl_credentials_mock:
                        if use_client_cert_env == "false":
                            is_mtls_mock.return_value = False
                            ssl_credentials_mock.return_value = None
                            expected_host = client.DEFAULT_ENDPOINT
                            expected_ssl_channel_creds = None
                        else:
                            is_mtls_mock.return_value = True
                            ssl_credentials_mock.return_value = mock.Mock()
                            expected_host = client.DEFAULT_MTLS_ENDPOINT
                            expected_ssl_channel_creds = (
                                ssl_credentials_mock.return_value
                            )

                        patched.return_value = None
                        client = client_class()
                        patched.assert_called_once_with(
                            credentials=None,
                            credentials_file=None,
                            host=expected_host,
                            scopes=None,
                            ssl_channel_credentials=expected_ssl_channel_creds,
                            quota_project_id=None,
                            client_info=transports.base.DEFAULT_CLIENT_INFO,
                        )

    # Check the case client_cert_source and ADC client cert are not provided.
    with mock.patch.dict(
        os.environ, {"GOOGLE_API_USE_CLIENT_CERTIFICATE": use_client_cert_env}
    ):
        with mock.patch.object(transport_class, "__init__") as patched:
            with mock.patch(
                "google.auth.transport.grpc.SslCredentials.__init__", return_value=None
            ):
                with mock.patch(
                    "google.auth.transport.grpc.SslCredentials.is_mtls",
                    new_callable=mock.PropertyMock,
                ) as is_mtls_mock:
                    is_mtls_mock.return_value = False
                    patched.return_value = None
                    client = client_class()
                    patched.assert_called_once_with(
                        credentials=None,
                        credentials_file=None,
                        host=client.DEFAULT_ENDPOINT,
                        scopes=None,
                        ssl_channel_credentials=None,
                        quota_project_id=None,
                        client_info=transports.base.DEFAULT_CLIENT_INFO,
                    )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (CloudBillingClient, transports.CloudBillingGrpcTransport, "grpc"),
        (
            CloudBillingAsyncClient,
            transports.CloudBillingGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_cloud_billing_client_client_options_scopes(
    client_class, transport_class, transport_name
):
    # Check the case scopes are provided.
    options = client_options.ClientOptions(scopes=["1", "2"],)
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host=client.DEFAULT_ENDPOINT,
            scopes=["1", "2"],
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


@pytest.mark.parametrize(
    "client_class,transport_class,transport_name",
    [
        (CloudBillingClient, transports.CloudBillingGrpcTransport, "grpc"),
        (
            CloudBillingAsyncClient,
            transports.CloudBillingGrpcAsyncIOTransport,
            "grpc_asyncio",
        ),
    ],
)
def test_cloud_billing_client_client_options_credentials_file(
    client_class, transport_class, transport_name
):
    # Check the case credentials file is provided.
    options = client_options.ClientOptions(credentials_file="credentials.json")
    with mock.patch.object(transport_class, "__init__") as patched:
        patched.return_value = None
        client = client_class(client_options=options)
        patched.assert_called_once_with(
            credentials=None,
            credentials_file="credentials.json",
            host=client.DEFAULT_ENDPOINT,
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_cloud_billing_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.billing_v1.services.cloud_billing.transports.CloudBillingGrpcTransport.__init__"
    ) as grpc_transport:
        grpc_transport.return_value = None
        client = CloudBillingClient(client_options={"api_endpoint": "squid.clam.whelk"})
        grpc_transport.assert_called_once_with(
            credentials=None,
            credentials_file=None,
            host="squid.clam.whelk",
            scopes=None,
            ssl_channel_credentials=None,
            quota_project_id=None,
            client_info=transports.base.DEFAULT_CLIENT_INFO,
        )


def test_get_billing_account(
    transport: str = "grpc", request_type=cloud_billing.GetBillingAccountRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount(
            name="name_value",
            open_=True,
            display_name="display_name_value",
            master_billing_account="master_billing_account_value",
        )

        response = client.get_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.GetBillingAccountRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


def test_get_billing_account_from_dict():
    test_get_billing_account(request_type=dict)


@pytest.mark.asyncio
async def test_get_billing_account_async(
    transport: str = "grpc_asyncio", request_type=cloud_billing.GetBillingAccountRequest
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount(
                name="name_value",
                open_=True,
                display_name="display_name_value",
                master_billing_account="master_billing_account_value",
            )
        )

        response = await client.get_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.GetBillingAccountRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


@pytest.mark.asyncio
async def test_get_billing_account_async_from_dict():
    await test_get_billing_account_async(request_type=dict)


def test_get_billing_account_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.GetBillingAccountRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        call.return_value = cloud_billing.BillingAccount()

        client.get_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_billing_account_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.GetBillingAccountRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount()
        )

        await client.get_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_billing_account_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_billing_account(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_billing_account_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_billing_account(
            cloud_billing.GetBillingAccountRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_billing_account_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_billing_account(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_billing_account_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_billing_account(
            cloud_billing.GetBillingAccountRequest(), name="name_value",
        )


def test_list_billing_accounts(
    transport: str = "grpc", request_type=cloud_billing.ListBillingAccountsRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ListBillingAccountsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_billing_accounts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.ListBillingAccountsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListBillingAccountsPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_billing_accounts_from_dict():
    test_list_billing_accounts(request_type=dict)


@pytest.mark.asyncio
async def test_list_billing_accounts_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.ListBillingAccountsRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ListBillingAccountsResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_billing_accounts(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.ListBillingAccountsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListBillingAccountsAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_billing_accounts_async_from_dict():
    await test_list_billing_accounts_async(request_type=dict)


def test_list_billing_accounts_pager():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[], next_page_token="def",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[cloud_billing.BillingAccount(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        pager = client.list_billing_accounts(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, cloud_billing.BillingAccount) for i in results)


def test_list_billing_accounts_pages():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[], next_page_token="def",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[cloud_billing.BillingAccount(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_billing_accounts(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_billing_accounts_async_pager():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[], next_page_token="def",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[cloud_billing.BillingAccount(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_billing_accounts(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, cloud_billing.BillingAccount) for i in responses)


@pytest.mark.asyncio
async def test_list_billing_accounts_async_pages():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_billing_accounts),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[], next_page_token="def",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[cloud_billing.BillingAccount(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListBillingAccountsResponse(
                billing_accounts=[
                    cloud_billing.BillingAccount(),
                    cloud_billing.BillingAccount(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_billing_accounts(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_update_billing_account(
    transport: str = "grpc", request_type=cloud_billing.UpdateBillingAccountRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount(
            name="name_value",
            open_=True,
            display_name="display_name_value",
            master_billing_account="master_billing_account_value",
        )

        response = client.update_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.UpdateBillingAccountRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


def test_update_billing_account_from_dict():
    test_update_billing_account(request_type=dict)


@pytest.mark.asyncio
async def test_update_billing_account_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.UpdateBillingAccountRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount(
                name="name_value",
                open_=True,
                display_name="display_name_value",
                master_billing_account="master_billing_account_value",
            )
        )

        response = await client.update_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.UpdateBillingAccountRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


@pytest.mark.asyncio
async def test_update_billing_account_async_from_dict():
    await test_update_billing_account_async(request_type=dict)


def test_update_billing_account_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.UpdateBillingAccountRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        call.return_value = cloud_billing.BillingAccount()

        client.update_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_billing_account_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.UpdateBillingAccountRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount()
        )

        await client.update_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_update_billing_account_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_billing_account(
            name="name_value", account=cloud_billing.BillingAccount(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].account == cloud_billing.BillingAccount(name="name_value")


def test_update_billing_account_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_billing_account(
            cloud_billing.UpdateBillingAccountRequest(),
            name="name_value",
            account=cloud_billing.BillingAccount(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_billing_account_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_billing_account(
            name="name_value", account=cloud_billing.BillingAccount(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].account == cloud_billing.BillingAccount(name="name_value")


@pytest.mark.asyncio
async def test_update_billing_account_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_billing_account(
            cloud_billing.UpdateBillingAccountRequest(),
            name="name_value",
            account=cloud_billing.BillingAccount(name="name_value"),
        )


def test_create_billing_account(
    transport: str = "grpc", request_type=cloud_billing.CreateBillingAccountRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount(
            name="name_value",
            open_=True,
            display_name="display_name_value",
            master_billing_account="master_billing_account_value",
        )

        response = client.create_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.CreateBillingAccountRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


def test_create_billing_account_from_dict():
    test_create_billing_account(request_type=dict)


@pytest.mark.asyncio
async def test_create_billing_account_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.CreateBillingAccountRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount(
                name="name_value",
                open_=True,
                display_name="display_name_value",
                master_billing_account="master_billing_account_value",
            )
        )

        response = await client.create_billing_account(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.CreateBillingAccountRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, cloud_billing.BillingAccount)

    assert response.name == "name_value"

    assert response.open_ is True

    assert response.display_name == "display_name_value"

    assert response.master_billing_account == "master_billing_account_value"


@pytest.mark.asyncio
async def test_create_billing_account_async_from_dict():
    await test_create_billing_account_async(request_type=dict)


def test_create_billing_account_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.create_billing_account(
            billing_account=cloud_billing.BillingAccount(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].billing_account == cloud_billing.BillingAccount(
            name="name_value"
        )


def test_create_billing_account_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_billing_account(
            cloud_billing.CreateBillingAccountRequest(),
            billing_account=cloud_billing.BillingAccount(name="name_value"),
        )


@pytest.mark.asyncio
async def test_create_billing_account_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.create_billing_account), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.BillingAccount()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.BillingAccount()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.create_billing_account(
            billing_account=cloud_billing.BillingAccount(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].billing_account == cloud_billing.BillingAccount(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_create_billing_account_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.create_billing_account(
            cloud_billing.CreateBillingAccountRequest(),
            billing_account=cloud_billing.BillingAccount(name="name_value"),
        )


def test_list_project_billing_info(
    transport: str = "grpc", request_type=cloud_billing.ListProjectBillingInfoRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ListProjectBillingInfoResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.ListProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, pagers.ListProjectBillingInfoPager)

    assert response.next_page_token == "next_page_token_value"


def test_list_project_billing_info_from_dict():
    test_list_project_billing_info(request_type=dict)


@pytest.mark.asyncio
async def test_list_project_billing_info_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.ListProjectBillingInfoRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ListProjectBillingInfoResponse(
                next_page_token="next_page_token_value",
            )
        )

        response = await client.list_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.ListProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListProjectBillingInfoAsyncPager)

    assert response.next_page_token == "next_page_token_value"


@pytest.mark.asyncio
async def test_list_project_billing_info_async_from_dict():
    await test_list_project_billing_info_async(request_type=dict)


def test_list_project_billing_info_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.ListProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        call.return_value = cloud_billing.ListProjectBillingInfoResponse()

        client.list_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_list_project_billing_info_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.ListProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ListProjectBillingInfoResponse()
        )

        await client.list_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_list_project_billing_info_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ListProjectBillingInfoResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.list_project_billing_info(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_list_project_billing_info_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_project_billing_info(
            cloud_billing.ListProjectBillingInfoRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_list_project_billing_info_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ListProjectBillingInfoResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ListProjectBillingInfoResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.list_project_billing_info(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_list_project_billing_info_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.list_project_billing_info(
            cloud_billing.ListProjectBillingInfoRequest(), name="name_value",
        )


def test_list_project_billing_info_pager():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[], next_page_token="def",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[cloud_billing.ProjectBillingInfo(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
            ),
            RuntimeError,
        )

        metadata = ()
        metadata = tuple(metadata) + (
            gapic_v1.routing_header.to_grpc_metadata((("name", ""),)),
        )
        pager = client.list_project_billing_info(request={})

        assert pager._metadata == metadata

        results = [i for i in pager]
        assert len(results) == 6
        assert all(isinstance(i, cloud_billing.ProjectBillingInfo) for i in results)


def test_list_project_billing_info_pages():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[], next_page_token="def",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[cloud_billing.ProjectBillingInfo(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_project_billing_info(request={}).pages)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


@pytest.mark.asyncio
async def test_list_project_billing_info_async_pager():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[], next_page_token="def",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[cloud_billing.ProjectBillingInfo(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
            ),
            RuntimeError,
        )
        async_pager = await client.list_project_billing_info(request={},)
        assert async_pager.next_page_token == "abc"
        responses = []
        async for response in async_pager:
            responses.append(response)

        assert len(responses) == 6
        assert all(isinstance(i, cloud_billing.ProjectBillingInfo) for i in responses)


@pytest.mark.asyncio
async def test_list_project_billing_info_async_pages():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.list_project_billing_info),
        "__call__",
        new_callable=mock.AsyncMock,
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
                next_page_token="abc",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[], next_page_token="def",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[cloud_billing.ProjectBillingInfo(),],
                next_page_token="ghi",
            ),
            cloud_billing.ListProjectBillingInfoResponse(
                project_billing_info=[
                    cloud_billing.ProjectBillingInfo(),
                    cloud_billing.ProjectBillingInfo(),
                ],
            ),
            RuntimeError,
        )
        pages = []
        async for page_ in (await client.list_project_billing_info(request={})).pages:
            pages.append(page_)
        for page_, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page_.raw_page.next_page_token == token


def test_get_project_billing_info(
    transport: str = "grpc", request_type=cloud_billing.GetProjectBillingInfoRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo(
            name="name_value",
            project_id="project_id_value",
            billing_account_name="billing_account_name_value",
            billing_enabled=True,
        )

        response = client.get_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.GetProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, cloud_billing.ProjectBillingInfo)

    assert response.name == "name_value"

    assert response.project_id == "project_id_value"

    assert response.billing_account_name == "billing_account_name_value"

    assert response.billing_enabled is True


def test_get_project_billing_info_from_dict():
    test_get_project_billing_info(request_type=dict)


@pytest.mark.asyncio
async def test_get_project_billing_info_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.GetProjectBillingInfoRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo(
                name="name_value",
                project_id="project_id_value",
                billing_account_name="billing_account_name_value",
                billing_enabled=True,
            )
        )

        response = await client.get_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.GetProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, cloud_billing.ProjectBillingInfo)

    assert response.name == "name_value"

    assert response.project_id == "project_id_value"

    assert response.billing_account_name == "billing_account_name_value"

    assert response.billing_enabled is True


@pytest.mark.asyncio
async def test_get_project_billing_info_async_from_dict():
    await test_get_project_billing_info_async(request_type=dict)


def test_get_project_billing_info_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.GetProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        call.return_value = cloud_billing.ProjectBillingInfo()

        client.get_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_project_billing_info_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.GetProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo()
        )

        await client.get_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_project_billing_info_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_project_billing_info(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


def test_get_project_billing_info_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_project_billing_info(
            cloud_billing.GetProjectBillingInfoRequest(), name="name_value",
        )


@pytest.mark.asyncio
async def test_get_project_billing_info_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.get_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_project_billing_info(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"


@pytest.mark.asyncio
async def test_get_project_billing_info_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_project_billing_info(
            cloud_billing.GetProjectBillingInfoRequest(), name="name_value",
        )


def test_update_project_billing_info(
    transport: str = "grpc", request_type=cloud_billing.UpdateProjectBillingInfoRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo(
            name="name_value",
            project_id="project_id_value",
            billing_account_name="billing_account_name_value",
            billing_enabled=True,
        )

        response = client.update_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.UpdateProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, cloud_billing.ProjectBillingInfo)

    assert response.name == "name_value"

    assert response.project_id == "project_id_value"

    assert response.billing_account_name == "billing_account_name_value"

    assert response.billing_enabled is True


def test_update_project_billing_info_from_dict():
    test_update_project_billing_info(request_type=dict)


@pytest.mark.asyncio
async def test_update_project_billing_info_async(
    transport: str = "grpc_asyncio",
    request_type=cloud_billing.UpdateProjectBillingInfoRequest,
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo(
                name="name_value",
                project_id="project_id_value",
                billing_account_name="billing_account_name_value",
                billing_enabled=True,
            )
        )

        response = await client.update_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == cloud_billing.UpdateProjectBillingInfoRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, cloud_billing.ProjectBillingInfo)

    assert response.name == "name_value"

    assert response.project_id == "project_id_value"

    assert response.billing_account_name == "billing_account_name_value"

    assert response.billing_enabled is True


@pytest.mark.asyncio
async def test_update_project_billing_info_async_from_dict():
    await test_update_project_billing_info_async(request_type=dict)


def test_update_project_billing_info_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.UpdateProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        call.return_value = cloud_billing.ProjectBillingInfo()

        client.update_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_update_project_billing_info_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = cloud_billing.UpdateProjectBillingInfoRequest()
    request.name = "name/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo()
        )

        await client.update_project_billing_info(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_update_project_billing_info_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.update_project_billing_info(
            name="name_value",
            project_billing_info=cloud_billing.ProjectBillingInfo(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].project_billing_info == cloud_billing.ProjectBillingInfo(
            name="name_value"
        )


def test_update_project_billing_info_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_project_billing_info(
            cloud_billing.UpdateProjectBillingInfoRequest(),
            name="name_value",
            project_billing_info=cloud_billing.ProjectBillingInfo(name="name_value"),
        )


@pytest.mark.asyncio
async def test_update_project_billing_info_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.update_project_billing_info), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = cloud_billing.ProjectBillingInfo()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            cloud_billing.ProjectBillingInfo()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.update_project_billing_info(
            name="name_value",
            project_billing_info=cloud_billing.ProjectBillingInfo(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].name == "name_value"

        assert args[0].project_billing_info == cloud_billing.ProjectBillingInfo(
            name="name_value"
        )


@pytest.mark.asyncio
async def test_update_project_billing_info_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.update_project_billing_info(
            cloud_billing.UpdateProjectBillingInfoRequest(),
            name="name_value",
            project_billing_info=cloud_billing.ProjectBillingInfo(name="name_value"),
        )


def test_get_iam_policy(
    transport: str = "grpc", request_type=iam_policy.GetIamPolicyRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.GetIamPolicyRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_get_iam_policy_from_dict():
    test_get_iam_policy(request_type=dict)


@pytest.mark.asyncio
async def test_get_iam_policy_async(
    transport: str = "grpc_asyncio", request_type=iam_policy.GetIamPolicyRequest
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.GetIamPolicyRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_get_iam_policy_async_from_dict():
    await test_get_iam_policy_async(request_type=dict)


def test_get_iam_policy_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_get_iam_policy_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.GetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.get_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_get_iam_policy_from_dict_foreign():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.get_iam_policy(
            request={
                "resource": "resource_value",
                "options": options.GetPolicyOptions(requested_policy_version=2598),
            }
        )
        call.assert_called()


def test_get_iam_policy_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.get_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


def test_get_iam_policy_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_iam_policy(
            iam_policy.GetIamPolicyRequest(), resource="resource_value",
        )


@pytest.mark.asyncio
async def test_get_iam_policy_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.get_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.get_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


@pytest.mark.asyncio
async def test_get_iam_policy_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.get_iam_policy(
            iam_policy.GetIamPolicyRequest(), resource="resource_value",
        )


def test_set_iam_policy(
    transport: str = "grpc", request_type=iam_policy.SetIamPolicyRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy(version=774, etag=b"etag_blob",)

        response = client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.SetIamPolicyRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


def test_set_iam_policy_from_dict():
    test_set_iam_policy(request_type=dict)


@pytest.mark.asyncio
async def test_set_iam_policy_async(
    transport: str = "grpc_asyncio", request_type=iam_policy.SetIamPolicyRequest
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            policy.Policy(version=774, etag=b"etag_blob",)
        )

        response = await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.SetIamPolicyRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, policy.Policy)

    assert response.version == 774

    assert response.etag == b"etag_blob"


@pytest.mark.asyncio
async def test_set_iam_policy_async_from_dict():
    await test_set_iam_policy_async(request_type=dict)


def test_set_iam_policy_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        call.return_value = policy.Policy()

        client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_set_iam_policy_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.SetIamPolicyRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())

        await client.set_iam_policy(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_set_iam_policy_from_dict_foreign():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        response = client.set_iam_policy(
            request={
                "resource": "resource_value",
                "policy": policy.Policy(version=774),
            }
        )
        call.assert_called()


def test_set_iam_policy_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.set_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


def test_set_iam_policy_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.set_iam_policy(
            iam_policy.SetIamPolicyRequest(), resource="resource_value",
        )


@pytest.mark.asyncio
async def test_set_iam_policy_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client.transport.set_iam_policy), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = policy.Policy()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(policy.Policy())
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.set_iam_policy(resource="resource_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"


@pytest.mark.asyncio
async def test_set_iam_policy_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.set_iam_policy(
            iam_policy.SetIamPolicyRequest(), resource="resource_value",
        )


def test_test_iam_permissions(
    transport: str = "grpc", request_type=iam_policy.TestIamPermissionsRequest
):
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse(
            permissions=["permissions_value"],
        )

        response = client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.TestIamPermissionsRequest()

    # Establish that the response is the type that we expect.

    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


def test_test_iam_permissions_from_dict():
    test_test_iam_permissions(request_type=dict)


@pytest.mark.asyncio
async def test_test_iam_permissions_async(
    transport: str = "grpc_asyncio", request_type=iam_policy.TestIamPermissionsRequest
):
    client = CloudBillingAsyncClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = request_type()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse(permissions=["permissions_value"],)
        )

        response = await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0] == iam_policy.TestIamPermissionsRequest()

    # Establish that the response is the type that we expect.
    assert isinstance(response, iam_policy.TestIamPermissionsResponse)

    assert response.permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_async_from_dict():
    await test_test_iam_permissions_async(request_type=dict)


def test_test_iam_permissions_field_headers():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = iam_policy.TestIamPermissionsResponse()

        client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


@pytest.mark.asyncio
async def test_test_iam_permissions_field_headers_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = iam_policy.TestIamPermissionsRequest()
    request.resource = "resource/value"

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse()
        )

        await client.test_iam_permissions(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "resource=resource/value",) in kw["metadata"]


def test_test_iam_permissions_from_dict_foreign():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)
    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        response = client.test_iam_permissions(
            request={
                "resource": "resource_value",
                "permissions": ["permissions_value"],
            }
        )
        call.assert_called()


def test_test_iam_permissions_flattened():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        client.test_iam_permissions(
            resource="resource_value", permissions=["permissions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"

        assert args[0].permissions == ["permissions_value"]


def test_test_iam_permissions_flattened_error():
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.test_iam_permissions(
            iam_policy.TestIamPermissionsRequest(),
            resource="resource_value",
            permissions=["permissions_value"],
        )


@pytest.mark.asyncio
async def test_test_iam_permissions_flattened_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client.transport.test_iam_permissions), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = iam_policy.TestIamPermissionsResponse()

        call.return_value = grpc_helpers_async.FakeUnaryUnaryCall(
            iam_policy.TestIamPermissionsResponse()
        )
        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = await client.test_iam_permissions(
            resource="resource_value", permissions=["permissions_value"],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls)
        _, args, _ = call.mock_calls[0]

        assert args[0].resource == "resource_value"

        assert args[0].permissions == ["permissions_value"]


@pytest.mark.asyncio
async def test_test_iam_permissions_flattened_error_async():
    client = CloudBillingAsyncClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        await client.test_iam_permissions(
            iam_policy.TestIamPermissionsRequest(),
            resource="resource_value",
            permissions=["permissions_value"],
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.CloudBillingGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudBillingClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )

    # It is an error to provide a credentials file and a transport instance.
    transport = transports.CloudBillingGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudBillingClient(
            client_options={"credentials_file": "credentials.json"},
            transport=transport,
        )

    # It is an error to provide scopes and a transport instance.
    transport = transports.CloudBillingGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = CloudBillingClient(
            client_options={"scopes": ["1", "2"]}, transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.CloudBillingGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = CloudBillingClient(transport=transport)
    assert client.transport is transport


def test_transport_get_channel():
    # A client may be instantiated with a custom transport instance.
    transport = transports.CloudBillingGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel

    transport = transports.CloudBillingGrpcAsyncIOTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    channel = transport.grpc_channel
    assert channel


@pytest.mark.parametrize(
    "transport_class",
    [transports.CloudBillingGrpcTransport, transports.CloudBillingGrpcAsyncIOTransport],
)
def test_transport_adc(transport_class):
    # Test default credentials are used if not provided.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport_class()
        adc.assert_called_once()


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = CloudBillingClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client.transport, transports.CloudBillingGrpcTransport,)


def test_cloud_billing_base_transport_error():
    # Passing both a credentials object and credentials_file should raise an error
    with pytest.raises(exceptions.DuplicateCredentialArgs):
        transport = transports.CloudBillingTransport(
            credentials=credentials.AnonymousCredentials(),
            credentials_file="credentials.json",
        )


def test_cloud_billing_base_transport():
    # Instantiate the base transport.
    with mock.patch(
        "google.cloud.billing_v1.services.cloud_billing.transports.CloudBillingTransport.__init__"
    ) as Transport:
        Transport.return_value = None
        transport = transports.CloudBillingTransport(
            credentials=credentials.AnonymousCredentials(),
        )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "get_billing_account",
        "list_billing_accounts",
        "update_billing_account",
        "create_billing_account",
        "list_project_billing_info",
        "get_project_billing_info",
        "update_project_billing_info",
        "get_iam_policy",
        "set_iam_policy",
        "test_iam_permissions",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_cloud_billing_base_transport_with_credentials_file():
    # Instantiate the base transport with a credentials file
    with mock.patch.object(
        auth, "load_credentials_from_file"
    ) as load_creds, mock.patch(
        "google.cloud.billing_v1.services.cloud_billing.transports.CloudBillingTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        load_creds.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.CloudBillingTransport(
            credentials_file="credentials.json", quota_project_id="octopus",
        )
        load_creds.assert_called_once_with(
            "credentials.json",
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_cloud_billing_base_transport_with_adc():
    # Test the default credentials are used if credentials and credentials_file are None.
    with mock.patch.object(auth, "default") as adc, mock.patch(
        "google.cloud.billing_v1.services.cloud_billing.transports.CloudBillingTransport._prep_wrapped_messages"
    ) as Transport:
        Transport.return_value = None
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transport = transports.CloudBillingTransport()
        adc.assert_called_once()


def test_cloud_billing_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        CloudBillingClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id=None,
        )


def test_cloud_billing_transport_auth_adc():
    # If credentials and host are not provided, the transport class should use
    # ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        transports.CloudBillingGrpcTransport(
            host="squid.clam.whelk", quota_project_id="octopus"
        )
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",),
            quota_project_id="octopus",
        )


def test_cloud_billing_host_no_port():
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="cloudbilling.googleapis.com"
        ),
    )
    assert client.transport._host == "cloudbilling.googleapis.com:443"


def test_cloud_billing_host_with_port():
    client = CloudBillingClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="cloudbilling.googleapis.com:8000"
        ),
    )
    assert client.transport._host == "cloudbilling.googleapis.com:8000"


def test_cloud_billing_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.CloudBillingGrpcTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


def test_cloud_billing_grpc_asyncio_transport_channel():
    channel = aio.insecure_channel("http://localhost/")

    # Check that channel is used if provided.
    transport = transports.CloudBillingGrpcAsyncIOTransport(
        host="squid.clam.whelk", channel=channel,
    )
    assert transport.grpc_channel == channel
    assert transport._host == "squid.clam.whelk:443"
    assert transport._ssl_channel_credentials == None


@pytest.mark.parametrize(
    "transport_class",
    [transports.CloudBillingGrpcTransport, transports.CloudBillingGrpcAsyncIOTransport],
)
def test_cloud_billing_transport_channel_mtls_with_client_cert_source(transport_class):
    with mock.patch(
        "grpc.ssl_channel_credentials", autospec=True
    ) as grpc_ssl_channel_cred:
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_ssl_cred = mock.Mock()
            grpc_ssl_channel_cred.return_value = mock_ssl_cred

            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel

            cred = credentials.AnonymousCredentials()
            with pytest.warns(DeprecationWarning):
                with mock.patch.object(auth, "default") as adc:
                    adc.return_value = (cred, None)
                    transport = transport_class(
                        host="squid.clam.whelk",
                        api_mtls_endpoint="mtls.squid.clam.whelk",
                        client_cert_source=client_cert_source_callback,
                    )
                    adc.assert_called_once()

            grpc_ssl_channel_cred.assert_called_once_with(
                certificate_chain=b"cert bytes", private_key=b"key bytes"
            )
            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel
            assert transport._ssl_channel_credentials == mock_ssl_cred


@pytest.mark.parametrize(
    "transport_class",
    [transports.CloudBillingGrpcTransport, transports.CloudBillingGrpcAsyncIOTransport],
)
def test_cloud_billing_transport_channel_mtls_with_adc(transport_class):
    mock_ssl_cred = mock.Mock()
    with mock.patch.multiple(
        "google.auth.transport.grpc.SslCredentials",
        __init__=mock.Mock(return_value=None),
        ssl_credentials=mock.PropertyMock(return_value=mock_ssl_cred),
    ):
        with mock.patch.object(
            transport_class, "create_channel", autospec=True
        ) as grpc_create_channel:
            mock_grpc_channel = mock.Mock()
            grpc_create_channel.return_value = mock_grpc_channel
            mock_cred = mock.Mock()

            with pytest.warns(DeprecationWarning):
                transport = transport_class(
                    host="squid.clam.whelk",
                    credentials=mock_cred,
                    api_mtls_endpoint="mtls.squid.clam.whelk",
                    client_cert_source=None,
                )

            grpc_create_channel.assert_called_once_with(
                "mtls.squid.clam.whelk:443",
                credentials=mock_cred,
                credentials_file=None,
                scopes=("https://www.googleapis.com/auth/cloud-platform",),
                ssl_credentials=mock_ssl_cred,
                quota_project_id=None,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )
            assert transport.grpc_channel == mock_grpc_channel


def test_common_billing_account_path():
    billing_account = "squid"

    expected = "billingAccounts/{billing_account}".format(
        billing_account=billing_account,
    )
    actual = CloudBillingClient.common_billing_account_path(billing_account)
    assert expected == actual


def test_parse_common_billing_account_path():
    expected = {
        "billing_account": "clam",
    }
    path = CloudBillingClient.common_billing_account_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudBillingClient.parse_common_billing_account_path(path)
    assert expected == actual


def test_common_folder_path():
    folder = "whelk"

    expected = "folders/{folder}".format(folder=folder,)
    actual = CloudBillingClient.common_folder_path(folder)
    assert expected == actual


def test_parse_common_folder_path():
    expected = {
        "folder": "octopus",
    }
    path = CloudBillingClient.common_folder_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudBillingClient.parse_common_folder_path(path)
    assert expected == actual


def test_common_organization_path():
    organization = "oyster"

    expected = "organizations/{organization}".format(organization=organization,)
    actual = CloudBillingClient.common_organization_path(organization)
    assert expected == actual


def test_parse_common_organization_path():
    expected = {
        "organization": "nudibranch",
    }
    path = CloudBillingClient.common_organization_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudBillingClient.parse_common_organization_path(path)
    assert expected == actual


def test_common_project_path():
    project = "cuttlefish"

    expected = "projects/{project}".format(project=project,)
    actual = CloudBillingClient.common_project_path(project)
    assert expected == actual


def test_parse_common_project_path():
    expected = {
        "project": "mussel",
    }
    path = CloudBillingClient.common_project_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudBillingClient.parse_common_project_path(path)
    assert expected == actual


def test_common_location_path():
    project = "winkle"
    location = "nautilus"

    expected = "projects/{project}/locations/{location}".format(
        project=project, location=location,
    )
    actual = CloudBillingClient.common_location_path(project, location)
    assert expected == actual


def test_parse_common_location_path():
    expected = {
        "project": "scallop",
        "location": "abalone",
    }
    path = CloudBillingClient.common_location_path(**expected)

    # Check that the path construction is reversible.
    actual = CloudBillingClient.parse_common_location_path(path)
    assert expected == actual


def test_client_withDEFAULT_CLIENT_INFO():
    client_info = gapic_v1.client_info.ClientInfo()

    with mock.patch.object(
        transports.CloudBillingTransport, "_prep_wrapped_messages"
    ) as prep:
        client = CloudBillingClient(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)

    with mock.patch.object(
        transports.CloudBillingTransport, "_prep_wrapped_messages"
    ) as prep:
        transport_class = CloudBillingClient.get_transport_class()
        transport = transport_class(
            credentials=credentials.AnonymousCredentials(), client_info=client_info,
        )
        prep.assert_called_once_with(client_info)
