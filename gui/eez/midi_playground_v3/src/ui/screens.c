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
uint32_t active_theme_index = 0;

static void event_handler_cb_main_encoder_text_arc_1(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_1_val(value);
        }
    }
}

static void event_handler_cb_main_encoder_text_arc_2(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_2_val(value);
        }
    }
}

static void event_handler_cb_main_encoder_text_arc_3(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_3_val(value);
        }
    }
}

static void event_handler_cb_main_encoder_text_arc_4(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_4_val(value);
        }
    }
}

static void event_handler_cb_main_arc_encoder_1(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_1_val(value);
        }
    }
}

static void event_handler_cb_main_arc_encoder_2(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_2_val(value);
        }
    }
}

static void event_handler_cb_main_arc_encoder_3(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_3_val(value);
        }
    }
}

static void event_handler_cb_main_arc_encoder_4(lv_event_t *e) {
    lv_event_code_t event = lv_event_get_code(e);
    if (event == LV_EVENT_VALUE_CHANGED) {
        lv_obj_t *ta = lv_event_get_target(e);
        if (tick_value_change_obj != ta) {
            int32_t value = lv_arc_get_value(ta);
            set_var_encoder_4_val(value);
        }
    }
}

void create_screen_main() {
    lv_obj_t *obj = lv_obj_create(0);
    objects.main = obj;
    lv_obj_set_pos(obj, 0, 0);
    lv_obj_set_size(obj, 320, 240);
    lv_obj_add_flag(obj, LV_OBJ_FLAG_SCROLL_ONE);
    lv_obj_set_scrollbar_mode(obj, LV_SCROLLBAR_MODE_AUTO);
    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
    {
        lv_obj_t *parent_obj = obj;
        {
            // tab_view_pages
            lv_obj_t *obj = lv_tabview_create(parent_obj, LV_DIR_BOTTOM, 30);
            objects.tab_view_pages = obj;
            lv_obj_set_pos(obj, 2, 2);
            lv_obj_set_size(obj, 316, 236);
            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
            {
                lv_obj_t *parent_obj = obj;
                {
                    // tab_main
                    lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "Main");
                    objects.tab_main = obj;
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            // container_chord
                            lv_obj_t *obj = lv_obj_create(parent_obj);
                            objects.container_chord = obj;
                            lv_obj_set_pos(obj, -11, -11);
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
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xff00e0ff), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    {
                                        lv_obj_t *parent_obj = obj;
                                        {
                                            // button_text_key
                                            lv_obj_t *obj = lv_label_create(parent_obj);
                                            objects.button_text_key = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            add_style_button_push_opaque(obj);
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
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_32, LV_PART_MAIN | LV_STATE_DEFAULT);
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
                            lv_obj_set_pos(obj, 141, -13);
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
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_encoder_text_arc_1, LV_EVENT_ALL, 0);
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
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_encoder_text_arc_2, LV_EVENT_ALL, 0);
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
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_encoder_text_arc_3, LV_EVENT_ALL, 0);
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
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_encoder_text_arc_4, LV_EVENT_ALL, 0);
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
                                    add_style_encoders_text(obj);
                                    lv_label_set_text(obj, "20");
                                }
                                {
                                    // encoder_text_value_2
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.encoder_text_value_2 = obj;
                                    lv_obj_set_pos(obj, 35, -45);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    add_style_text_standard_value(obj);
                                    lv_label_set_text(obj, "40");
                                }
                                {
                                    // encoder_text_value_4
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.encoder_text_value_4 = obj;
                                    lv_obj_set_pos(obj, 35, 25);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
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
                                    add_style_text_standard_value(obj);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
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
                            lv_obj_set_pos(obj, -9, 135);
                            lv_obj_set_size(obj, 300, 45);
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
                                    lv_obj_set_pos(obj, -108, -10);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "KEY");
                                }
                                {
                                    // text_title_transpose
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_title_transpose = obj;
                                    lv_obj_set_pos(obj, -3, -10);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    add_style_title_text_style(obj);
                                    lv_label_set_text(obj, "TRANSPOSE");
                                }
                                {
                                    // text_title_octave
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_title_octave = obj;
                                    lv_obj_set_pos(obj, 97, -10);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa8fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "OCTAVE");
                                }
                                {
                                    // button_key_dec
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_key_dec = obj;
                                    lv_obj_set_pos(obj, -130, 10);
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
                                            objects.obj0 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "-");
                                        }
                                    }
                                }
                                {
                                    // button_key_inc
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_key_inc = obj;
                                    lv_obj_set_pos(obj, -80, 10);
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
                                            objects.obj1 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "+");
                                        }
                                    }
                                }
                                {
                                    // button_trans_dec
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_trans_dec = obj;
                                    lv_obj_set_pos(obj, -28, 10);
                                    lv_obj_set_size(obj, 40, 20);
                                    add_style_button_touch_inc_dec(obj);
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
                                            objects.obj2 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            add_style_button_push_opaque(obj);
                                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "-");
                                        }
                                    }
                                }
                                {
                                    // button_trans_inc
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_trans_inc = obj;
                                    lv_obj_set_pos(obj, 22, 10);
                                    lv_obj_set_size(obj, 40, 20);
                                    add_style_button_touch_inc_dec(obj);
                                    {
                                        lv_obj_t *parent_obj = obj;
                                        {
                                            lv_obj_t *obj = lv_label_create(parent_obj);
                                            objects.obj3 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "+");
                                        }
                                    }
                                }
                                {
                                    // button_oct_dec
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_oct_dec = obj;
                                    lv_obj_set_pos(obj, 77, 10);
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
                                            objects.obj4 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            add_style_button_push_opaque(obj);
                                            lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "-");
                                        }
                                    }
                                }
                                {
                                    // button_oct_inc
                                    lv_obj_t *obj = lv_btn_create(parent_obj);
                                    objects.button_oct_inc = obj;
                                    lv_obj_set_pos(obj, 127, 10);
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
                                            objects.obj5 = obj;
                                            lv_obj_set_pos(obj, 0, 0);
                                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                            add_style_button_push_opaque(obj);
                                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_16, LV_PART_MAIN | LV_STATE_DEFAULT);
                                            lv_label_set_text(obj, "+");
                                        }
                                    }
                                }
                            }
                        }
                        {
                            lv_obj_t *obj = lv_line_create(parent_obj);
                            objects.obj6 = obj;
                            lv_obj_set_pos(obj, 15, 132);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            static lv_point_t line_points[] = {
                                { 0, 0 },
                                { 250, 0 }
                            };
                            lv_line_set_points(obj, line_points, 2);
                            lv_obj_set_style_line_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                        }
                    }
                }
                {
                    // tab_scales_arp
                    lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "Scales/Arp");
                    objects.tab_scales_arp = obj;
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_line_create(parent_obj);
                            objects.obj7 = obj;
                            lv_obj_set_pos(obj, 15, 20);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            static lv_point_t line_points[] = {
                                { 0, 0 },
                                { 250, 0 }
                            };
                            lv_line_set_points(obj, line_points, 2);
                            lv_obj_set_style_line_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                        }
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, -60, -90);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            add_style_title_text_style(obj);
                            lv_label_set_text(obj, "ARPEGGIATOR/SCALES");
                        }
                        {
                            lv_obj_t *obj = lv_roller_create(parent_obj);
                            objects.obj8 = obj;
                            lv_obj_set_pos(obj, 12, 56);
                            lv_obj_set_size(obj, 80, 99);
                            lv_roller_set_options(obj, "Major \nMinor\nDorian \nPhrygian\nLydian \nMixolydian\nLocrian", LV_ROLLER_MODE_NORMAL);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xfffafafa), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xff2f3237), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_SELECTED | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_opa(obj, 190, LV_PART_SELECTED | LV_STATE_DEFAULT);
                        }
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 35, 39);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_label_set_text(obj, "SCALE");
                        }
                        {
                            lv_obj_t *obj = lv_roller_create(parent_obj);
                            objects.obj9 = obj;
                            lv_obj_set_pos(obj, 201, 56);
                            lv_obj_set_size(obj, 80, 100);
                            lv_roller_set_options(obj, "UP\nDOWN\nUP/DOWN\nPLAYED\nCHORD", LV_ROLLER_MODE_NORMAL);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xff2f3237), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_SELECTED | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_opa(obj, 190, LV_PART_SELECTED | LV_STATE_DEFAULT);
                        }
                        {
                            lv_obj_t *obj = lv_roller_create(parent_obj);
                            objects.obj10 = obj;
                            lv_obj_set_pos(obj, 105, 56);
                            lv_obj_set_size(obj, 80, 100);
                            lv_roller_set_options(obj, "1/128\n1/64\n1/32\n1/16\n1/8\n1/4\n1/2\n1/1\n2/1\n4/1\n6/1\n8/1\n12/1\n16/1\n", LV_ROLLER_MODE_NORMAL);
                            lv_obj_set_style_bg_grad_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_opa(obj, 190, LV_PART_SELECTED | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_SELECTED | LV_STATE_DEFAULT);
                        }
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 132, 39);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "RATE");
                        }
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            lv_obj_set_pos(obj, 225, 39);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "MODE");
                        }
                    }
                }
                {
                    lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "Super \nFaders");
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_line_create(parent_obj);
                            objects.obj11 = obj;
                            lv_obj_set_pos(obj, 10, 139);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            static lv_point_t line_points[] = {
                                { 0, 0 },
                                { 270, 0 }
                            };
                            lv_line_set_points(obj, line_points, 2);
                            lv_obj_set_style_line_color(obj, lv_color_hex(0xff2a2a2a), LV_PART_MAIN | LV_STATE_DEFAULT);
                        }
                        {
                            // button_fader_animate
                            lv_obj_t *obj = lv_btn_create(parent_obj);
                            objects.button_fader_animate = obj;
                            lv_obj_set_pos(obj, 220, 46);
                            lv_obj_set_size(obj, 73, 25);
                            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                            {
                                lv_obj_t *parent_obj = obj;
                                {
                                    // button_fader_animate_text
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.button_fader_animate_text = obj;
                                    lv_obj_set_pos(obj, 0, 0);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_add_flag(obj, LV_OBJ_FLAG_CHECKABLE);
                                    lv_obj_add_state(obj, LV_STATE_FOCUSED|LV_STATE_CHECKED);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffc711d5), LV_PART_MAIN | LV_STATE_CHECKED);
                                    lv_label_set_text(obj, "ANIMATE");
                                }
                            }
                        }
                        {
                            // button_fader_gravity_1
                            lv_obj_t *obj = lv_btn_create(parent_obj);
                            objects.button_fader_gravity_1 = obj;
                            lv_obj_set_pos(obj, 220, 75);
                            lv_obj_set_size(obj, 73, 25);
                            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                            {
                                lv_obj_t *parent_obj = obj;
                                {
                                    // button_fader_animate_text_1
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.button_fader_animate_text_1 = obj;
                                    lv_obj_set_pos(obj, 0, 0);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "GRAVITY");
                                }
                            }
                        }
                        {
                            // button_fader_gravity_2
                            lv_obj_t *obj = lv_btn_create(parent_obj);
                            objects.button_fader_gravity_2 = obj;
                            lv_obj_set_pos(obj, 220, 104);
                            lv_obj_set_size(obj, 73, 25);
                            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                            {
                                lv_obj_t *parent_obj = obj;
                                {
                                    // button_fader_animate_text_2
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.button_fader_animate_text_2 = obj;
                                    lv_obj_set_pos(obj, 0, 0);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "RESET");
                                }
                            }
                        }
                        {
                            // button_fader_animate_1
                            lv_obj_t *obj = lv_btn_create(parent_obj);
                            objects.button_fader_animate_1 = obj;
                            lv_obj_set_pos(obj, 11, 156);
                            lv_obj_set_size(obj, 73, 25);
                            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_width(obj, 1, LV_PART_MAIN | LV_STATE_DEFAULT);
                            {
                                lv_obj_t *parent_obj = obj;
                                {
                                    // button_fader_animate_text_3
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.button_fader_animate_text_3 = obj;
                                    lv_obj_set_pos(obj, 0, 0);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_12, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "ANIMATE");
                                }
                            }
                        }
                        {
                            // text_fader_assign_mode
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.text_fader_assign_mode = obj;
                            lv_obj_set_pos(obj, 10, 145);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "ASSIGN MODE");
                        }
                        {
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.obj12 = obj;
                            lv_obj_set_pos(obj, 0, 0);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "SUPER FADERS");
                        }
                        {
                            // text_fader_2
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.text_fader_2 = obj;
                            lv_obj_set_pos(obj, 130, 30);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "FADER 1");
                        }
                        {
                            // text_fader_1_cc
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.text_fader_1_cc = obj;
                            lv_obj_set_pos(obj, 26, 51);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "CC 07 (VOLUME)");
                        }
                        {
                            // text_fader_2_cc
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.text_fader_2_cc = obj;
                            lv_obj_set_pos(obj, 130, 51);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "CC74 (FILTER)");
                        }
                        {
                            // text_fader_1
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.text_fader_1 = obj;
                            lv_obj_set_pos(obj, 26, 30);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_14, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_text_color(obj, lv_color_hex(0xffa0fff9), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "FADER 1");
                        }
                        {
                            // bar_fader_text_1
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.bar_fader_text_1 = obj;
                            lv_obj_set_pos(obj, 65, 113);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_22, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "104");
                        }
                        {
                            // bar_fader_text_2
                            lv_obj_t *obj = lv_label_create(parent_obj);
                            objects.bar_fader_text_2 = obj;
                            lv_obj_set_pos(obj, 169, 113);
                            lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                            lv_obj_set_style_text_font(obj, &lv_font_montserrat_22, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_label_set_text(obj, "53");
                        }
                        {
                            // bar_fader_1
                            lv_obj_t *obj = lv_bar_create(parent_obj);
                            objects.bar_fader_1 = obj;
                            lv_obj_set_pos(obj, 26, 135);
                            lv_obj_set_size(obj, 70, 30);
                            lv_bar_set_range(obj, 1, 127);
                            lv_bar_set_value(obj, 64, LV_ANIM_ON);
                            lv_obj_add_flag(obj, LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_CHECKABLE|LV_OBJ_FLAG_SCROLL_ONE);
                            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff2a2a2a), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_transform_angle(obj, 2700, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xffe4ff00), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                            lv_obj_set_style_radius(obj, 0, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                            lv_obj_set_style_transform_angle(obj, 2700, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                        }
                        {
                            // bar_fader_2
                            lv_obj_t *obj = lv_bar_create(parent_obj);
                            objects.bar_fader_2 = obj;
                            lv_obj_set_pos(obj, 130, 135);
                            lv_obj_set_size(obj, 70, 30);
                            lv_bar_set_range(obj, 1, 127);
                            lv_bar_set_value(obj, 64, LV_ANIM_ON);
                            lv_obj_add_flag(obj, LV_OBJ_FLAG_SCROLLABLE|LV_OBJ_FLAG_CHECKABLE|LV_OBJ_FLAG_SCROLL_ONE);
                            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xff2a2a2a), LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_transform_angle(obj, 2700, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_color(obj, lv_color_hex(0xffe4ff00), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                            lv_obj_set_style_radius(obj, 0, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                            lv_obj_set_style_transform_angle(obj, 2700, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                        }
                    }
                }
                {
                    // tab_super_encoders
                    lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "Super \nEncoders");
                    objects.tab_super_encoders = obj;
                    lv_obj_set_style_text_color(obj, lv_color_hex(0xffe4ff00), LV_PART_MAIN | LV_STATE_DEFAULT);
                    {
                        lv_obj_t *parent_obj = obj;
                        {
                            lv_obj_t *obj = lv_obj_create(parent_obj);
                            lv_obj_set_pos(obj, 0, -10);
                            lv_obj_set_size(obj, 290, 190);
                            lv_obj_set_style_pad_left(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_pad_top(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_pad_right(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_pad_bottom(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_bg_opa(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            lv_obj_set_style_radius(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                            {
                                lv_obj_t *parent_obj = obj;
                                {
                                    lv_obj_t *obj = lv_tabview_create(parent_obj, LV_DIR_TOP, 32);
                                    lv_obj_set_pos(obj, 157, 26);
                                    lv_obj_set_size(obj, 133, 142);
                                    {
                                        lv_obj_t *parent_obj = obj;
                                        {
                                            lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "1");
                                        }
                                        {
                                            lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "2");
                                        }
                                        {
                                            lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "3");
                                        }
                                        {
                                            lv_obj_t *obj = lv_tabview_add_tab(parent_obj, "4");
                                        }
                                    }
                                }
                                {
                                    lv_obj_t *obj = lv_line_create(parent_obj);
                                    objects.obj13 = obj;
                                    lv_obj_set_pos(obj, -13, 4);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    static lv_point_t line_points[] = {
                                        { 160, 0 },
                                        { 160, 150 }
                                    };
                                    lv_line_set_points(obj, line_points, 2);
                                    lv_obj_set_style_line_color(obj, lv_color_hex(0xff2a2a2a), LV_PART_MAIN | LV_STATE_DEFAULT);
                                }
                                {
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    lv_obj_set_pos(obj, 79, -85);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    add_style_text_standard_value(obj);
                                    lv_obj_set_style_text_font(obj, &lv_font_montserrat_10, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_label_set_text(obj, "ENCODER MAPPED CC'S");
                                }
                                {
                                    // text_encoder_1
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_1 = obj;
                                    lv_obj_set_pos(obj, 23, 7);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_label_set_text(obj, "ENC 1");
                                }
                                {
                                    // text_encoder_2
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_2 = obj;
                                    lv_obj_set_pos(obj, 94, 7);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_label_set_text(obj, "ENC 2");
                                }
                                {
                                    // text_encoder_3
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_3 = obj;
                                    lv_obj_set_pos(obj, 21, 94);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_label_set_text(obj, "ENC 3");
                                }
                                {
                                    // text_encoder_4
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_4 = obj;
                                    lv_obj_set_pos(obj, 94, 94);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_label_set_text(obj, "ENC 4");
                                }
                                {
                                    // arc_encoder_1
                                    lv_obj_t *obj = lv_arc_create(parent_obj);
                                    objects.arc_encoder_1 = obj;
                                    lv_obj_set_pos(obj, 12, 22);
                                    lv_obj_set_size(obj, 50, 50);
                                    lv_arc_set_range(obj, 1, 127);
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_arc_encoder_1, LV_EVENT_ALL, 0);
                                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffa0fff9), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_MAIN | LV_STATE_DEFAULT);
                                }
                                {
                                    // arc_encoder_2
                                    lv_obj_t *obj = lv_arc_create(parent_obj);
                                    objects.arc_encoder_2 = obj;
                                    lv_obj_set_pos(obj, 84, 22);
                                    lv_obj_set_size(obj, 50, 50);
                                    lv_arc_set_range(obj, 1, 127);
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_arc_encoder_2, LV_EVENT_ALL, 0);
                                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffa0fff9), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_MAIN | LV_STATE_DEFAULT);
                                }
                                {
                                    // arc_encoder_3
                                    lv_obj_t *obj = lv_arc_create(parent_obj);
                                    objects.arc_encoder_3 = obj;
                                    lv_obj_set_pos(obj, 12, 109);
                                    lv_obj_set_size(obj, 50, 50);
                                    lv_arc_set_range(obj, 1, 127);
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_arc_encoder_3, LV_EVENT_ALL, 0);
                                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffa0fff9), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_MAIN | LV_STATE_DEFAULT);
                                }
                                {
                                    // arc_encoder_4
                                    lv_obj_t *obj = lv_arc_create(parent_obj);
                                    objects.arc_encoder_4 = obj;
                                    lv_obj_set_pos(obj, 84, 109);
                                    lv_obj_set_size(obj, 50, 50);
                                    lv_arc_set_range(obj, 1, 127);
                                    lv_obj_add_event_cb(obj, event_handler_cb_main_arc_encoder_4, LV_EVENT_ALL, 0);
                                    lv_obj_set_style_arc_color(obj, lv_color_hex(0xffa0fff9), LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_INDICATOR | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_color(obj, lv_color_hex(0xffa0fff9), LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_bg_opa(obj, 0, LV_PART_KNOB | LV_STATE_DEFAULT);
                                    lv_obj_set_style_border_width(obj, 0, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_rounded(obj, false, LV_PART_MAIN | LV_STATE_DEFAULT);
                                    lv_obj_set_style_arc_width(obj, 6, LV_PART_MAIN | LV_STATE_DEFAULT);
                                }
                                {
                                    // text_encoder_value_1
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_value_1 = obj;
                                    lv_obj_set_pos(obj, 31, 42);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_add_event_cb(obj, action_encoder_mimic_1, LV_EVENT_VALUE_CHANGED, (void *)0);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_FOCUSED);
                                    lv_label_set_text(obj, "77");
                                }
                                {
                                    // text_encoder_value_2
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_value_2 = obj;
                                    lv_obj_set_pos(obj, 106, 42);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_FOCUSED);
                                    lv_label_set_text(obj, "0");
                                }
                                {
                                    // text_encoder_value_3
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_value_3 = obj;
                                    lv_obj_set_pos(obj, 29, 127);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_FOCUSED);
                                    lv_label_set_text(obj, "114");
                                }
                                {
                                    // text_encoder_value_4
                                    lv_obj_t *obj = lv_label_create(parent_obj);
                                    objects.text_encoder_value_4 = obj;
                                    lv_obj_set_pos(obj, 103, 127);
                                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                                    lv_label_set_long_mode(obj, LV_LABEL_LONG_CLIP);
                                    lv_obj_set_style_align(obj, LV_ALIGN_CENTER, LV_PART_MAIN | LV_STATE_FOCUSED);
                                    lv_label_set_text(obj, "");
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    tick_screen_main();
}

void tick_screen_main() {
    {
        int32_t new_val = get_var_encoder_1_val();
        int32_t cur_val = lv_arc_get_value(objects.encoder_text_arc_1);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.encoder_text_arc_1;
            lv_arc_set_value(objects.encoder_text_arc_1, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_2_val();
        int32_t cur_val = lv_arc_get_value(objects.encoder_text_arc_2);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.encoder_text_arc_2;
            lv_arc_set_value(objects.encoder_text_arc_2, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_3_val();
        int32_t cur_val = lv_arc_get_value(objects.encoder_text_arc_3);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.encoder_text_arc_3;
            lv_arc_set_value(objects.encoder_text_arc_3, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_4_val();
        int32_t cur_val = lv_arc_get_value(objects.encoder_text_arc_4);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.encoder_text_arc_4;
            lv_arc_set_value(objects.encoder_text_arc_4, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_1_val();
        int32_t cur_val = lv_arc_get_value(objects.arc_encoder_1);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.arc_encoder_1;
            lv_arc_set_value(objects.arc_encoder_1, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_2_val();
        int32_t cur_val = lv_arc_get_value(objects.arc_encoder_2);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.arc_encoder_2;
            lv_arc_set_value(objects.arc_encoder_2, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_3_val();
        int32_t cur_val = lv_arc_get_value(objects.arc_encoder_3);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.arc_encoder_3;
            lv_arc_set_value(objects.arc_encoder_3, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        int32_t new_val = get_var_encoder_4_val();
        int32_t cur_val = lv_arc_get_value(objects.arc_encoder_4);
        if (new_val != cur_val) {
            tick_value_change_obj = objects.arc_encoder_4;
            lv_arc_set_value(objects.arc_encoder_4, new_val);
            tick_value_change_obj = NULL;
        }
    }
    {
        const char *new_val = get_var_encoder_4_val();
        const char *cur_val = lv_label_get_text(objects.text_encoder_value_4);
        if (strcmp(new_val, cur_val) != 0) {
            tick_value_change_obj = objects.text_encoder_value_4;
            lv_label_set_text(objects.text_encoder_value_4, new_val);
            tick_value_change_obj = NULL;
        }
    }
}

void create_screen_splash() {
    lv_obj_t *obj = lv_obj_create(0);
    objects.splash = obj;
    lv_obj_set_pos(obj, 0, 0);
    lv_obj_set_size(obj, 320, 240);
    lv_obj_add_event_cb(obj, action_change_page, LV_EVENT_PRESSED, (void *)1);
    lv_obj_set_style_bg_color(obj, lv_color_hex(0xff000000), LV_PART_MAIN | LV_STATE_DEFAULT);
    {
        lv_obj_t *parent_obj = obj;
        {
            // animation_splash_timer
            lv_obj_t *obj = lv_animimg_create(parent_obj);
            objects.animation_splash_timer = obj;
            lv_obj_set_pos(obj, 0, 0);
            lv_obj_set_size(obj, 320, 240);
            {
                lv_obj_t *parent_obj = obj;
                {
                    // animation_splash
                    lv_obj_t *obj = lv_img_create(parent_obj);
                    objects.animation_splash = obj;
                    lv_obj_set_pos(obj, 0, 0);
                    lv_obj_set_size(obj, LV_SIZE_CONTENT, LV_SIZE_CONTENT);
                    lv_img_set_src(obj, &img_midi_playground_splash_screen);
                }
            }
        }
    }
    
    tick_screen_splash();
}

void tick_screen_splash() {
}



typedef void (*tick_screen_func_t)();
tick_screen_func_t tick_screen_funcs[] = {
    tick_screen_main,
    tick_screen_splash,
};
void tick_screen(int screen_index) {
    tick_screen_funcs[screen_index]();
}
void tick_screen_by_id(enum ScreensEnum screenId) {
    tick_screen_funcs[screenId - 1]();
}

void create_screens() {
    lv_disp_t *dispp = lv_disp_get_default();
    lv_theme_t *theme = lv_theme_default_init(dispp, lv_palette_main(LV_PALETTE_BLUE), lv_palette_main(LV_PALETTE_RED), true, LV_FONT_DEFAULT);
    lv_disp_set_theme(dispp, theme);
    
    create_screen_main();
    create_screen_splash();
}
