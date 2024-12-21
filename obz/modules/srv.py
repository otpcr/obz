# This file is placed in the Public Domain.
# pylint: disable=C


"service file"


from ..persist import Config


TXT = """[Unit]
Description=%s
After=network-online.target

[Service]
Type=simple
User=%s
Group=%s
ExecStart=/home/%s/.local/bin/%ss

[Install]
WantedBy=multi-user.target"""



def srv(event):
    import getpass
    name = getpass.getuser()
    event.reply(TXT % (Config.name.upper(), name, name, name, Config.name))
