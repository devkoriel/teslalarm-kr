import asyncio

import aiohttp


async def fetch_async(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


async def fetch_all_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        texts = []
        for resp in responses:
            texts.append(await resp.text())
        return texts
