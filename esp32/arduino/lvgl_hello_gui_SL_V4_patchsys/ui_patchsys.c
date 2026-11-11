// PatchSYS page for the MidiBox screen. See ui_patchsys.h for the serial contract.
//
// 320 x 240 landscape. Holson palette: black ground, cyan for live values, ice white for
// text, amber for the DEPTH mode and warnings, muted teal for labels.
//
//   PATCHSYS            SERUM 2                   ● ONLINE
//   SOUND  Deep rolling reese
//   [A]  (arc) (arc) (arc) (arc)        values inside, names below
//   SUPERCORE  (arc 120) TEMPO BPM      [GEN ] [VARY] [UNDO]
//                                       [BANK] [MODE] [MIDI]

#include "ui.h"
#include "ui_patchsys.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>

extern void sendWidgetValue(const char *name, int val);

lv_obj_t *ui_PatchSys = NULL;

static lv_obj_t *s_synth, *s_dot, *s_status, *s_sound;
static lv_obj_t *s_bank_lbl;
static lv_obj_t *s_arc[4], *s_val[4], *s_lbl[4];
static lv_obj_t *s_sc_arc, *s_sc_val, *s_sc_mode, *s_sc_unit;
static lv_obj_t *s_btn[6];
static int s_suppress = 0;

static const char *BTN_NAME[6] = {"ps_gen", "ps_vary", "ps_undo", "ps_bank", "ps_mode", "ps_back"};
static const char *BTN_TEXT[6] = {"GEN", "VARY", "UNDO", "BANK", "MODE", "MIDI"};

#define C_BG     lv_color_hex(0x000000)
#define C_PANEL  lv_color_hex(0x0E1B1F)
#define C_TRACK  lv_color_hex(0x16262A)
#define C_CYAN   lv_color_hex(0x59F0E0)
#define C_ICE    lv_color_hex(0xF5FDFB)
#define C_MUTED  lv_color_hex(0x8FBDB6)
#define C_AMBER  lv_color_hex(0xFFC45A)
#define C_RED    lv_color_hex(0xFF4C4C)
#define C_GREEN  lv_color_hex(0x3DDC84)

static lv_obj_t *make_label(lv_obj_t *parent, const char *text, const lv_font_t *font, lv_color_t color,
                            int x, int y, int w, lv_text_align_t align)
{
    lv_obj_t *l = lv_label_create(parent);
    lv_label_set_text(l, text);
    lv_obj_set_style_text_font(l, font, 0);
    lv_obj_set_style_text_color(l, color, 0);
    lv_obj_set_pos(l, x, y);
    if (w > 0) {
        lv_obj_set_width(l, w);
        lv_label_set_long_mode(l, LV_LABEL_LONG_DOT);
    }
    lv_obj_set_style_text_align(l, align, 0);
    return l;
}

static void arc_event(lv_event_t *e)
{
    if (lv_event_get_code(e) != LV_EVENT_VALUE_CHANGED || s_suppress) return;
    int i = (int)(intptr_t)lv_event_get_user_data(e);
    int v = (int)lv_arc_get_value(s_arc[i]);
    lv_label_set_text_fmt(s_val[i], "%d", v);
    char name[12];
    snprintf(name, sizeof name, "ps_arc%d", i + 1);
    sendWidgetValue(name, v);
}

static void btn_event(lv_event_t *e)
{
    if (lv_event_get_code(e) != LV_EVENT_CLICKED) return;
    int i = (int)(intptr_t)lv_event_get_user_data(e);
    if (i == 6) { ui_patchsys_show(1); sendWidgetValue("ps_open", 1); return; }   // PS on the MIDI page
    if (i == 5) ui_patchsys_show(0);
    sendWidgetValue(BTN_NAME[i], 1);
}

