#include "styles.h"
#include "images.h"
#include "fonts.h"

#include "ui.h"
#include "screens.h"

//
// Style: MIDI BOX COLOUR SCHEME
//

void init_style_midi_box_colour_scheme_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_align(style, LV_ALIGN_CENTER);
};

lv_style_t *get_style_midi_box_colour_scheme_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_midi_box_colour_scheme_MAIN_DEFAULT(style);
    }
    return style;
};

void init_style_midi_box_colour_scheme_MAIN_CHECKED(lv_style_t *style) {
    lv_style_set_text_font(style, &lv_font_montserrat_14);
    lv_style_set_text_color(style, lv_color_hex(0xff1e2c4d));
    lv_style_set_text_opa(style, 255);
};

lv_style_t *get_style_midi_box_colour_scheme_MAIN_CHECKED() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_midi_box_colour_scheme_MAIN_CHECKED(style);
    }
    return style;
};

void add_style_midi_box_colour_scheme(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_midi_box_colour_scheme_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_add_style(obj, get_style_midi_box_colour_scheme_MAIN_CHECKED(), LV_PART_MAIN | LV_STATE_CHECKED);
};

void remove_style_midi_box_colour_scheme(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_midi_box_colour_scheme_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_remove_style(obj, get_style_midi_box_colour_scheme_MAIN_CHECKED(), LV_PART_MAIN | LV_STATE_CHECKED);
};

//
// Style: main_text_style
//

void init_style_main_text_style_MAIN_DEFAULT(lv_style_t *style) {
    init_style_midi_box_colour_scheme_MAIN_DEFAULT(style);
    
    lv_style_set_align(style, LV_ALIGN_TOP_LEFT);
    lv_style_set_text_font(style, &ui_font_montserrat_semi_bold_14);
    lv_style_set_text_color(style, lv_color_hex(0xffa8fff9));
};

lv_style_t *get_style_main_text_style_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_main_text_style_MAIN_DEFAULT(style);
    }
    return style;
};

void init_style_main_text_style_MAIN_CHECKED(lv_style_t *style) {
    init_style_midi_box_colour_scheme_MAIN_CHECKED(style);
    
};

lv_style_t *get_style_main_text_style_MAIN_CHECKED() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_main_text_style_MAIN_CHECKED(style);
    }
    return style;
};

void add_style_main_text_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_main_text_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_add_style(obj, get_style_main_text_style_MAIN_CHECKED(), LV_PART_MAIN | LV_STATE_CHECKED);
};

void remove_style_main_text_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_main_text_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_remove_style(obj, get_style_main_text_style_MAIN_CHECKED(), LV_PART_MAIN | LV_STATE_CHECKED);
};

//
// Style: Button Style
//

void init_style_button_style_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_bg_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_bg_opa(style, 0);
    lv_style_set_outline_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_outline_width(style, 1);
    lv_style_set_text_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_text_font(style, &lv_font_montserrat_12);
    lv_style_set_radius(style, 3);
};

lv_style_t *get_style_button_style_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_button_style_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_button_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_button_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_button_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_button_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
// Style: Text Main Colour
//

void init_style_text_main_colour_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_text_font(style, &ui_font_montserrat_extra_bold_36);
    lv_style_set_text_color(style, lv_color_hex(0xffa8fff9));
    lv_style_set_align(style, LV_ALIGN_TOP_MID);
};

lv_style_t *get_style_text_main_colour_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_text_main_colour_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_text_main_colour(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_text_main_colour_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_text_main_colour(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_text_main_colour_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
//
//

void add_style(lv_obj_t *obj, int32_t styleIndex) {
    typedef void (*AddStyleFunc)(lv_obj_t *obj);
    static const AddStyleFunc add_style_funcs[] = {
        add_style_midi_box_colour_scheme,
        add_style_main_text_style,
        add_style_button_style,
        add_style_text_main_colour,
    };
    add_style_funcs[styleIndex](obj);
}

void remove_style(lv_obj_t *obj, int32_t styleIndex) {
    typedef void (*RemoveStyleFunc)(lv_obj_t *obj);
    static const RemoveStyleFunc remove_style_funcs[] = {
        remove_style_midi_box_colour_scheme,
        remove_style_main_text_style,
        remove_style_button_style,
        remove_style_text_main_colour,
    };
    remove_style_funcs[styleIndex](obj);
}

