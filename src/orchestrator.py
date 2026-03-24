import hashlib
import asyncio
import ipfs_client

class Orchestrator:
    def __init__(self, ipfs_endpoint):
        self.ipfs = ipfs_client.IPFSClient(ipfs_endpoint)

    async def cache_and_distribute(self, content):
        """
        Caches the given content on the IPFS network and distributes it to peers.
        
        Args:
            content (bytes): The content to be cached and distributed.
        
        Returns:
            str: The IPFS content ID (CID) of the cached content.
        """
        # Calculate the content hash
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Check if the content is already cached
        if await self.ipfs.is_content_cached(content_hash):
            return content_hash
        
        # Cache the content on IPFS
        cid = await self.ipfs.add_content(content)
        
        # Distribute the content to peers
        await self.ipfs.distribute_content(cid)
        
        return cid

    async def retrieve_content(self, cid):
        """
        Retrieves the content associated with the given IPFS content ID (CID).
        
        Args:
            cid (str): The IPFS content ID of the content to retrieve.
        
        Returns:
            bytes: The retrieved content.
        """
        return await self.ipfs.get_content(cid)
