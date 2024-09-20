import asyncio
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        response = await session.post('http://localhost:8080/post/', 
                                      json={"title": "hello_world:D", 
                                            "description": "program on Python", 
                                            "owner": "Really Positive Person"},)
        print(response.status)
        print(await response.text())
        
        response = await session.post('http://localhost:8080/post/', 
                                      json={"title": "byeeee?", 
                                            "description": "how to write consequential code", 
                                            "owner": "Pedantic Programmer"},
                                            headers={"token": "cdhjjjjj3jee8fh"})
        print(response.status)
        print(await response.text())

        response = await session.get('http://localhost:8080/post/2/')
        print(response.status)
        print(await response.text())
        response = await session.patch('http://localhost:8080/post/2/',
                                       json={"title": "Coding tutorial"})
        print(response.status)
        print(await response.text())

        response = await session.get('http://localhost:8080/post/2/')
        print(response.status)
        print(await response.text())

        response = await session.delete('http://localhost:8080/post/2/')
        print(response.status)
        print(await response.text())

        response = await session.get('http://localhost:8080/post/2/')
        print(response.status)
        print(await response.text())

if __name__ == "__main__":
    asyncio.run(main())
