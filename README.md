# Smart Playground — Distributed Embedded Interaction System

Developed as part of the Smart Playground Initiative (Tufts CEEO).

## Overview
Three ESP-based nodes coordinate a physical interaction loop between an input object and an output object via a relay.

## Nodes
- Mailbox node: input + state changes
- Relay node: message routing/coordination
- Plushie node: output feedback

## Repo layout
- `mailESP1.py` — mailbox node firmware
- `middleManESP2.py` — relay node firmware
- `stuffyESP3.py` — plushie node firmware

## Notes
Identifiers and environment-specific values are removed or replaced with placeholders.
