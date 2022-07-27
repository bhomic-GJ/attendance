import os

import qrcode

from . import new_uuid

def generate_qr(string, path, filename = None):
    os.makedirs(path, exist_ok=True)
    c = qrcode.make(string)
    path = os.path.join(path, f"{filename or new_uuid()}.png")
    c.save(path)
    return path