#ifndef EEZ_LVGL_UI_STYLES_H
#define EEZ_LVGL_UI_STYLES_H

#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

// Style: Button Style
lv_style_t *get_style_button_style_MAIN_SCROLLED();
lv_style_t *get_style_button_style_MAIN_DEFAULT();
void add_style_button_style(lv_obj_t *obj);
void remove_style_button_style(lv_obj_t *obj);

// Style: button_touch_inc_dec
lv_style_t *get_style_button_touch_inc_dec_MAIN_DEFAULT();
lv_style_t *get_style_button_touch_inc_dec_MAIN_SCROLLED();
void add_style_button_touch_inc_dec(lv_obj_t *obj);
void remove_style_button_touch_inc_dec(lv_obj_t *obj);

// Style: Text Main Colour
lv_style_t *get_style_text_main_colour_MAIN_DEFAULT();
lv_style_t *get_style_text_main_colour_MAIN_FOCUSED();
void add_style_text_main_colour(lv_obj_t *obj);
void remove_style_text_main_colour(lv_obj_t *obj);

// Style: button_push_opaque
lv_style_t *get_style_button_push_opaque_MAIN_DEFAULT();
void add_style_button_push_opaque(lv_obj_t *obj);
void remove_style_button_push_opaque(lv_obj_t *obj);

// Style: encoders_text
lv_style_t *get_style_encoders_text_MAIN_DEFAULT();
void add_style_encoders_text(lv_obj_t *obj);
void remove_style_encoders_text(lv_obj_t *obj);

// Style: text_standard_value
lv_style_t *get_style_text_standard_value_MAIN_DEFAULT();
void add_style_text_standard_value(lv_obj_t *obj);
void remove_style_text_standard_value(lv_obj_t *obj);

// Style: title_text_style
lv_style_t *get_style_title_text_style_MAIN_DEFAULT();
void add_style_title_text_style(lv_obj_t *obj);
void remove_style_title_text_style(lv_obj_t *obj);



#ifdef __cplusplus
}
#endif

#endif /*EEZ_LVGL_UI_STYLES_H*/