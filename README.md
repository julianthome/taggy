# taggy

taggy is a simple micro-service for tagging files within your
[Nextcloud](https://Nextcloud.com/) repository. 

Nextcloud provides a scriptable DAV interface for managing files within your
Nextcloud storage. However, Nextcloud does not provide a scriptable 
interface for automated (remote) file tagging yet.

In order to tag uploaded files automatically, you can run the taggy
microservice on your Nextcloud server. taggy provides a simple JSON REST
API for tagging your files automatically. The following payload will give
you an idea what information is required by taggy:

```json
{ 
    "user": "<user>", 
    "pw": "<pw>", 
    "file": "files/<file>", 
    "tags": [ <tag0>,...,<tagN> ]
}
```

The script `taggy_client.sh` illustrates how the taggy microservice
(`taggy.py`) can be invoked remotely. The file `taggy_client.cfg` contains the
configuration for the taggy client whereas the file `taggy.json` contains the
configuration for the taggy service which is supposed to run on the
Nextcloud server.

# Limitations

Currently, the communication between taggy client and server is not encrypted 
so that the credentials are transmitted as plain text which can be dangerous 
depending on your setup. It is recommended to enable HTTPS for your Nextcloud
installation. SSL support for taggy will be added soon.

# Licence
The MIT License (MIT)

Copyright (c) 2017 Julian Thome <julian.thome.de@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
