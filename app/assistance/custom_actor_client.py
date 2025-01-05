# Created: dylannguyen
from typing import Any
from apify_client._utils import encode_key_value_store_record_value, encode_webhook_list_to_base64, pluck_data
from apify_client.clients.resource_clients import ActorClient
from apify_shared.utils import (
    parse_date_fields,
)
from apify_client import ApifyClient
from apify_client._http_client import HTTPClient

class CustomActorClient(ActorClient):
    """Custom ActorClient with a modified `start` method to include a custom User-Agent header."""
    def __init__(self, headers: dict, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.headers = headers

    
    def start(
        self: ActorClient,
        *,
        run_input: Any = None,
        content_type: str | None = None,
        build: str | None = None,
        max_items: int | None = None,
        memory_mbytes: int | None = None,
        timeout_secs: int | None = None,
        wait_for_finish: int | None = None,
        webhooks: list[dict] | None = None,
    ) -> dict:
        run_input, content_type = encode_key_value_store_record_value(run_input, content_type)

        request_params = self._params(
            build=build,
            maxItems=max_items,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        # Modify the headers to include the custom User-Agent
        self.headers['content-type'] = content_type
        print(self.headers)
        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers=self.headers,
            data=run_input,
            params=request_params,
        )

        return parse_date_fields(pluck_data(response.json()))

class CustomApifyClient(ApifyClient):
    http_client: HTTPClient

    def __init__(
        self: ApifyClient,
        token: str | None = None,
        *,
        api_url: str | None = None,
        max_retries: int | None = 8,
        min_delay_between_retries_millis: int | None = 500,
        timeout_secs: int | None = 360,
        headers: dict
    ) -> None:
        """Initialize the ApifyClient.

        Args:
            token (str, optional): The Apify API token
            api_url (str, optional): The URL of the Apify API server to which to connect to. Defaults to https://api.apify.com
            max_retries (int, optional): How many times to retry a failed request at most
            min_delay_between_retries_millis (int, optional): How long will the client wait between retrying requests
                (increases exponentially from this value)
            timeout_secs (int, optional): The socket timeout of the HTTP requests sent to the Apify API
        """
        super().__init__(
            token,
            api_url=api_url,
            max_retries=max_retries,
            min_delay_between_retries_millis=min_delay_between_retries_millis,
            timeout_secs=timeout_secs,
        )

        self.http_client = HTTPClient(
            token=token,
            max_retries=self.max_retries,
            min_delay_between_retries_millis=self.min_delay_between_retries_millis,
            timeout_secs=self.timeout_secs,
        )
        
        self.headers = headers
        


    def actor(self: ApifyClient, actor_id: str) -> CustomActorClient:
        """Retrieve the sub-client for manipulating a single Actor.

        Args:
            actor_id (str): ID of the Actor to be manipulated
        """
        return CustomActorClient(resource_id=actor_id, headers = self.headers, **self._options())