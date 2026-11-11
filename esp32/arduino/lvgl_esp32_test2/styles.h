#ifndef EEZ_LVGL_UI_STYLES_H
#define EEZ_LVGL_UI_STYLES_H

#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

// Style: MIDI BOX COLOUR SCHEME
lv_style_t *get_style_midi_box_colour_scheme_MAIN_DEFAULT();
lv_style_t *get_style_midi_box_colour_scheme_MAIN_CHECKED();
void add_style_midi_box_colour_scheme(lv_obj_t *obj);
void remove_style_midi_box_colour_scheme(lv_obj_t *obj);

// Style: main_text_style
lv_style_t *get_style_main_text_style_MAIN_DEFAULT();
lv_style_t *get_style_main_text_style_MAIN_CHECKED();
void add_style_main_text_style(lv_obj_t *obj);
void remove_style_main_text_style(lv_obj_t *obj);

// Style: Button Style
lv_style_t *get_style_button_style_MAIN_DEFAULT();
void add_style_button_style(lv_obj_t *obj);
void remove_style_button_style(lv_obj_t *obj);

// Style: Text Main Colour
lv_style_t *get_style_text_main_colour_MAIN_DEFAULT();
void add_style_text_main_colour(lv_obj_t *obj);
void remove_style_text_main_colour(lv_obj_t *obj);



#ifdef __cplusplus
}
#endif

#endif /*EEZ_LVGL_UI_STYLES_H*/