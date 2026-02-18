# Smart Playground — Distributed Embedded Interaction System

Developed as part of the Smart Playground Initiative at the Tufts Center for Engineering Education and Outreach (CEEO).

## Overview
A three-node ESP32-based system enab leing coordinated physical-digital interaction loop between embedded devices via input object and an output object via a relay. The architecture separates input generation, message mediation, and output feedback across independent microcontroller nodes.

## Nodes
- Mailbox node: Generates interaction events and manages local state transitions.
- Relay node: Handles message routing, coordination logic, and state synchronization.
- Plushie node: Receives routed events and produces LED-based feedback responses.

## Repository Structure
- `mailESP1.py` — Mailbox node firmware (authored by Infania Pimentel)
- `middleManESP2.py` — Relay node firmware (authored by Infania Pimentel)
- `stuffyESP3.py` — Plushie node firmware (authored by Infania Pimentel)
- `ledTasks.py` — LED state/task management module (authored by Infania Pimentel)
- `ssp_networking.py` — networking module from CEEO lab framework
- `networking.py` — networking module from CEEO lab framework


## Notes
Identifiers and environment-specific values are removed or replaced with placeholders.
Some networking modules originated from the CEEO lab framework and are included here for system completeness.

