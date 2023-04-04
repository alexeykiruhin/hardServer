import asyncio
import websockets


async def websocket_handler(websocket, path):
    async for message in websocket:
        # Обработка входящих сообщений от клиента
        response = f"Вы сказали: {message}"
        await websocket.send(response)


async def main():
    async with websockets.serve(websocket_handler, "localhost", 8764):
        print('awaiting...')
        await asyncio.Future()  # Ожидание завершения работы сервера


if __name__ == "__main__":
    asyncio.run(main())
