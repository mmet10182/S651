#!/usr/bin/env python
import io
import uuid
from urllib.request import urlopen, Request
from subprocess import Popen, PIPE
import socket


# Get ip address
hostname=socket.gethostname()
ip_addr=socket.gethostbyname(hostname)

# Get hwuuid
hwuuid = Popen(['esxcfg-info', '--hwuuid'], stdout=PIPE).communicate()[0]
hwuuid = hwuuid.decode('utf-8').strip()

host = 'http://10.7.240.156:443/raidmon/api/v1/hosts/{}/disks/report'.format(hwuuid)

def make_request(url, data, headers={}):
    req = Request(url, headers=headers, data=data)

    with urlopen(req) as resp:
        return resp.read()


def get_report_raid():
    try:
      shell_out = Popen(["/opt/lsi/storcli64/storcli64", "/c0 show"], stdout=PIPE).communicate()[0]
    except FileNotFoundError:
      shell_out = Popen(["/opt/pmc/arcconf", "getconfig", "1"], stdout=PIPE).communicate()[0]
    shell_out = str('{}\n{}'.format(ip_addr, shell_out.decode('utf-8'))).encode()
    return shell_out


def main() -> None:
    data = io.BytesIO()

    report_raid = get_report_raid()

    boundary = uuid.uuid4().hex

    data.write('--{}\r\n'.format(boundary).encode())
    data.write('Content-Disposition: form-data; name="{}"; filename="{}"\r\n'.format('shell_out', 'test.txt').encode())
    data.write('Content-Type: text/plain\r\n'.encode())
    data.write('\r\n'.encode())
    data.write(report_raid)
    data.write('\r\n'.encode())
    data.write('--{}--\r\n'.format(boundary).encode())

    response = make_request(host,
                            headers={"Content-Type": "multipart/form-data; boundary={}".format(boundary)},
                            data=data.getvalue(),
                            )


if __name__ == "__main__":
    main()