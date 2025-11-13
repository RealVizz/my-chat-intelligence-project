import asyncio

import httpx

from message_api import config
from message_api.schemas import ExternalMessagesResponseSchemaObj
from message_api.utils import db_utils


async def _fetch_messages_page(client: httpx.AsyncClient, skip: int, limit: int):
    """ Fetches a single page of messages from the external API with retry logic. """
    max_retries = 6
    timeout_seconds = 15
    retry_delay_seconds = 0.5

    for attempt in range(max_retries):
        try:
            response = await client.get(
                f"{config.EXTERNAL_API_BASE_URL}{config.EXTERNAL_API_MESSAGES_ENDPOINT}",
                params={"skip": skip, "limit": limit},
                timeout=timeout_seconds
            )
            response.raise_for_status()

            if response.json().get("detail") == "Oops!":
                print(f"Attempt {attempt + 1}/{max_retries}: Received 'Oops!' error. Retrying...")
                await asyncio.sleep(retry_delay_seconds)
                continue

            return ExternalMessagesResponseSchemaObj(**response.json())

        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Error fetching messages: {e}. Retrying...")
            await asyncio.sleep(retry_delay_seconds)

    print(f"Failed to fetch messages after {max_retries} attempts.")
    return None


def _process_and_store_messages(messages_response: ExternalMessagesResponseSchemaObj):
    """Processes a page of messages, stores them, and returns the count of new messages."""
    for message in messages_response.items:
        was_inserted = db_utils.add_raw_message(message.id, message.model_dump(mode='json'))
        if was_inserted:
            db_utils.add_identity_record(message.user_name, message.id)


async def _run_sync_cycle():
    """Runs 'seeker' synchronization cycle."""
    print("--- Starting background sync cycle ---")
    async with httpx.AsyncClient() as client:
        initial_response = await _fetch_messages_page(client, skip=0, limit=1)
        if not initial_response:
            print("Could not fetch remote total. Aborting sync cycle.")
            return

        remote_total = initial_response.total
        local_total = db_utils.get_raw_message_count()
        print(f"Remote has {remote_total} messages. Local has {local_total} messages.")

        if local_total >= remote_total:
            print("Sync cycle complete: Local data is up to date.")
            return

        skip = local_total

        while skip < remote_total:
            messages_response = await _fetch_messages_page(
                client, skip=skip, limit=config.EXTERNAL_API_PAGE_LIMIT
            )

            if not messages_response or not messages_response.items:
                print(f"Stopping sync due to API error or no items at skip={skip}.")
                break

            _process_and_store_messages(messages_response)
            print(f"Processed page starting at skip={skip}.")

            skip += len(messages_response.items)

    print("--- Sync cycle finished. ---")


async def start_background_sync():
    """The main background task loop that runs indefinitely."""
    while True:
        await _run_sync_cycle()
        # print(f"--- Sleeping for {config.BACKGROUND_SYNC_INTERVAL_SECONDS} seconds. ---")
        await asyncio.sleep(config.BACKGROUND_SYNC_INTERVAL_SECONDS)
