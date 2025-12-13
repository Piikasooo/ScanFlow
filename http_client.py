import aiohttp

class HTTPClient:
    session: aiohttp.ClientSession = None

    @classmethod
    def get_session(cls):
        if cls.session is None:
            connector = aiohttp.TCPConnector(ssl=False)
            cls.session = aiohttp.ClientSession(connector=connector)
        return cls.session

    @classmethod
    async def close(cls):
        if cls.session:
            await cls.session.close()
            cls.session = None

http_client = HTTPClient()