import requests
from dataclasses import dataclass
from typing import Optional, Dict, Any
import json

@dataclass
class Choice:
    """Represents a form choice option for Kobo Toolbox surveys"""
    list_name: str
    value: str
    label: str
    kuid: str = None
    autovalue: str = None

    def __post_init__(self):
        self.kuid = f"k{requests.utils.quote(self.value)[:7]}"
        self.autovalue = self.value

    def to_dict(self) -> Dict[str, Any]:
        """Serialize choice to API-compatible dictionary"""
        return {
            "name": self.value,
            "label": [self.label],
            "list_name": self.list_name,
            "$kuid": self.kuid,
            "$autovalue": self.autovalue
        }

class KoboToolboxClient:
    """Base client for Kobo Toolbox API interactions"""
    def __init__(self, api_token: str, base_url: str = "https://eu.kobotoolbox.org/api/v2/"):
        self.base_url = base_url.rstrip('/') + '/'
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Accept": "application/json"
        }

    def _get(self, endpoint: str) -> requests.Response: 
        return requests.get(f"{self.base_url}{endpoint}", headers=self.headers)

    def _patch(self, endpoint: str, data: Dict, use_json: bool = True) -> requests.Response:
        """Flexible PATCH method that handles both JSON and form data"""
        url = f"{self.base_url}{endpoint.lstrip('/')}"
        if use_json:
            return requests.patch(url, headers=self.headers, json=data)
        return requests.patch(url, headers=self.headers, data=data)

class FormManager(KoboToolboxClient):
    """Manages form configurations and updates for Kobo Toolbox surveys"""
    def __init__(self, api_token: str, asset_uid: str):
        super().__init__(api_token)
        self.asset_uid = asset_uid
        self.asset_data: Optional[Dict] = None
        self.latest_version_id: Optional[str] = None
        self.deployed_version_id: Optional[str] = None

    def refresh_version_info(self):
        """Update version information from API"""
        response = self._get(f"assets/{self.asset_uid}/")
        if response.status_code == 200:
            data = response.json()
            self.latest_version_id = data.get('version_id')
            self.deployed_version_id = data.get('deployed_version_id')
            return True
        return False

    def fetch_form_structure(self) -> bool:
        """Retrieve current form structure from API"""
        response = self._get(f"assets/{self.asset_uid}/")
        if response.status_code == 200:
            self.asset_data = response.json()
            self.refresh_version_info()
            return True
        print(f"Failed to fetch form structure: {response.text}")
        return False

    def add_choice(self, choice: Choice) -> bool:
        """Add a new choice to the form structure"""
        if not self.asset_data:
            raise ValueError("Form structure not loaded - call fetch_form_structure first")
        
        try:
            self.asset_data['content']['choices'].append(choice.to_dict())
            return True
        except KeyError as e:
            print(f"Invalid form structure: {e}")
            return False

    def update_form(self) -> bool:
        """Push updated form structure to Kobo Toolbox and get new version ID"""
        if not self.asset_data:
            return False

        response = self._patch(f"assets/{self.asset_uid}/", self.asset_data)
        if response.status_code != 200:
            print(f"Form update failed: {response.text}")
            return False

        self.latest_version_id = response.json().get('version_id')
        print(f"Form updated successfully (New version: {self.latest_version_id})")
        return self.refresh_version_info()

    def redeploy_form(self, version_id: str = None) -> bool:
        """Redeploy form with specific version (uses latest if not specified)"""
        target_version = version_id or self.latest_version_id
        if not target_version:
            print("No version specified and no updates available")
            return False

        response = self._patch(
            f"assets/{self.asset_uid}/deployment/",
            {"version_id": target_version},
            use_json=False  # Send as form data
        )
        
        if response.status_code == 200:
            print(f"Successfully redeployed version {target_version}")
            self.deployed_version_id = target_version
            return True
            
        print(f"Redeployment failed: {response.text}")
        return False

    def needs_redeploy(self) -> bool:
        """Check if latest version is deployed"""
        return self.latest_version_id != self.deployed_version_id

    def update_and_redeploy(self, choice: Choice) -> bool:
        """Complete update cycle with validation"""
        if not all([
            self.fetch_form_structure(),
            self.add_choice(choice),
            self.update_form()
        ]):
            return False

        if self.needs_redeploy():
            return self.redeploy_form()
        
        print("Latest version already deployed")
        return True
    def export_data(self):
        response = self._get(f"assets/{self.asset_uid}/data.json")
        response = response.json()
        response = response["results"]
        with open("data.json", "w") as f:
            json.dump(response, f, indent=4)
            