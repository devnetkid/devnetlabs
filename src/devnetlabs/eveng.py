# src/devnetlabs/eveng.py

import json
import logging
import requests
# Needed to prevent InsecureRequestWarning from being printed to stdout
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

import requests

class EveNgClient:
    def __init__(self, host, username='admin', password='eve'):
        self.base_url = f"http://{host}/api"
        self.session = requests.Session()
        self.username = username
        self.password = password
        self.logged_in = False

    def login(self):
        url = f"{self.base_url}/auth/login"
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self.session.post(url, json=payload, verify=False)
        if response.status_code == 200 and response.json().get('code') == 200:
            self.logged_in = True
            print("Logged in successfully.")
        else:
            raise Exception(f"Login failed: {response.text}")

    def get_lab(self, lab_name):
        if not self.logged_in:
            raise Exception("Not logged in.")
        url = f"{self.base_url}/labs/{lab_name}.unl"
        response = self.session.get(url, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch labs: {response.text}")

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

    def create_lab(self, new_lab):
        if not self.logged_in:
            raise Exception("Not logged in.")
        url = f"{self.base_url}/labs"
        data = json.dumps(new_lab)
        response = self.session.post(url, data=data, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch labs: {response.text}")

    def logout(self):
        url = f"{self.base_url}/auth/logout"
        response = self.session.get(url, verify=False)
        if response.status_code == 200:
            self.logged_in = False
            print("Logged out successfully.")
        else:
            raise Exception(f"Logout failed: {response.text}")

