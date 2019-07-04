from kotano import proxy
from io import BytesIO

import time
import boto3
import json
import os

BUCKET = os.environ.get("DEFAULT_BUCKET")
OBJNAME = "redmoon.json"
LENGTH = 28


@proxy('api')
def set_anchor(request):
    params = request.params
    a = params.get("anchor")
    if a is None:
        return {
        'success': False,
        'message': 'Invalid request.  Need anchor'}

    data = {"anchor": a, "timestamp": time.time()}
    s = json.dumps(data)
    buf = BytesIO(s.encode())
    s3 = boto3.client('s3')
    try:
        s3.upload_fileobj(buf, BUCKET, OBJNAME)
    except Exception as e:
        return {'success': False,
                'message': 'Upload to S3 failed: ' + str(e)}
    return {'success': True, 'message': 'Success'}


@proxy('api')
def root(request):
    # Read config
    s3 = boto3.resource("s3")
    try:
        obj = s3.Object(BUCKET, OBJNAME)
        data = obj.get()["Body"].read()
        cfg = json.loads(data)
    except Exception as e:
        return {"success": False,
                "message": "Retrieval from S3 failed: " + str(e)}

    # Get anchor and timestamp
    _anchor = cfg["anchor"]
    _timestamp = cfg["timestamp"]
    anchor = int(_anchor)
    timestamp = float(_timestamp)

    # Compute number of days since timestamp
    now = time.time()
    since = int((now - timestamp)/(3600*24))

    # Return mod length
    return (since + anchor) % LENGTH