static lv_obj_t *make_arc(lv_obj_t *parent, int x, int y, int size, int lo, int hi, int value, lv_color_t color)
{
    lv_obj_t *a = lv_arc_create(parent);
    lv_obj_set_size(a, size, size);
    lv_obj_set_pos(a, x, y);
    lv_arc_set_rotation(a, 135);
    lv_arc_set_bg_angles(a, 0, 270);
    lv_arc_set_range(a, lo, hi);
    lv_arc_set_value(a, value);
    lv_obj_set_style_arc_width(a, 6, LV_PART_MAIN);
    lv_obj_set_style_arc_color(a, C_TRACK, LV_PART_MAIN);
    lv_obj_set_style_arc_width(a, 6, LV_PART_INDICATOR);
    lv_obj_set_style_arc_color(a, color, LV_PART_INDICATOR);
    lv_obj_set_style_arc_rounded(a, true, LV_PART_INDICATOR);
    lv_obj_remove_style(a, NULL, LV_PART_KNOB);   // no knob: the value sits in the middle
    lv_obj_set_style_bg_opa(a, LV_OPA_TRANSP, 0);
    lv_obj_clear_flag(a, LV_OBJ_FLAG_SCROLLABLE);
    return a;
}

static void style_button(lv_obj_t *b)
{
    lv_obj_set_style_bg_color(b, C_PANEL, 0);
    lv_obj_set_style_bg_opa(b, LV_OPA_COVER, 0);
    lv_obj_set_style_border_color(b, C_MUTED, 0);
    lv_obj_set_style_border_width(b, 1, 0);
    lv_obj_set_style_radius(b, 6, 0);
    lv_obj_set_style_shadow_width(b, 0, 0);
    lv_obj_set_style_bg_color(b, C_CYAN, LV_STATE_PRESSED);
    lv_obj_set_style_border_color(b, C_CYAN, LV_STATE_PRESSED);
    lv_obj_set_style_text_color(b, C_BG, LV_STATE_PRESSED);
    lv_obj_set_style_text_color(b, C_ICE, 0);
    lv_obj_set_style_text_font(b, &lv_font_montserrat_12, 0);
}

