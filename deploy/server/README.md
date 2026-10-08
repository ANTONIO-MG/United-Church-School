# Web service unit (Oracle Cloud box)

`ucs-lms.service` is the copy of record for the unit that serves the
site on port 80. The live file is `/etc/systemd/system/ucs-lms.service`
— this directory exists so a change to it survives a rebuild of the machine.

Install / update:

    sudo cp deploy/server/ucs-lms.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now ucs-lms

There is **no nginx**. gunicorn runs the ASGI app directly on `0.0.0.0:80` with
`CAP_NET_BIND_SERVICE`, and whitenoise serves `staticfiles/` from inside the app
process, so this unit plus postgresql and redis-server is the whole stack.

Check it:

    systemctl status ucs-lms
    sudo journalctl -u ucs-lms -f
    python3 run.py --check          # verifies postgres, redis, migrations, static

Two details in the unit are deliberate and easy to undo by accident:

* **`Wants=`, not `Requires=`**, on postgresql/redis-server. `Requires=` sounds
  stricter and is worse: `systemctl stop redis-server` propagates into stopping
  the site, and it does *not* come back when redis returns. Start ordering is
  already guaranteed by `After=`.
* **`Restart=always`**, so a worker that dies while redis is briefly away is
  retried until it can start again.
