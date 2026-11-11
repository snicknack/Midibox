#include <string.h>

#include "screens.h"
#include "images.h"
#include "fonts.h"
#include "actions.h"
#include "vars.h"
#include "styles.h"
#include "ui.h"

#include <string.h>

objects_t objects;
lv_obj_t *tick_value_change_obj;

void create_screen_main() {
    void *flowState = getFlowState(0, 0);
    (void)flowState;
    lv_obj_t *obj = lv_obj_create(0);
    objects.main = obj;
    lv_obj_set_pos(obj, 0, 0);
    lv_obj_set_size(obj, 320, 240);
    {
        lv_obj_t *parent_obj = obj;
        {
            // container_chord
            lv_obj_t *obj = lv_obj_create(parent_obj);
            objects.container_chord = obj;
            lv_obj_set_pos(obj, 0, 0);
            lv_obj_set_size(obj, 160, 148);
            lv_obj_set_style_pad_left(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_top(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_right(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_bottom(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_add_flag(obj, LV_OBJ_FLAG_CHECKABLE);
            lv_obj_clear_flag(obj, LV_OBJ_FLAG_CLICKABLE|LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_SCROLL_CHAIN_HOR|LV_OBJ_FLAG_SCROLL_CHAIN_VER|LV_OBJ_FLAG_SCROLL_ELASTIC|LV_OBJ_FLAG_SCROLL_MOMENTUM);
            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
            {
                lv_obj_t *parent_obj = obj;
                {
                    // Key_text
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.key_text = obj;
                    lv_obj_set_pos(obj, 0, -60);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "KEY");
                }
                {
                    // button_key
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_key = obj;
                    lv_obj_set_pos(obj, 0, -40);
                    lv_obj_set_size(obj, 30, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_border_opa(obj, 255, LV_PART_MAIN | LV_STATE_SCROLLED);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_opa(obj, 255, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_opa(obj, 255, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            // button_text_key
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.button_text_key = obj;
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_opa(obj, 255, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xfffff800), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xfffff800), LV_PART_MAIN | LV_STATE_FOCUSED);
                            lv_label_set_text(obj, "C");
                        }
                    }
                }
                {
                    // pitch_text_chord
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.pitch_text_chord = obj;
                    lv_obj_set_pos(obj, 0, 0);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    add_style_text_main_colour(obj);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "Am");
                }
                {
                    // pitch_text_notes
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.pitch_text_notes = obj;
                    lv_obj_set_pos(obj, 0, 100);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_TOP_MID, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_letter_space(obj, 10, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "ACE");
                }
            }
        }
        {
            // container_encoders
            lv_obj_t *obj = lv_obj_create(parent_obj);
            objects.container_encoders = obj;
            lv_obj_set_pos(obj, 158, 1);
            lv_obj_set_size(obj, 160, 147);
            lv_obj_set_style_pad_left(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_top(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_right(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_bottom(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_clear_flag(obj, LV_OBJ_FLAG_SCROLLABLE);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            {
                lv_obj_t *parent_obj = obj;
                {
                    // encoder_text_arc_1
                    lv_obj_t *obj = lv_arc_create(parent_obj);
                    objects.encoder_text_arc_1 = obj;
                    lv_obj_set_pos(obj, -22, -5);
                    lv_obj_set_size(obj, 65, 61);
                    lv_arc_set_range(obj, 1, 127);
                    lv_arc_set_value(obj, 25);
                    lv_obj_add_flag(obj, LV_OBJ_FLAG_FLOATING|LV_OBJ_FLAG_IGNORE_LAYOUT|LV_OBJ_FLAG_SCROLL_ONE);
                    lv_obj_clear_flag(obj, LV_OBJ_FLAG_SCROLL_ELASTIC|LV_OBJ_FLAG_SCROLL_MOMENTUM);
                    lv_obj_set_scroll_snap_x(obj, LV_SCROLL_SNAP_START);
                    lv_obj_set_scroll_snap_y(obj, LV_SCROLL_SNAP_END);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_transform_zoom(obj, 128, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_width(obj, 10, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff40ffff), LV_PART_KNOB | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xff40ffff), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                }
                {
                    // encoder_text_arc_2
                    lv_obj_t *obj = lv_arc_create(parent_obj);
                    objects.encoder_text_arc_2 = obj;
                    lv_obj_set_pos(obj, 52, -5);
                    lv_obj_set_size(obj, 65, 61);
                    lv_arc_set_range(obj, 1, 127);
                    lv_arc_set_value(obj, 25);
                    lv_obj_add_flag(obj, LV_OBJ_FLAG_IGNORE_LAYOUT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_transform_zoom(obj, 128, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_width(obj, 10, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff40ffff), LV_PART_KNOB | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xff40ffff), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                }
                {
                    // encoder_text_arc_3
                    lv_obj_t *obj = lv_arc_create(parent_obj);
                    objects.encoder_text_arc_3 = obj;
                    lv_obj_set_pos(obj, -22, 65);
                    lv_obj_set_size(obj, 65, 61);
                    lv_arc_set_range(obj, 1, 127);
                    lv_arc_set_value(obj, 25);
                    lv_obj_add_flag(obj, LV_OBJ_FLAG_IGNORE_LAYOUT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_transform_zoom(obj, 128, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_width(obj, 10, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff40ffff), LV_PART_KNOB | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xff40ffff), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                }
                {
                    // encoder_text_arc_4
                    lv_obj_t *obj = lv_arc_create(parent_obj);
                    objects.encoder_text_arc_4 = obj;
                    lv_obj_set_pos(obj, 52, 65);
                    lv_obj_set_size(obj, 65, 61);
                    lv_arc_set_range(obj, 1, 127);
                    lv_arc_set_value(obj, 25);
                    lv_obj_add_flag(obj, LV_OBJ_FLAG_IGNORE_LAYOUT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_transform_zoom(obj, 128, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_width(obj, 10, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff40ffff), LV_PART_KNOB | LV_STATE_DEFAULT);
                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xff40ffff), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                }
                {
                    // encoder_text_value_1
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_value_1 = obj;
                    lv_obj_set_pos(obj, -40, -45);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_extrabold_18, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "20");
                }
                {
                    // encoder_text_value_2
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_value_2 = obj;
                    lv_obj_set_pos(obj, 35, -45);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_extrabold_18, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "40");
                }
                {
                    // encoder_text_value_4
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_value_4 = obj;
                    lv_obj_set_pos(obj, 35, 25);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_extrabold_18, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "58");
                }
                {
                    // encoder_text_value_3
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_value_3 = obj;
                    lv_obj_set_pos(obj, -40, 25);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_extrabold_18, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "50");
                }
                {
                    // encoder_text_type_1
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_type_1 = obj;
                    lv_obj_set_pos(obj, -40, -65);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "ATTACK");
                }
                {
                    // encoder_text_type_2
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_type_2 = obj;
                    lv_obj_set_pos(obj, 35, -65);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "RELEASE");
                }
                {
                    // encoder_text_type_3
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_type_3 = obj;
                    lv_obj_set_pos(obj, -40, 5);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "CUTTOFF");
                }
                {
                    // encoder_text_type_4
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.encoder_text_type_4 = obj;
                    lv_obj_set_pos(obj, 35, 5);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "RES");
                }
            }
        }
        {
            // container_pitch
            lv_obj_t *obj = lv_obj_create(parent_obj);
            objects.container_pitch = obj;
            lv_obj_set_pos(obj, 0, 148);
            lv_obj_set_size(obj, 320, 56);
            lv_obj_set_style_pad_left(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_top(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_right(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_pad_bottom(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_clear_flag(obj, LV_OBJ_FLAG_CLICKABLE|LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_SCROLL_CHAIN_HOR|LV_OBJ_FLAG_SCROLL_CHAIN_VER|LV_OBJ_FLAG_SCROLL_ELASTIC|LV_OBJ_FLAG_SCROLL_MOMENTUM|LV_OBJ_FLAG_SCROLL_WITH_ARROW);
            lv_obj_set_scrollbar_mode(obj, LV_SCROLLBAR_MODE_AUTO);
            lv_obj_set_scroll_dir(obj, LV_DIR_ALL);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_CHECKED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_DEFAULT);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_CHECKED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_PRESSED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_CHECKED | LV_STATE_PRESSED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_DISABLED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_FOCUSED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_FOCUS_KEY);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_EDITED);
            lv_obj_set_style_bg_opa(obj, 0, LV_PART_ANY | LV_STATE_SCROLLED);
            {
                lv_obj_t *parent_obj = obj;
                {
                    // text_title_key
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.text_title_key = obj;
                    lv_obj_set_pos(obj, -108, -20);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    add_style_midi_box_colour_scheme(obj);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_semi_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "KEY");
                }
                {
                    // text_title_transpose
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.text_title_transpose = obj;
                    lv_obj_set_pos(obj, -3, -20);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    add_style_main_text_style(obj);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "TRANSPOSE");
                }
                {
                    // text_title_octave
                    lv_obj_t *obj = lv_label_create(parent_obj);
                    objects.text_title_octave = obj;
                    lv_obj_set_pos(obj, 97, -20);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    add_style_midi_box_colour_scheme(obj);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &ui_font_montserrat_semi_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_label_set_text(obj, "OCTAVE");
                }
                {
                    // button_key_dec
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_key_dec = obj;
                    lv_obj_set_pos(obj, -130, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_SCROLLED);
                    lv_obj_set_style_text_opa(obj, 255, LV_PART_MAIN | LV_STATE_SCROLLED);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "-");
                        }
                    }
                }
                {
                    // button_key_inc
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_key_inc = obj;
                    lv_obj_set_pos(obj, -80, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "+");
                        }
                    }
                }
                {
                    // button_trans_dec
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_trans_dec = obj;
                    lv_obj_set_pos(obj, -28, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "-");
                        }
                    }
                }
                {
                    // button_trans_inc
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_trans_inc = obj;
                    lv_obj_set_pos(obj, 22, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "+");
                        }
                    }
                }
                {
                    // button_oct_dec
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_oct_dec = obj;
                    lv_obj_set_pos(obj, 77, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "-");
                        }
                    }
                }
                {
                    // button_oct_inc
                    lv_obj_t *obj = lv_btn_create(parent_obj);
                    objects.button_oct_inc = obj;
                    lv_obj_set_pos(obj, 127, 5);
                    lv_obj_set_size(obj, 40, 20);
                    add_style_button_style(obj);
                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_outline_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_radius(obj, 3, LV_PART_MAIN | LV_STATE_DEFAULT);
                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_text_main_colour(obj);
                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_font(obj, &ui_font_montserrat_extra_bold_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "+");
                        }
                    }
                }
            }
        }
        {
            // page_select
            lv_obj_t *obj = lv_btnmatrix_create(parent_obj);
            objects.page_select = obj;
            lv_obj_set_pos(obj, 0, 205);
            lv_obj_set_size(obj, 320, 35);
            static const char *map[6] = {
                "Main",
                "Scale",
                "Faders",
                "Encoders",
                "Utilities",
                NULL,
            };
            lv_btnmatrix_set_map(obj, map);
            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff282b30), LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_line_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_line_opa(obj, 255, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_border_opa(obj, 128, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_ITEMS | LV_STATE_DEFAULT);
            lv_obj_set_style_line_width(obj, 1, LV_PART_ITEMS | LV_STATE_DEFAULT);
            lv_obj_set_style_line_rounded(obj, true, LV_PART_ITEMS | LV_STATE_DEFAULT);
            lv_obj_set_style_line_color(obj, lv_color_hex(0xffa0fff9), LV_PART_ITEMS | LV_STATE_DEFAULT);
            lv_obj_set_style_text_color(obj, lv_color_hex(0xfffff800), LV_PART_ITEMS | LV_STATE_FOCUSED);
        }
        {
            lv_obj_t *obj = lv_line_create(parent_obj);
            objects.obj0 = obj;
            lv_obj_set_pos(obj, 0, 143);
            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
            static lv_point_t line_points[] = {
                { 0, 0 },
                { 320, 0 }
            };
            lv_line_set_points(obj, line_points, 2);
            lv_obj_set_style_line_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
        }
    }
    
    tick_screen_main();
}

