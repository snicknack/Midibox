#include "styles.h"
#include "images.h"
#include "fonts.h"

#include "ui.h"
#include "screens.h"

//
// Style: Button Style
//

void init_style_button_style_MAIN_SCROLLED(lv_style_t *style) {
    lv_style_set_border_opa(style, 255);
};

lv_style_t *get_style_button_style_MAIN_SCROLLED() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_button_style_MAIN_SCROLLED(style);
    }
    return style;
};

void init_style_button_style_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_outline_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_outline_opa(style, 255);
    lv_style_set_text_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_text_opa(style, 255);
    lv_style_set_align(style, LV_ALIGN_CENTER);
    lv_style_set_bg_opa(style, 0);
    lv_style_set_bg_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_outline_width(style, 1);
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
    lv_obj_add_style(obj, get_style_button_style_MAIN_SCROLLED(), LV_PART_MAIN | LV_STATE_SCROLLED);
    lv_obj_add_style(obj, get_style_button_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_button_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_button_style_MAIN_SCROLLED(), LV_PART_MAIN | LV_STATE_SCROLLED);
    lv_obj_remove_style(obj, get_style_button_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
// Style: button_touch_inc_dec
//

void init_style_button_touch_inc_dec_MAIN_DEFAULT(lv_style_t *style) {
    init_style_button_style_MAIN_DEFAULT(style);
    
    lv_style_set_bg_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_bg_opa(style, 0);
    lv_style_set_outline_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_outline_width(style, 1);
    lv_style_set_text_color(style, lv_color_hex(0xff00e0ff));
    lv_style_set_text_font(style, &lv_font_montserrat_12);
    lv_style_set_radius(style, 3);
    lv_style_set_align(style, LV_ALIGN_CENTER);
};

lv_style_t *get_style_button_touch_inc_dec_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_button_touch_inc_dec_MAIN_DEFAULT(style);
    }
    return style;
};

void init_style_button_touch_inc_dec_MAIN_SCROLLED(lv_style_t *style) {
    init_style_button_style_MAIN_SCROLLED(style);
    
};

lv_style_t *get_style_button_touch_inc_dec_MAIN_SCROLLED() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_button_touch_inc_dec_MAIN_SCROLLED(style);
    }
    return style;
};

void add_style_button_touch_inc_dec(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_button_touch_inc_dec_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_add_style(obj, get_style_button_touch_inc_dec_MAIN_SCROLLED(), LV_PART_MAIN | LV_STATE_SCROLLED);
};

void remove_style_button_touch_inc_dec(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_button_touch_inc_dec_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_remove_style(obj, get_style_button_touch_inc_dec_MAIN_SCROLLED(), LV_PART_MAIN | LV_STATE_SCROLLED);
};

//
// Style: Text Main Colour
//

void init_style_text_main_colour_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_align(style, LV_ALIGN_CENTER);
    lv_style_set_text_opa(style, 255);
    lv_style_set_text_color(style, lv_color_hex(0xfffff800));
    lv_style_set_text_font(style, &lv_font_montserrat_14);
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

void init_style_text_main_colour_MAIN_FOCUSED(lv_style_t *style) {
    lv_style_set_text_color(style, lv_color_hex(0xfffff800));
};

lv_style_t *get_style_text_main_colour_MAIN_FOCUSED() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_text_main_colour_MAIN_FOCUSED(style);
    }
    return style;
};

void add_style_text_main_colour(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_text_main_colour_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_add_style(obj, get_style_text_main_colour_MAIN_FOCUSED(), LV_PART_MAIN | LV_STATE_FOCUSED);
};

void remove_style_text_main_colour(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_text_main_colour_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
    lv_obj_remove_style(obj, get_style_text_main_colour_MAIN_FOCUSED(), LV_PART_MAIN | LV_STATE_FOCUSED);
};

//
// Style: button_push_opaque
//

void init_style_button_push_opaque_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_align(style, LV_ALIGN_CENTER);
    lv_style_set_text_font(style, &lv_font_montserrat_16);
};

lv_style_t *get_style_button_push_opaque_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_button_push_opaque_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_button_push_opaque(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_button_push_opaque_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_button_push_opaque(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_button_push_opaque_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
// Style: encoders_text
//

void init_style_encoders_text_MAIN_DEFAULT(lv_style_t *style) {
    init_style_button_push_opaque_MAIN_DEFAULT(style);
    
    lv_style_set_text_font(style, &lv_font_montserrat_14);
    lv_style_set_text_color(style, lv_color_hex(0xffa8fff9));
    lv_style_set_align(style, LV_ALIGN_CENTER);
};

lv_style_t *get_style_encoders_text_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_encoders_text_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_encoders_text(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_encoders_text_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_encoders_text(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_encoders_text_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
// Style: text_standard_value
//

void init_style_text_standard_value_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_text_font(style, &lv_font_montserrat_14);
    lv_style_set_text_color(style, lv_color_hex(0xffa8fff9));
    lv_style_set_align(style, LV_ALIGN_CENTER);
};

lv_style_t *get_style_text_standard_value_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_text_standard_value_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_text_standard_value(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_text_standard_value_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_text_standard_value(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_text_standard_value_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
// Style: title_text_style
//

void init_style_title_text_style_MAIN_DEFAULT(lv_style_t *style) {
    lv_style_set_text_color(style, lv_color_hex(0xffa8fff9));
    lv_style_set_align(style, LV_ALIGN_CENTER);
    lv_style_set_text_font(style, &lv_font_montserrat_14);
};

lv_style_t *get_style_title_text_style_MAIN_DEFAULT() {
    static lv_style_t *style;
    if (!style) {
        style = lv_mem_alloc(sizeof(lv_style_t));
        lv_style_init(style);
        init_style_title_text_style_MAIN_DEFAULT(style);
    }
    return style;
};

void add_style_title_text_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_add_style(obj, get_style_title_text_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

void remove_style_title_text_style(lv_obj_t *obj) {
    (void)obj;
    lv_obj_remove_style(obj, get_style_title_text_style_MAIN_DEFAULT(), LV_PART_MAIN | LV_STATE_DEFAULT);
};

//
//
//

void add_style(lv_obj_t *obj, int32_t styleIndex) {
    typedef void (*AddStyleFunc)(lv_obj_t *obj);
    static const AddStyleFunc add_style_funcs[] = {
        add_style_button_style,
        add_style_button_touch_inc_dec,
        add_style_text_main_colour,
        add_style_button_push_opaque,
        add_style_encoders_text,
        add_style_text_standard_value,
        add_style_title_text_style,
    };
    add_style_funcs[styleIndex](obj);
}

void remove_style(lv_obj_t *obj, int32_t styleIndex) {
    typedef void (*RemoveStyleFunc)(lv_obj_t *obj);
    static const RemoveStyleFunc remove_style_funcs[] = {
        remove_style_button_style,
        remove_style_button_touch_inc_dec,
        remove_style_text_main_colour,
        remove_style_button_push_opaque,
        remove_style_encoders_text,
        remove_style_text_standard_value,
        remove_style_title_text_style,
    };
    remove_style_funcs[styleIndex](obj);
}

