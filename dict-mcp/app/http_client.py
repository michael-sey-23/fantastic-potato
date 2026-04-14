import logging

from typing import Any, Optional
import httpx

logger = logging.getLogger(__name__)

class AuthenticatedClient:
    """Authenticated HTTP client for calling the Java backend REST API with JWT tokens."""

    def __init__(self, base_url: str, username: str, password: str) -> None:
        """
        Initialize the authenticated client.

        Args:
            base_url: The base URL of the Java backend (e.g., http://localhost:8080)
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient()


    async def login(self) -> None:
        """
        Authenticate with the Java backend and store the JWT token.

        Raises:
            Exception: If login fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/auth/login",
                    json={"username": self.username, "password": self.password}
                )
                response.raise_for_status()
                data = response.json()
                self.token = data["token"]
                logger.info(f"Successfully logged in as {self.username}")
            except httpx.HTTPError as e:
                logger.error(f"Houston, we have a problem : {str(e)}")
                raise Exception(f"Login failed: {str(e)}")


    async def get(self, endpoint: str, **kwargs: Any) -> Any:
        """
        Make an authenticated GET request.

        Args:
            endpoint: The API endpoint (relative path)
            **kwargs: Additional parameters (passed as query params)

        Returns:
            JSON response from the server

        Raises:
            Exception: If the request fails
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=kwargs
            )
            response.raise_for_status()
            logger.info("This works yay")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Houston, we have a problem : {str(e)}")
            raise Exception(f"Failed to make get request: {str(e)}")


    async def post(self, endpoint: str, json_data: dict, **kwargs: Any) -> Any:
        """
        Make an authenticated POST request.

        Args:
            endpoint: The API endpoint (relative path)
            json_data: JSON body to send
            **kwargs: Additional parameters (passed as query params)

        Returns:
            JSON response from the server

        Raises:
            Exception: If the request fails
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=kwargs,
                json=json_data
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Oh No! Post request failed! : {str(e)}")
            raise Exception(f"Failed to make post request: {str(e)}")


    async def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """
        Make an authenticated DELETE request.

        Args:
            endpoint: The API endpoint (relative path)
            **kwargs: Additional parameters (passed as query params)

        Returns:
            JSON response from the server

        Raises:
            Exception: If the request fails
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = await self.client.delete(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Okay so the delete request failed :( : {str(e)}")
            raise Exception(f"Failed to make delete request: {str(e)}")
#