void ui_patchsys_screen_init(void)
{
    if (ui_PatchSys) return;
    ui_PatchSys = lv_obj_create(NULL);
    lv_obj_set_style_bg_color(ui_PatchSys, C_BG, 0);
    lv_obj_set_style_bg_opa(ui_PatchSys, LV_OPA_COVER, 0);
    lv_obj_clear_flag(ui_PatchSys, LV_OBJ_FLAG_SCROLLABLE);

    // header: PATCHSYS, the target, the link's status
    make_label(ui_PatchSys, "PATCHSYS", &lv_font_montserrat_14, C_CYAN, 6, 4, 0, LV_TEXT_ALIGN_LEFT);
    s_synth = make_label(ui_PatchSys, "", &lv_font_montserrat_14, C_ICE, 90, 4, 140, LV_TEXT_ALIGN_CENTER);
    s_dot = lv_obj_create(ui_PatchSys);
    lv_obj_set_size(s_dot, 8, 8);
    lv_obj_set_pos(s_dot, 246, 9);
    lv_obj_set_style_radius(s_dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_border_width(s_dot, 0, 0);
    lv_obj_set_style_bg_color(s_dot, C_RED, 0);
    lv_obj_clear_flag(s_dot, LV_OBJ_FLAG_SCROLLABLE | LV_OBJ_FLAG_CLICKABLE);
    s_status = make_label(ui_PatchSys, "OFFLINE", &lv_font_montserrat_12, C_MUTED, 258, 5, 60, LV_TEXT_ALIGN_LEFT);

    // the sound on the target
    make_label(ui_PatchSys, "SOUND", &lv_font_montserrat_10, C_MUTED, 6, 29, 0, LV_TEXT_ALIGN_LEFT);
    s_sound = make_label(ui_PatchSys, "", &lv_font_montserrat_16, C_ICE, 50, 24, 264, LV_TEXT_ALIGN_LEFT);

    // bank badge, a button so a finger can swap banks too
    lv_obj_t *bank = lv_btn_create(ui_PatchSys);
    lv_obj_set_size(bank, 24, 64);
    lv_obj_set_pos(bank, 4, 56);
    style_button(bank);
    lv_obj_add_event_cb(bank, btn_event, LV_EVENT_CLICKED, (void *)(intptr_t)3);
    s_bank_lbl = lv_label_create(bank);
    lv_label_set_text(s_bank_lbl, "A");
    lv_obj_set_style_text_font(s_bank_lbl, &lv_font_montserrat_22, 0);
    lv_obj_set_style_text_color(s_bank_lbl, C_CYAN, 0);
    lv_obj_center(s_bank_lbl);
    make_label(ui_PatchSys, "BANK", &lv_font_montserrat_10, C_MUTED, 2, 122, 28, LV_TEXT_ALIGN_CENTER);

    // the four controls: value inside the arc, PatchSYS's own name under it
    for (int i = 0; i < 4; i++) {
        int x = 34 + 70 * i;
        s_arc[i] = make_arc(ui_PatchSys, x, 50, 64, 0, 127, 64, C_CYAN);
        lv_obj_add_event_cb(s_arc[i], arc_event, LV_EVENT_VALUE_CHANGED, (void *)(intptr_t)i);
        s_val[i] = lv_label_create(s_arc[i]);
        lv_label_set_text(s_val[i], "64");
        lv_obj_set_style_text_font(s_val[i], &lv_font_montserrat_18, 0);
        lv_obj_set_style_text_color(s_val[i], C_ICE, 0);
        lv_obj_center(s_val[i]);
        s_lbl[i] = make_label(ui_PatchSys, "", &lv_font_montserrat_12, C_MUTED, x - 4, 116, 72, LV_TEXT_ALIGN_CENTER);
    }

    // SuperCore: its arc, the value, the mode and unit
    make_label(ui_PatchSys, "SUPERCORE", &lv_font_montserrat_10, C_MUTED, 6, 140, 0, LV_TEXT_ALIGN_LEFT);
    s_sc_arc = make_arc(ui_PatchSys, 6, 154, 72, 0, 100, 55, C_CYAN);
    lv_obj_clear_flag(s_sc_arc, LV_OBJ_FLAG_CLICKABLE);   // the physical encoder owns it
    s_sc_val = lv_label_create(s_sc_arc);
    lv_label_set_text(s_sc_val, "120");
    lv_obj_set_style_text_font(s_sc_val, &lv_font_montserrat_20, 0);
    lv_obj_set_style_text_color(s_sc_val, C_ICE, 0);
    lv_obj_center(s_sc_val);
    s_sc_mode = make_label(ui_PatchSys, "TEMPO", &lv_font_montserrat_16, C_CYAN, 84, 166, 64, LV_TEXT_ALIGN_LEFT);
    s_sc_unit = make_label(ui_PatchSys, "BPM", &lv_font_montserrat_12, C_MUTED, 84, 188, 64, LV_TEXT_ALIGN_LEFT);

    // buttons: what the box can ask PatchSYS to do, and the page's own controls
    for (int i = 0; i < 6; i++) {
        int col = i % 3, row = i / 3;
        s_btn[i] = lv_btn_create(ui_PatchSys);
        lv_obj_set_size(s_btn[i], 50, 32);
        lv_obj_set_pos(s_btn[i], 156 + 54 * col, 150 + 40 * row);
        style_button(s_btn[i]);
        lv_obj_add_event_cb(s_btn[i], btn_event, LV_EVENT_CLICKED, (void *)(intptr_t)i);
        lv_obj_t *l = lv_label_create(s_btn[i]);
        lv_label_set_text(l, BTN_TEXT[i]);
        lv_obj_center(l);
    }
    ui_patchsys_set_int("ps_status", 0);

    // a way back from the MIDI page: a small PS button in its top-right corner
    if (ui_MainPage) {
        lv_obj_t *ps = lv_btn_create(ui_MainPage);
        lv_obj_set_size(ps, 30, 18);
        lv_obj_set_pos(ps, 288, 2);
        style_button(ps);
        lv_obj_set_style_text_font(ps, &lv_font_montserrat_10, 0);
        lv_obj_set_style_text_color(ps, C_CYAN, 0);
        lv_obj_add_event_cb(ps, btn_event, LV_EVENT_CLICKED, (void *)(intptr_t)6);
        lv_obj_t *l = lv_label_create(ps);
        lv_label_set_text(l, "PS");
        lv_obj_center(l);
    }
}

void ui_patchsys_show(int show)
{
    if (show) {
        if (ui_PatchSys) lv_disp_load_scr(ui_PatchSys);
    } else if (ui_MainPage) {
        lv_disp_load_scr(ui_MainPage);
    }
}

static int clamp(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }

int ui_patchsys_set_int(const char *name, int value)
{
    if (!ui_PatchSys || !name) return 0;
    if (!strncmp(name, "ps_arc", 6) && name[6] >= '1' && name[6] <= '4' && name[7] == 0) {
        int i = name[6] - '1';
        s_suppress = 1;
        lv_arc_set_value(s_arc[i], clamp(value, 0, 127));
        lv_label_set_text_fmt(s_val[i], "%d", clamp(value, 0, 127));
        s_suppress = 0;
        return 1;
    }
    if (!strcmp(name, "ps_sc")) { lv_arc_set_value(s_sc_arc, clamp(value, 0, 100)); return 1; }
    if (!strcmp(name, "ps_bank")) { lv_label_set_text(s_bank_lbl, value ? "B" : "A"); return 1; }
    if (!strcmp(name, "ps_mode_color")) {
        lv_color_t c = value ? C_AMBER : C_CYAN;
        lv_obj_set_style_arc_color(s_sc_arc, c, LV_PART_INDICATOR);
        lv_obj_set_style_text_color(s_sc_mode, c, 0);
        return 1;
    }
    if (!strcmp(name, "ps_status")) {
        lv_color_t dot = value == 1 ? C_GREEN : (value == 2 ? C_AMBER : C_RED);
        lv_obj_set_style_bg_color(s_dot, dot, 0);
        lv_obj_set_style_text_color(s_status, value == 1 ? C_ICE : C_MUTED, 0);
        if (value == 0) lv_label_set_text(s_status, "OFFLINE");
        else if (value == 2) lv_label_set_text(s_status, "BUSY");
        else lv_label_set_text(s_status, "ONLINE");
        lv_opa_t opa = value == 1 ? LV_OPA_COVER : LV_OPA_50;
        for (int i = 0; i < 4; i++) lv_obj_set_style_opa(s_arc[i], opa, 0);
        return 1;
    }
    if (!strcmp(name, "ps_show")) { ui_patchsys_show(value); return 1; }
    return 0;
}

int ui_patchsys_set_text(const char *name, const char *text)
{
    if (!ui_PatchSys || !name || !text) return 0;
    if (!strncmp(name, "ps_lbl", 6) && name[6] >= '1' && name[6] <= '4' && name[7] == 0) {
        lv_label_set_text(s_lbl[name[6] - '1'], text);
        return 1;
    }
    if (!strcmp(name, "ps_synth")) { lv_label_set_text(s_synth, text); return 1; }
    if (!strcmp(name, "ps_sound")) { lv_label_set_text(s_sound, text); return 1; }
    if (!strcmp(name, "ps_mode")) { lv_label_set_text(s_sc_mode, text); return 1; }
    if (!strcmp(name, "ps_scval")) { lv_label_set_text(s_sc_val, text); return 1; }
    if (!strcmp(name, "ps_unit")) { lv_label_set_text(s_sc_unit, text); return 1; }
    if (!strcmp(name, "ps_status_t")) { lv_label_set_text(s_status, text); return 1; }
    return 0;
}
