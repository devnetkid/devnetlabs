# src/devnetlabs/eveng.py

import json
import logging

import requests
# Needed to prevent InsecureRequestWarning from being printed to stdout
from requests.packages import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)

logger = logging.getLogger(__name__)

import requests


class EveNgClient:
    def __init__(self, host, username="admin", password="eve"):
        self.base_url = f"http://{host}/api"
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False

    def login(self):
        url = f"{self.base_url}/auth/login"
        payload = {"username": self.username, "password": self.password}
        try:
            response = self.session.post(url, json=payload, verify=False)
            if response.status_code == 200 and response.json().get("code") == 200:
                self.logged_in = True
                print("Logged in successfully.")
            else:
                raise Exception(f"Login failed: {response.text}")
        except Timeout:
            print("Request timed out. Try again later.")
        except ConnectionError:
            print("Connection error. Check your network.")
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except RequestException as err:
            print(f"General error occurred: {err}")

    def list_labs(self):
        """
        List the folders and labs in the root folder
        """
        url = f"{self.base_url}/folders/"
        response = self.session.get(url, verify=False)
        return response.json()

    def get_lab(self, lab_name):
        if not self.logged_in:
            raise Exception("Not logged in.")
        url = f"{self.base_url}/labs/{lab_name}.unl"
        try:
            response = self.session.get(url, verify=False)
            if response.status_code == 200:
                return response.json()
        except Exception as err:
            print(f"Failed to fetch labs: {response.text}")

    def get_lab_nodes(self, lab_name):
        if not self.logged_in:
            raise Exception("Not logged in.")
        url = f"{self.base_url}/labs/{lab_name}.unl/nodes"
        response = self.session.get(url, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch labs: {response.text}")

    def get_lab_topology(self, lab_name):
        if not self.logged_in:
            raise Exception("Not logged in.")
        url = f"{self.base_url}/labs/{lab_name}.unl/topology"
        response = self.session.get(url, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch labs: {response.text}")

    def get_intf(self, lab_name, node_id):
        """Get specified lab topology"""
        url = f"{self.base_url}/labs/{lab_name}.unl/nodes/{node_id}/interfaces"
        response = self.session.get(url, verify=False)
        return response.json()

    def create_lab(self, lab):
        """
        Creates a new lab in eve-ng from a toml configuration file

        Args:
            lab (dict): toml configuration file describing lab components.
        """
        url = f"{self.base_url}/labs"
        data = json.dumps(lab)
        try:
            response = self.session.post(url, data=data, verify=False)
            return response.json()
        except Exception as err:
            print(f"Failed to create lab: {err}")

    def delete_lab(self, lab):
        """
        Deletes a lab from eve-ng

        Args:
            lab (string): The name of the lab to delete.
        """
        url = f"{self.base_url}/labs/{lab}.unl"
        response = self.session.delete(url, verify=False)
        return response.json()

    def create_node(self, lab, node_data):
        url = f"{self.base_url}/labs/{lab}.unl/nodes"
        data = json.dumps(node_data)
        response = self.session.post(url=url, data=data, verify=False)
        return response.json()

    def create_network(self, lab, new_network):
        """
        Creates a network object in eve-ng

        Args:
            lab (string): The name of the lab to delete.
            new_network (dict): The network object to be created.
        """
        url = f"{self.base_url}/labs/{lab}.unl/networks"
        data = json.dumps(new_network)
        response = self.session.post(url=url, data=data, verify=False)
        return response.json()

    def set_intf(self, lab_name, node_id, data):
        """Get specified lab topology"""
        url = f"{self.base_url}/labs/{lab_name}.unl/nodes/{node_id}/interfaces"
        data = json.dumps(data)
        response = self.session.put(url=url, data=data, verify=False)
        return response.json()

    def modify_network(self, lab_name, bridge_id, data):
        """Creates a new lab in eve-ng"""
        url = f"{self.base_url}/labs/{lab_name}.unl/networks/{bridge_id}"
        data = json.dumps(data)
        response = self.session.put(url=url, data=data, verify=False)
        return response.json()

    def logout(self):
        url = f"{self.base_url}/auth/logout"
        response = self.session.get(url, verify=False)
        if response.status_code == 200:
            self.logged_in = False
            print("Logged out successfully.")
        else:
            raise Exception(f"Logout failed: {response.text}")
