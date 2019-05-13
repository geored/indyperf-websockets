
import asyncio
import websockets
import os
import json
import logging
import aiohttp
import ssl

# json build-config payload & http endpoint
# {"kind":"BuildRequest","apiVersion":"build.openshift.io/v1","metadata":{"name":"indy-perf","creationTimestamp":None},"triggeredBy":[{"message":"Manually triggered"}],"dockerStrategyOptions":{},"sourceStrategyOptions":{}}
# 'https://paas.upshift.redhat.com:443/apis/build.openshift.io/v1/namespaces/nos-perf/buildconfigs/indy-perf/instantiate'

# http endpoint for github webhooks
# https://paas.upshift.redhat.com/oapi/v1/namespaces/nos-perf/buildconfigs/indy-perf/webhooks/fWXhF3kdYJQsbVZdvRqS/github
# ws://ws-server-nos-perf.7e14.starter-us-west-2.openshiftapps.com/ws

async def start():
    # Default Service Account Token
    token = open('/var/run/secrets/kubernetes.io/serviceaccount/token').read()
    # Certification file for SSL
    cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    # Provided URL for triggering build proccess or starting pipeline
    build_url = os.getenv('URL_TRIGGER','')
    # WebSockets Endpoint URL provided
    ws_endpoint = os.getenv('WS_SERVER', "")
    # List of Allowed Headers from Github webhooks POST request
    alowed = ["Accept", "User-Agent", "X-Github-Event", "X-Github-Delivery", "Content-Type", "X-Hub-Signature"]
    # Creating Default SSL Context
    sslcontext = ssl.create_default_context(cafile=cert)
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)

    # Opening WebSocket Connection to WebSocket server
    async with websockets.connect(ws_endpoint) as websocket:
        logging.warning('Opened Connection to Server')
        # sending websocket message to server
        await websocket.send(json.dumps({'msg':'TEST MESSAGE'}))
        # Creating Client Session with provided SSL configuration
        async with aiohttp.ClientSession(connector=conn) as session:

            while True:
                # Listening for recived messages from websocket server
                response = await websocket.recv()
                logging.warning('-- Recived: {}'.format(response))
                data = json.loads(response)
                payload = {}
                payload["payload"] = json.loads(data["payload"])

                # adding metadata and triggeredBy keys just for testing starting build job
                payload["metadata"] = {
                    "name":"indy-perf"
                }
                payload["triggeredBy"] = {}
                # end of test added key values

                headers = {x:y for x,y in data["headers"].items() if x in alowed}
                # Authorization header with token
                headers['Authorization'] = "Bearer {}".format(token)
                # Connection from websocket server is closed so terminate this iterations
                if response is None: break
                else:
                    # If there is websocket message from server then send HTTP POST request
                    # to generated HTTP URL for triggering build proccess
                    async with session.post(build_url, data=json.dumps(payload), headers=headers) as resp:
                        logging.warning(resp.status)
                        logging.warning(await resp.text())

# Start Non-Blocking thread for Asynchronous Handling of Long Lived Connections
asyncio.get_event_loop().run_until_complete(start())