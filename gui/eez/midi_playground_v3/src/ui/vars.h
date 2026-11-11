#ifndef EEZ_LVGL_UI_VARS_H
#define EEZ_LVGL_UI_VARS_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// enum declarations



// Flow global variables

enum FlowGlobalVariables {
    FLOW_GLOBAL_VARIABLE_ENCODER_1_VAL = 0,
    FLOW_GLOBAL_VARIABLE_ENCODER_2_VAL = 1,
    FLOW_GLOBAL_VARIABLE_ENCODER_3_VAL = 2,
    FLOW_GLOBAL_VARIABLE_ENCODER_4_VAL = 3
};

// Native global variables

extern int32_t get_var_encoder_1_val();
extern void set_var_encoder_1_val(int32_t value);
extern int32_t get_var_encoder_2_val();
extern void set_var_encoder_2_val(int32_t value);
extern int32_t get_var_encoder_3_val();
extern void set_var_encoder_3_val(int32_t value);
extern int32_t get_var_encoder_4_val();
extern void set_var_encoder_4_val(int32_t value);


#ifdef __cplusplus
}
#endif

#endif /*EEZ_LVGL_UI_VARS_H*/