"""Necessary imports to test configuration data model logic."""

import unittest
from typing import Any

from packages_engine.models.configuration import ConfigurationData


class TestConfigurationData(unittest.TestCase):
    """Configuration data model logic tests."""

    data: ConfigurationData
    data_obj: Any

    def setUp(self):
        self.data = ConfigurationData(
            server_data_dir="srv",
            remote_ip_address="127.0.0.1",
            domain_name="internal.app",
            gitea_db_name="gitea-db",
            gitea_db_user="gitea-usr",
            gitea_db_password="gitea-pwd",
            pg_admin_email="user@example.com",
            pg_admin_password="pg-admin-pwd",
            num_wireguard_clients=2,
            wireguard_client_names=["limitless", "viewer"],
            clients_data_dir="/usr/local/share/clients",
        )
        self.data_obj = {
            "server_data_dir": "srv",
            "remote_ip_address": "127.0.0.1",
            "domain_name": "internal.app",
            "gitea_db_name": "gitea-db",
            "gitea_db_user": "gitea-usr",
            "gitea_db_password": "gitea-pwd",
            "pg_admin_email": "user@example.com",
            "pg_admin_password": "pg-admin-pwd",
            "num_wireguard_clients": 2,
            "wireguard_client_names": ["limitless", "viewer"],
            "clients_data_dir": "/usr/local/share/clients",
        }

    def test_converts_to_object_representation(self):
        """Converts to object representation."""
        # Act
        result = self.data.as_object()

        # Assert
        self.assertEqual(result, self.data_obj)

    def test_converts_from_object_representation(self):
        """Converts from object representation."""
        # Act
        result = ConfigurationData.from_object(self.data_obj)

        # Assert
        self.assertEqual(result, self.data)

    def test_conversion_integration(self):
        """Convertion integration"""
        # Act
        result_one = ConfigurationData.from_object(self.data_obj)
        result_two = result_one.as_object()
        result_three = ConfigurationData.from_object(result_two)

        # Assert
        self.assertEqual(result_one, self.data)
        self.assertEqual(result_two, self.data_obj)
        self.assertEqual(result_three, self.data)
