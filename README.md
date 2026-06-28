# Multi-Agent Transportation Modeling

**Live project:** [https://multi-agent-transportation-modeling.vercel.app](https://multi-agent-transportation-modeling.vercel.app)

An interactive traffic simulation developed as a master's project. The model
simulates cars with aggressive, standard, and cautious driving behaviours at a
four-way intersection with dynamically timed traffic lights.

## Features

- Eight incoming lanes at a four-way intersection
- Three driver behaviour profiles
- Traffic lights whose green times respond to traffic density
- Live counts for moving and waiting cars
- Traffic-density and flow monitoring
- Runs as a desktop app or in a modern web browser

## Run locally

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

Enter vehicle counts in the coloured boxes for one or more lanes, then select
**Start/Continue**. The colours represent aggressive (red), standard (green),
and cautious (blue) drivers.

## Build the browser version

The web build uses [pygbag](https://pygame-web.github.io/) to package Pygame as
WebAssembly.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pygbag --build .
```

The generated static site is written to `build/web`. To test it, serve that
folder through a local HTTP server rather than opening `index.html` directly.

## Deploy on Vercel

The included `vercel.json` installs the web build tooling, builds the static
site, and publishes `build/web`. Import this GitHub repository into Vercel and
deploy it with the repository settings; no environment variables are needed.

## Project structure

- `main.py` — application loop and user interaction
- `traffic_model.py` — simulation state, scheduling, and traffic-light timing
- `car_agent.py` — car agents, movement, and turning logic
- `behaviour.py` — driver behaviour profiles
- `traffic_light.py` — traffic-light states and rendering
- `intersection.py` — intersection rendering
- `monitor.py` — live metrics and chart
- `ui.py` — controls and vehicle-count inputs
