#!/usr/bin/env bash

poetry run download-garmin-activities
poetry run merge-activities
poetry run calculate-total
