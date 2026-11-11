// PatchSYS page for the MidiBox screen (hand-written LVGL 8.3, not a SquareLine export).
//
// The Pi feeds it over the same serial link as the SquareLine pages:
//   ints   name:value\n   ps_arc1..4 0..127, ps_sc 0..100, ps_bank 0|1, ps_status 0|1|2,
//                         ps_mode_color 0|1, ps_show 0|1
//   text   name=text\n    ps_lbl1..4, ps_synth, ps_sound, ps_mode, ps_scval, ps_unit, ps_status_t
// and it answers with the usual {"get":"<name>","val":N} lines for arcs and buttons:
//   ps_arc1..4 (0..127), ps_gen, ps_vary, ps_undo, ps_bank, ps_mode, ps_back (val 1).

#ifndef UI_PATCHSYS_H
#define UI_PATCHSYS_H

#ifdef __cplusplus
extern "C" {
#endif

#include "lvgl.h"

extern lv_obj_t *ui_PatchSys;

void ui_patchsys_screen_init(void);
void ui_patchsys_show(int show);                              // 1 = this page, 0 = back to the MIDI page
int  ui_patchsys_set_int(const char *name, int value);         // 1 if the name was one of ours
int  ui_patchsys_set_text(const char *name, const char *text); // 1 if the name was one of ours

#ifdef __cplusplus
}
#endif

#endif
