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

from typing import Callable, Dict

from google.api_core import grpc_helpers  # type: ignore
from google.auth import credentials  # type: ignore

import grpc  # type: ignore

from google.cloud.billing_v1.types import cloud_billing
from google.iam.v1 import iam_policy_pb2 as iam_policy  # type: ignore
from google.iam.v1 import policy_pb2 as policy  # type: ignore

from .base import CloudBillingTransport


class CloudBillingGrpcTransport(CloudBillingTransport):
    """gRPC backend transport for CloudBilling.

    Retrieves GCP Console billing accounts and associates them
    with projects.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    def __init__(
        self,
        *,
        host: str = "cloudbilling.googleapis.com",
        credentials: credentials.Credentials = None,
        channel: grpc.Channel = None
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            channel (Optional[grpc.Channel]): A ``Channel`` instance through
                which to make calls.
        """
        # Sanity check: Ensure that channel and credentials are not both
        # provided.
        if channel:
            credentials = False

        # Run the base constructor.
        super().__init__(host=host, credentials=credentials)
        self._stubs = {}  # type: Dict[str, Callable]

        # If a channel was explicitly provided, set it.
        if channel:
            self._grpc_channel = channel

    @classmethod
    def create_channel(
        cls,
        host: str = "cloudbilling.googleapis.com",
        credentials: credentials.Credentials = None,
        **kwargs
    ) -> grpc.Channel:
        """Create and return a gRPC channel object.
        Args:
            address (Optionsl[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            grpc.Channel: A gRPC channel object.
        """
        return grpc_helpers.create_channel(
            host, credentials=credentials, scopes=cls.AUTH_SCOPES, **kwargs
        )

    @property
    def grpc_channel(self) -> grpc.Channel:
        """Create the channel designed to connect to this service.

        This property caches on the instance; repeated calls return
        the same channel.
        """
        # Sanity check: Only create a new channel if we do not already
        # have one.
        if not hasattr(self, "_grpc_channel"):
            self._grpc_channel = self.create_channel(
                self._host, credentials=self._credentials
            )

        # Return the channel from cache.
        return self._grpc_channel

    @property
    def get_billing_account(
        self
    ) -> Callable[
        [cloud_billing.GetBillingAccountRequest], cloud_billing.BillingAccount
    ]:
        r"""Return a callable for the get billing account method over gRPC.

        Gets information about a billing account. The current
        authenticated user must be a `viewer of the billing
        account <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        Returns:
            Callable[[~.GetBillingAccountRequest],
                    ~.BillingAccount]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_billing_account" not in self._stubs:
            self._stubs["get_billing_account"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/GetBillingAccount",
                request_serializer=cloud_billing.GetBillingAccountRequest.serialize,
                response_deserializer=cloud_billing.BillingAccount.deserialize,
            )
        return self._stubs["get_billing_account"]

    @property
    def list_billing_accounts(
        self
    ) -> Callable[
        [cloud_billing.ListBillingAccountsRequest],
        cloud_billing.ListBillingAccountsResponse,
    ]:
        r"""Return a callable for the list billing accounts method over gRPC.

        Lists the billing accounts that the current authenticated user
        has permission to
        `view <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        Returns:
            Callable[[~.ListBillingAccountsRequest],
                    ~.ListBillingAccountsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_billing_accounts" not in self._stubs:
            self._stubs["list_billing_accounts"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/ListBillingAccounts",
                request_serializer=cloud_billing.ListBillingAccountsRequest.serialize,
                response_deserializer=cloud_billing.ListBillingAccountsResponse.deserialize,
            )
        return self._stubs["list_billing_accounts"]

    @property
    def update_billing_account(
        self
    ) -> Callable[
        [cloud_billing.UpdateBillingAccountRequest], cloud_billing.BillingAccount
    ]:
        r"""Return a callable for the update billing account method over gRPC.

        Updates a billing account's fields. Currently the only field
        that can be edited is ``display_name``. The current
        authenticated user must have the ``billing.accounts.update`` IAM
        permission, which is typically given to the
        `administrator <https://cloud.google.com/billing/docs/how-to/billing-access>`__
        of the billing account.

        Returns:
            Callable[[~.UpdateBillingAccountRequest],
                    ~.BillingAccount]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_billing_account" not in self._stubs:
            self._stubs["update_billing_account"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/UpdateBillingAccount",
                request_serializer=cloud_billing.UpdateBillingAccountRequest.serialize,
                response_deserializer=cloud_billing.BillingAccount.deserialize,
            )
        return self._stubs["update_billing_account"]

    @property
    def create_billing_account(
        self
    ) -> Callable[
        [cloud_billing.CreateBillingAccountRequest], cloud_billing.BillingAccount
    ]:
        r"""Return a callable for the create billing account method over gRPC.

        Creates a billing account. This method can only be used to
        create `billing
        subaccounts <https://cloud.google.com/billing/docs/concepts>`__
        by GCP resellers. When creating a subaccount, the current
        authenticated user must have the ``billing.accounts.update`` IAM
        permission on the master account, which is typically given to
        billing account
        `administrators <https://cloud.google.com/billing/docs/how-to/billing-access>`__.
        This method will return an error if the master account has not
        been provisioned as a reseller account.

        Returns:
            Callable[[~.CreateBillingAccountRequest],
                    ~.BillingAccount]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_billing_account" not in self._stubs:
            self._stubs["create_billing_account"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/CreateBillingAccount",
                request_serializer=cloud_billing.CreateBillingAccountRequest.serialize,
                response_deserializer=cloud_billing.BillingAccount.deserialize,
            )
        return self._stubs["create_billing_account"]

    @property
    def list_project_billing_info(
        self
    ) -> Callable[
        [cloud_billing.ListProjectBillingInfoRequest],
        cloud_billing.ListProjectBillingInfoResponse,
    ]:
        r"""Return a callable for the list project billing info method over gRPC.

        Lists the projects associated with a billing account. The
        current authenticated user must have the
        ``billing.resourceAssociations.list`` IAM permission, which is
        often given to billing account
        `viewers <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        Returns:
            Callable[[~.ListProjectBillingInfoRequest],
                    ~.ListProjectBillingInfoResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_project_billing_info" not in self._stubs:
            self._stubs["list_project_billing_info"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/ListProjectBillingInfo",
                request_serializer=cloud_billing.ListProjectBillingInfoRequest.serialize,
                response_deserializer=cloud_billing.ListProjectBillingInfoResponse.deserialize,
            )
        return self._stubs["list_project_billing_info"]

    @property
    def get_project_billing_info(
        self
    ) -> Callable[
        [cloud_billing.GetProjectBillingInfoRequest], cloud_billing.ProjectBillingInfo
    ]:
        r"""Return a callable for the get project billing info method over gRPC.

        Gets the billing information for a project. The current
        authenticated user must have `permission to view the
        project <https://cloud.google.com/docs/permissions-overview#h.bgs0oxofvnoo>`__.

        Returns:
            Callable[[~.GetProjectBillingInfoRequest],
                    ~.ProjectBillingInfo]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_project_billing_info" not in self._stubs:
            self._stubs["get_project_billing_info"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/GetProjectBillingInfo",
                request_serializer=cloud_billing.GetProjectBillingInfoRequest.serialize,
                response_deserializer=cloud_billing.ProjectBillingInfo.deserialize,
            )
        return self._stubs["get_project_billing_info"]

    @property
    def update_project_billing_info(
        self
    ) -> Callable[
        [cloud_billing.UpdateProjectBillingInfoRequest],
        cloud_billing.ProjectBillingInfo,
    ]:
        r"""Return a callable for the update project billing info method over gRPC.

        Sets or updates the billing account associated with a project.
        You specify the new billing account by setting the
        ``billing_account_name`` in the ``ProjectBillingInfo`` resource
        to the resource name of a billing account. Associating a project
        with an open billing account enables billing on the project and
        allows charges for resource usage. If the project already had a
        billing account, this method changes the billing account used
        for resource usage charges.

        *Note:* Incurred charges that have not yet been reported in the
        transaction history of the GCP Console might be billed to the
        new billing account, even if the charge occurred before the new
        billing account was assigned to the project.

        The current authenticated user must have ownership privileges
        for both the
        `project <https://cloud.google.com/docs/permissions-overview#h.bgs0oxofvnoo>`__
        and the `billing
        account <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        You can disable billing on the project by setting the
        ``billing_account_name`` field to empty. This action
        disassociates the current billing account from the project. Any
        billable activity of your in-use services will stop, and your
        application could stop functioning as expected. Any unbilled
        charges to date will be billed to the previously associated
        account. The current authenticated user must be either an owner
        of the project or an owner of the billing account for the
        project.

        Note that associating a project with a *closed* billing account
        will have much the same effect as disabling billing on the
        project: any paid resources used by the project will be shut
        down. Thus, unless you wish to disable billing, you should
        always call this method with the name of an *open* billing
        account.

        Returns:
            Callable[[~.UpdateProjectBillingInfoRequest],
                    ~.ProjectBillingInfo]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_project_billing_info" not in self._stubs:
            self._stubs["update_project_billing_info"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/UpdateProjectBillingInfo",
                request_serializer=cloud_billing.UpdateProjectBillingInfoRequest.serialize,
                response_deserializer=cloud_billing.ProjectBillingInfo.deserialize,
            )
        return self._stubs["update_project_billing_info"]

    @property
    def get_iam_policy(
        self
    ) -> Callable[[iam_policy.GetIamPolicyRequest], policy.Policy]:
        r"""Return a callable for the get iam policy method over gRPC.

        Gets the access control policy for a billing account. The caller
        must have the ``billing.accounts.getIamPolicy`` permission on
        the account, which is often given to billing account
        `viewers <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        Returns:
            Callable[[~.GetIamPolicyRequest],
                    ~.Policy]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_iam_policy" not in self._stubs:
            self._stubs["get_iam_policy"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/GetIamPolicy",
                request_serializer=iam_policy.GetIamPolicyRequest.SerializeToString,
                response_deserializer=policy.Policy.FromString,
            )
        return self._stubs["get_iam_policy"]

    @property
    def set_iam_policy(
        self
    ) -> Callable[[iam_policy.SetIamPolicyRequest], policy.Policy]:
        r"""Return a callable for the set iam policy method over gRPC.

        Sets the access control policy for a billing account. Replaces
        any existing policy. The caller must have the
        ``billing.accounts.setIamPolicy`` permission on the account,
        which is often given to billing account
        `administrators <https://cloud.google.com/billing/docs/how-to/billing-access>`__.

        Returns:
            Callable[[~.SetIamPolicyRequest],
                    ~.Policy]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "set_iam_policy" not in self._stubs:
            self._stubs["set_iam_policy"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/SetIamPolicy",
                request_serializer=iam_policy.SetIamPolicyRequest.SerializeToString,
                response_deserializer=policy.Policy.FromString,
            )
        return self._stubs["set_iam_policy"]

    @property
    def test_iam_permissions(
        self
    ) -> Callable[
        [iam_policy.TestIamPermissionsRequest], iam_policy.TestIamPermissionsResponse
    ]:
        r"""Return a callable for the test iam permissions method over gRPC.

        Tests the access control policy for a billing
        account. This method takes the resource and a set of
        permissions as input and returns the subset of the input
        permissions that the caller is allowed for that
        resource.

        Returns:
            Callable[[~.TestIamPermissionsRequest],
                    ~.TestIamPermissionsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "test_iam_permissions" not in self._stubs:
            self._stubs["test_iam_permissions"] = self.grpc_channel.unary_unary(
                "/google.cloud.billing.v1.CloudBilling/TestIamPermissions",
                request_serializer=iam_policy.TestIamPermissionsRequest.SerializeToString,
                response_deserializer=iam_policy.TestIamPermissionsResponse.FromString,
            )
        return self._stubs["test_iam_permissions"]


__all__ = ("CloudBillingGrpcTransport",)