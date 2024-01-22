# pi_planter

## Packages

```
git
python3-venv
python3-dev
```

## Installation

Install the above packages for Raspberry Pi OS,

```
sudo apt update && sudo apt install git python3-venv python3-dev -y
```

Clone the repo,
```
git clone git@github.com:hahnx117/pi_planter.git
```

`cd` into the repo and set up your Python venv,

```
cd pi_planter
python3 -m venv .
```

Once it's done, activate the virtual environment and install the requirements
```
. bin/activate
python3 -m pip install -r requirements.txt
```

After that run `python main.py`. If the logging starts, it's good to go.

## Add the `systemd` service

Make sure to update the `WorkingDirectory` and `ExecStart` variables in `pi_planter.service`. Then, from the repo directory,

```
sudo cp pi_planter.service /etc/systemd/system/pi_planter.service
sudo systemctl daemon-reload
sudo systemctl enable pi_planter.service
sudo systemctl start pi_planter.service
```

The logs will be viewable at `journalctl -u pi_planter.service | less -20`

The current status is viewable at `systemctl status pi_planter.service`