#!/usr/bin/env python3
"""A stand-in PatchSYS Link server for bench tests, built from PatchSYS's own server class.

It answers exactly as PatchSYS Development's Link does (same module), but instead of a
view model it prints every command and action it receives, confirms each parameter value
back after a short delay, and pushes a state with a tempo. Run it on the Mac with the
PatchSYS venv while PatchSYS itself is closed (they share port 39276):

    cd ~/PatchSYS && PYTHONPATH=src .venv/bin/python ~/MidiBox/tools/link_standin.py

Then start the MidiBox service on the Pi. Ctrl-C stops it.
"""

import argparse
import logging
import threading
import time

from patchsys.remote_link import ALL_PARAMETER_IDS, RemoteLinkContext, RemoteLinkServer

LOGGER = logging.getLogger("standin")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=39276)
    parser.add_argument("--seconds", type=float, default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    state = {"tempo": 120, "depth": 33, "commands": 0, "actions": 0}
    server = None

    def command_sink(command):
        state["commands"] += 1
        LOGGER.info("SET %-16s = %.3f  (seq %d)", command.parameter_id, command.normalized_value, command.sequence)
        def confirm():
            time.sleep(0.05)
            server.set_values({command.parameter_id: command.normalized_value})
        threading.Thread(target=confirm, daemon=True).start()
        return True

    def action_sink(action):
        state["actions"] += 1
        LOGGER.info("ACTION %-12s %s", action.name, action.payload)
        if action.name == "tempo" and isinstance(action.payload.get("bpm"), (int, float)):
            state["tempo"] = int(action.payload["bpm"])
            server.set_state({"tempo": state["tempo"]})
        elif action.name == "set_depth" and isinstance(action.payload.get("depth"), (int, float)):
            state["depth"] = int(action.payload["depth"])
            server.set_state({"depth": state["depth"]})
        return True

    server = RemoteLinkServer(command_sink, action_sink, host="0.0.0.0", port=args.port)
    server.start()
    server.update_context(RemoteLinkContext(
        online=True, session_id="standin-1", generation=1, synth_id="standin",
        synth_name="Stand-in target", available_parameter_ids=ALL_PARAMETER_IDS, status="ONLINE",
    ))
    server.set_values({pid: 0.5 for pid in ALL_PARAMETER_IDS})
    server.set_state({"tempo": state["tempo"], "depth": state["depth"], "sound": "stand-in"})
    LOGGER.info("stand-in Link listening on port %d (online, eight parameters at 0.5)", server.port)
    deadline = None if args.seconds is None else time.monotonic() + args.seconds
    try:
        while deadline is None or time.monotonic() < deadline:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        LOGGER.info("received %d parameter commands and %d actions; clients %d",
                    state["commands"], state["actions"], server.client_count)
        server.close()


if __name__ == "__main__":
    main()
