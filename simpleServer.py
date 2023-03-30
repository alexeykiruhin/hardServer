import asyncio
import websockets
import json

# count connected users
connected_clients = set()
# count rooms
rooms = {}


async def handle(websocket):
    connected_clients.add(websocket)
    print(f'New connect. All connects: {len(connected_clients)}')

    msg = await websocket.recv()
    msg_json = json.loads(msg)
    print(f'msg_json: {msg_json}')
    if msg_json['action'] == 'CREATE':
        room_name = msg_json['room_name']
        room_pwd = msg_json['room_pwd']
        if room_name not in rooms:
            rooms[room_name] = room_name
            rooms[room_name] = {'pwd': room_pwd, 'list': []}
            print(rooms)
            response = json.dumps({'room_name': room_name, 'cnt_users': len(rooms[room_name]['list'])})
        else:
            response = '0'
    await websocket.send(response)


async def main():
    async with websockets.serve(handle, 'localhost', 5000):
        print('awaiting...')
        await asyncio.Future()


asyncio.run(main())
