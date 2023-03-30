#!/bin/bash
docker run --restart on-failure:3 --name datadog_status_monitor -d  -v "$(pwd):/app" datadog_status_monitor python  datadog_status_int.py

