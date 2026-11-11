# Midibox raspberry pi — ChatGPT project export

Pulled from the ChatGPT project "Midibox raspberry pi" on 2026-11-11 through the
Claude browser pane. Landing folder only; the working repo will be ~/MidiBox.

- `chats/`        41 conversations as markdown (01–39 project chats, newest first
                  as ChatGPT listed them; 40–41 are outside the project, reached
                  through the share links in ~/Desktop/Links). Code blocks are
                  kept as fenced code. Images appear as `[image file_…]` markers.
- `chats_json/`   The same conversations as raw ChatGPT JSON.
- `chat_index.tsv` Number, title and conversation id for chats 01–39.
- `files/sources/` The 23 files from the project's Sources tab (SquareLine/LVGL
                  ESP32 UI export, Pi-side Python for ADS1115 and SX1509, Build
                  Overview docx).
- `files_index.json` Metadata for those 23 files.
- `assets_index*.json` Every image/attachment reference in the chats (378 unique,
                  ~575 MB, mostly iPhone photos). Not downloaded by choice.
- `chatgpt_memory_midibox.md` The Midibox sections of ChatGPT's memory summary.
- `tools/chatgpt_receiver.py` Loopback receiver used for the transfer.

Not recoverable: the 10 files uploaded into chats (midibox_play_v2.py,
uart_sniffer_midi_v3/v9.py, Sigrok1.rtf, SL88 Studio 1.7.0.syx, plus four that
also exist in Sources). ChatGPT now answers "file not found" for them; their
content is largely reproduced as code blocks inside the chats.

Other local Midibox material already on this Mac:
- ~/Downloads/Midibox-main            GitHub snicknack/Midibox download (Pi Python app)
- ~/eez-projects/Midibox_GUI, Midi_Playground_1–3, midi_playground_v2/v3  EEZ Studio GUIs
- ~/Documents/midibox_dark_theme_v8_3_11, midibox_gui_font_pack_v8_3_11
- ~/Documents/Midibox Build overview.pages / .docx
