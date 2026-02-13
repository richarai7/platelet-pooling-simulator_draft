"""
Azure Digital Twins Client
Handles connection to Azure Digital Twins and twin property updates
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

try:
    from azure.identity import DefaultAzureCredential
    from azure.digitaltwins.core import DigitalTwinsClient
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    logging.warning("Azure SDK not installed. Install with: pip install azure-identity azure-digitaltwins-core")


@dataclass
class TwinUpdate:
    """Represents a twin property update"""
    twin_id: str
    properties: Dict[str, Any]
    timestamp: datetime


class DigitalTwinsClientWrapper:
    """
    Wrapper for Azure Digital Twins client with batching and throttling
    """
    
    def __init__(
        self,
        adt_endpoint: str,
        batch_size: int = 10,
        batch_interval_seconds: float = 1.0,
        max_retries: int = 3
    ):
        """
        Initialize Digital Twins client
        
        Args:
            adt_endpoint: Azure Digital Twins instance endpoint URL
            batch_size: Maximum number of updates to batch together
            batch_interval_seconds: Time to wait before flushing batch
            max_retries: Maximum retry attempts for failed updates
        """
        self.adt_endpoint = adt_endpoint
        self.batch_size = batch_size
        self.batch_interval_seconds = batch_interval_seconds
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
        # Initialize client if Azure SDK is available
        self.client: Optional[DigitalTwinsClient] = None
        self.is_mock = not AZURE_SDK_AVAILABLE or adt_endpoint.startswith("mock://")
        
        if not self.is_mock:
            try:
                credential = DefaultAzureCredential()
                self.client = DigitalTwinsClient(adt_endpoint, credential)
                self.logger.info(f"Connected to Azure Digital Twins: {adt_endpoint}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Azure Digital Twins: {e}")
                self.is_mock = True
        
        if self.is_mock:
            self.logger.warning("Running in MOCK mode - updates will be logged but not sent to Azure")
        
        # Batching state
        self._update_queue: List[TwinUpdate] = []
        self._last_flush_time = datetime.now()
        
    async def update_twin_properties(
        self,
        twin_id: str,
        properties: Dict[str, Any],
        flush_immediately: bool = False
    ) -> bool:
        """
        Update properties of a digital twin with batching support
        
        Args:
            twin_id: ID of the twin to update
            properties: Dictionary of properties to update
            flush_immediately: If True, bypass batching and update immediately
            
        Returns:
            True if update succeeded (or queued), False otherwise
        """
        update = TwinUpdate(
            twin_id=twin_id,
            properties=properties,
            timestamp=datetime.now()
        )
        
        if flush_immediately:
            return await self._send_update(update)
        else:
            self._update_queue.append(update)
            
            # Flush if batch size reached or interval elapsed
            time_since_flush = (datetime.now() - self._last_flush_time).total_seconds()
            if len(self._update_queue) >= self.batch_size or time_since_flush >= self.batch_interval_seconds:
                return await self.flush_updates()
            
            return True
    
    async def flush_updates(self) -> bool:
        """
        Flush all queued updates to Azure Digital Twins
        
        Returns:
            True if all updates succeeded, False otherwise
        """
        if not self._update_queue:
            return True
        
        self.logger.info(f"Flushing {len(self._update_queue)} twin updates")
        
        success = True
        for update in self._update_queue:
            if not await self._send_update(update):
                success = False
        
        self._update_queue.clear()
        self._last_flush_time = datetime.now()
        
        return success
    
    async def _send_update(self, update: TwinUpdate) -> bool:
        """
        Send a single update to Azure Digital Twins with retry logic
        
        Args:
            update: The twin update to send
            
        Returns:
            True if update succeeded, False otherwise
        """
        if self.is_mock:
            # Mock mode - just log the update
            self.logger.info(f"[MOCK] Update twin {update.twin_id}: {update.properties}")
            return True
        
        for attempt in range(self.max_retries):
            try:
                # Create JSON Patch document for property updates
                patch = []
                for key, value in update.properties.items():
                    patch.append({
                        "op": "replace",
                        "path": f"/{key}",
                        "value": value
                    })
                
                # Update twin using Azure SDK
                self.client.update_digital_twin(update.twin_id, patch)
                self.logger.debug(f"Updated twin {update.twin_id} successfully")
                return True
                
            except Exception as e:
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed for twin {update.twin_id}: {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to update twin {update.twin_id} after {self.max_retries} attempts")
                    return False
        
        return False
    
    async def get_twin(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a digital twin by ID
        
        Args:
            twin_id: ID of the twin to retrieve
            
        Returns:
            Twin data as dictionary, or None if not found
        """
        if self.is_mock:
            self.logger.info(f"[MOCK] Get twin {twin_id}")
            return {"$dtId": twin_id, "$metadata": {}}
        
        try:
            twin = self.client.get_digital_twin(twin_id)
            return twin
        except Exception as e:
            self.logger.error(f"Failed to get twin {twin_id}: {e}")
            return None
    
    async def create_or_update_twin(
        self,
        twin_id: str,
        model_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        Create a new twin or update if it already exists
        
        Args:
            twin_id: ID of the twin
            model_id: DTDL model ID
            properties: Initial properties
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_mock:
            self.logger.info(f"[MOCK] Create/update twin {twin_id} with model {model_id}")
            return True
        
        try:
            # Check if twin exists
            existing = await self.get_twin(twin_id)
            
            if existing:
                # Update existing twin
                return await self.update_twin_properties(twin_id, properties, flush_immediately=True)
            else:
                # Create new twin
                twin_data = {
                    "$dtId": twin_id,
                    "$metadata": {
                        "$model": model_id
                    },
                    **properties
                }
                self.client.upsert_digital_twin(twin_id, twin_data)
                self.logger.info(f"Created twin {twin_id} with model {model_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create/update twin {twin_id}: {e}")
            return False
    
    def close(self):
        """Close the client connection"""
        if self.client:
            self.logger.info("Closing Azure Digital Twins client")
            # Azure SDK client doesn't require explicit close