void tick_screen_main() {
    void *flowState = getFlowState(0, 0);
    (void)flowState;
}


extern void add_style(lv_obj_t *obj, int32_t styleIndex);
extern void remove_style(lv_obj_t *obj, int32_t styleIndex);

static const char *screen_names[] = { "Main" };
static const char *object_names[] = { "main", "container_chord", "key_text", "button_key", "button_text_key", "pitch_text_chord", "pitch_text_notes", "container_encoders", "encoder_text_arc_1", "encoder_text_arc_2", "encoder_text_arc_3", "encoder_text_arc_4", "encoder_text_value_1", "encoder_text_value_2", "encoder_text_value_4", "encoder_text_value_3", "encoder_text_type_1", "encoder_text_type_2", "encoder_text_type_3", "encoder_text_type_4", "container_pitch", "text_title_key", "text_title_transpose", "text_title_octave", "button_key_dec", "button_key_inc", "button_trans_dec", "button_trans_inc", "button_oct_dec", "button_oct_inc", "page_select", "obj0" };
static const char *style_names[] = { "MIDI BOX COLOUR SCHEME", "main_text_style", "Button Style", "Text Main Colour" };


typedef void (*tick_screen_func_t)();
tick_screen_func_t tick_screen_funcs[] = {
    tick_screen_main,
};
void tick_screen(int screen_index) {
    tick_screen_funcs[screen_index]();
}
void tick_screen_by_id(enum ScreensEnum screenId) {
    tick_screen_funcs[screenId - 1]();
}

void create_screens() {
    eez_flow_init_styles(add_style, remove_style);
    
    eez_flow_init_screen_names(screen_names, sizeof(screen_names) / sizeof(const char *));
    eez_flow_init_object_names(object_names, sizeof(object_names) / sizeof(const char *));
    eez_flow_init_style_names(style_names, sizeof(style_names) / sizeof(const char *));
    
    lv_disp_t *dispp = lv_disp_get_default();
    lv_theme_t *theme = lv_theme_default_init(dispp, lv_palette_main(LV_PALETTE_BLUE), lv_palette_main(LV_PALETTE_RED), true, LV_FONT_DEFAULT);
    lv_disp_set_theme(dispp, theme);
    
    create_screen_main();
}
