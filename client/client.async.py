
import asyncio
import websockets
import os
import json
import requests
import logging

async def start():
    async with websockets.connect(os.getenv('WS_SERVER',"ws://localhost:8182/ws")) as websocket:
        await websocket.send(os.getenv('MSG','TEST MESSAGE'))
        while True:
            response = await websocket.recv()
            print(response)
#           http POST on https://paas.upshift.redhat.com/oapi/v1/namespaces/nos-perf/buildconfigs/indy-perf/webhooks/fWXhF3kdYJQsbVZdvRqS/github
            token = open('/var/run/secrets/kubernetes.io/serviceaccount/token').read()
            data = json.loads(response)
            url = os.getenv('URL_TRIGGER','https://indy-perf:8080/oapi/v1/namespaces/nos-perf/buildconfigs/indy-perf/webhooks/fWXhF3kdYJQsbVZdvRqS/github')
            alowed = ["Accept" , "User-Agent" , "X-Github-Event" , "X-Github-Delivery" , "Content-Type" ]
            headers = {x:y for x,y in data["headers"].items() if x in alowed}
            headers['Authorization'] = "Bearer {}".format(token)
            payload = json.loads(data["payload"])
            resp = requests.post(
                url = url,
                data = payload,
                headers=headers
            )
            print(resp)

asyncio.get_event_loop().run_until_complete(start())