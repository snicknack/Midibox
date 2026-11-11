#ifndef EEZ_LVGL_UI_SCREENS_H
#define EEZ_LVGL_UI_SCREENS_H

#include <lvgl.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct _objects_t {
    lv_obj_t *main;
    lv_obj_t *splash;
    lv_obj_t *tab_view_pages;
    lv_obj_t *tab_main;
    lv_obj_t *container_chord;
    lv_obj_t *key_text;
    lv_obj_t *button_key;
    lv_obj_t *button_text_key;
    lv_obj_t *pitch_text_chord;
    lv_obj_t *pitch_text_notes;
    lv_obj_t *container_encoders;
    lv_obj_t *encoder_text_arc_1;
    lv_obj_t *encoder_text_arc_2;
    lv_obj_t *encoder_text_arc_3;
    lv_obj_t *encoder_text_arc_4;
    lv_obj_t *encoder_text_value_1;
    lv_obj_t *encoder_text_value_2;
    lv_obj_t *encoder_text_value_4;
    lv_obj_t *encoder_text_value_3;
    lv_obj_t *encoder_text_type_1;
    lv_obj_t *encoder_text_type_2;
    lv_obj_t *encoder_text_type_3;
    lv_obj_t *encoder_text_type_4;
    lv_obj_t *container_pitch;
    lv_obj_t *text_title_key;
    lv_obj_t *text_title_transpose;
    lv_obj_t *text_title_octave;
    lv_obj_t *button_key_dec;
    lv_obj_t *obj0;
    lv_obj_t *button_key_inc;
    lv_obj_t *obj1;
    lv_obj_t *button_trans_dec;
    lv_obj_t *obj2;
    lv_obj_t *button_trans_inc;
    lv_obj_t *obj3;
    lv_obj_t *button_oct_dec;
    lv_obj_t *obj4;
    lv_obj_t *button_oct_inc;
    lv_obj_t *obj5;
    lv_obj_t *obj6;
    lv_obj_t *tab_scales_arp;
    lv_obj_t *obj7;
    lv_obj_t *obj8;
    lv_obj_t *obj9;
    lv_obj_t *obj10;
    lv_obj_t *obj11;
    lv_obj_t *button_fader_animate;
    lv_obj_t *button_fader_animate_text;
    lv_obj_t *button_fader_gravity_1;
    lv_obj_t *button_fader_animate_text_1;
    lv_obj_t *button_fader_gravity_2;
    lv_obj_t *button_fader_animate_text_2;
    lv_obj_t *button_fader_animate_1;
    lv_obj_t *button_fader_animate_text_3;
    lv_obj_t *text_fader_assign_mode;
    lv_obj_t *obj12;
    lv_obj_t *text_fader_2;
    lv_obj_t *text_fader_1_cc;
    lv_obj_t *text_fader_2_cc;
    lv_obj_t *text_fader_1;
    lv_obj_t *bar_fader_text_1;
    lv_obj_t *bar_fader_text_2;
    lv_obj_t *bar_fader_1;
    lv_obj_t *bar_fader_2;
    lv_obj_t *tab_super_encoders;
    lv_obj_t *obj13;
    lv_obj_t *text_encoder_1;
    lv_obj_t *text_encoder_2;
    lv_obj_t *text_encoder_3;
    lv_obj_t *text_encoder_4;
    lv_obj_t *arc_encoder_1;
    lv_obj_t *arc_encoder_2;
    lv_obj_t *arc_encoder_3;
    lv_obj_t *arc_encoder_4;
    lv_obj_t *text_encoder_value_1;
    lv_obj_t *text_encoder_value_2;
    lv_obj_t *text_encoder_value_3;
    lv_obj_t *text_encoder_value_4;
    lv_obj_t *animation_splash_timer;
    lv_obj_t *animation_splash;
} objects_t;

extern objects_t objects;

enum ScreensEnum {
    SCREEN_ID_MAIN = 1,
    SCREEN_ID_SPLASH = 2,
};

void create_screen_main();
void tick_screen_main();

void create_screen_splash();
void tick_screen_splash();

void tick_screen_by_id(enum ScreensEnum screenId);
void tick_screen(int screen_index);

void create_screens();


#ifdef __cplusplus
}
#endif

#endif /*EEZ_LVGL_UI_SCREENS_H*/