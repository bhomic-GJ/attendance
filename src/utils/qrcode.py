import qrcode
from PIL import Image

def generate_qr(path,string):
    c = qrcode.make(string)
    c.save(path)
    return path