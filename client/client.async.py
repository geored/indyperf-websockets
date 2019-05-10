
import asyncio
import websockets
import os
import json
import logging
import time
import aiohttp
import ssl

# json build-config payload & http endpoint
# {"kind":"BuildRequest","apiVersion":"build.openshift.io/v1","metadata":{"name":"indy-perf","creationTimestamp":None},"triggeredBy":[{"message":"Manually triggered"}],"dockerStrategyOptions":{},"sourceStrategyOptions":{}}
# 'https://paas.upshift.redhat.com:443/apis/build.openshift.io/v1/namespaces/nos-perf/buildconfigs/indy-perf/instantiate'

# http endpoint for github webhooks
# https://paas.upshift.redhat.com/oapi/v1/namespaces/nos-perf/buildconfigs/indy-perf/webhooks/fWXhF3kdYJQsbVZdvRqS/github

async def start():
    token = open('/var/run/secrets/kubernetes.io/serviceaccount/token').read()
    cert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    build_url = os.getenv('URL_TRIGGER','https://paas.upshift.redhat.com/oapi/v1/namespaces/nos-perf/buildconfigs/indy-perf/webhooks/fWXhF3kdYJQsbVZdvRqS/github')
    ws_endpoint = os.getenv('WS_SERVER', "ws://ws-server-nos-perf.7e14.starter-us-west-2.openshiftapps.com/ws")
    alowed = ["Accept", "User-Agent", "X-Github-Event", "X-Github-Delivery", "Content-Type", "X-Hub-Signature"]

    sslcontext = ssl.create_default_context(cafile=cert)
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)


    async with websockets.connect(ws_endpoint) as websocket:
        logging.warning('Opened Connection to Server')
        await websocket.send(json.dumps({'msg':'TEST MESSAGE'}))
        async with aiohttp.ClientSession(connector=conn) as session:

            while True:
                response = await websocket.recv()
                logging.warning('-- Recived: {}'.format(response))
                data = json.loads(response)
                payload = json.loads(data["payload"])
                # adding metadata and triggeredBy keys just for testing starting build job
                payload["metadata"] = {
                    "name":"indy-perf"
                }
                payload["triggeredBy"] = {}
                # end of test added key values
                headers = {x:y for x,y in data["headers"].items() if x in alowed}
                headers['Authorization'] = "Bearer {}".format(token)
                headers['Accept'] = "application/json"
                if response is None: break
                else:
                    async with session.post(build_url, data=json.dumps(payload), headers=headers) as resp:
                        logging.warning(resp.status)
                        logging.warning(await resp.text())


asyncio.get_event_loop().run_until_complete(start())