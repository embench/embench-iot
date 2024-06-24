/* Copyright 2024 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Modified For Embench:
    - extracted DepthwiseConvPerChannel kernel and unit test, converted from C++ to C.
==============================================================================*/

#include "stdint.h"

#define MIN(X, Y) (((X) < (Y)) ? (X) : (Y))
#define MAX(X, Y) (((X) < (Y)) ? (Y) : (X))

typedef enum __attribute__((__packed__))
PaddingType
{
    kNone,
    kSame,
    kValid
} PaddingType;

typedef struct
{
    int16_t width;
    int16_t height;
    // offset is used for calculating "remaining" padding, for example, `width`
    // is 1 and `width_offset` is 1, so padding_left is 1 while padding_right is
    // 1 + 1 = 2.
    int16_t width_offset;
    // Same as width_offset except it's over the height dimension.
    int16_t height_offset;
} PaddingValues;

typedef struct
{
    PaddingType padding_type;
    PaddingValues padding_values;
    int16_t stride_width;
    int16_t stride_height;
    int16_t dilation_width_factor;
    int16_t dilation_height_factor;
    int16_t depth_multiplier;
    // uint8_t inference params.
    // TODO(b/65838351): Use smaller types if appropriate.
    int32_t input_offset;
    int32_t weights_offset;
    int32_t output_offset;
    int32_t output_multiplier;
    int output_shift;
    // uint8_t, etc, activation params.
    int32_t quantized_activation_min;
    int32_t quantized_activation_max;
    // float activation params.
    float float_activation_min;
    float float_activation_max;
    const int32_t *output_multiplier_per_channel;
    const int32_t *output_shift_per_channel;
} DepthwiseParams;

typedef struct
{
    int32_t dims_[6];
    int32_t size_;
} RuntimeShape;

static inline int32_t Dims(const RuntimeShape *rsh, int i)
{
    return rsh->dims_[i];
}
static inline int32_t DimensionsCount(const RuntimeShape *rsh)
{
    return rsh->size_;
}

static inline int MatchingDim(const RuntimeShape *shape1, int index1,
                              const RuntimeShape *shape2, int index2)
{
    return MIN(Dims(shape1, index1), Dims(shape2, index2));
}

static int32_t MultiplyByQuantizedMultiplier(int32_t x, int32_t quantized_multiplier,
                                             int shift)
{
    const int64_t total_shift = 31 - shift;
    const int64_t round = (int64_t)1 << (total_shift - 1);
    int64_t result = x * ((int64_t)quantized_multiplier) + round;
    result = result >> total_shift;

    return result;
}

static inline int Offset4(const RuntimeShape *shape, int i0, int i1, int i2, int i3)
{
    const int32_t *dims_data = shape->dims_;
    return ((i0 * dims_data[1] + i1) * dims_data[2] + i2) * dims_data[3] + i3;
}

static void __attribute__((__noinline__)) DepthwiseConvPerChannel(
    const DepthwiseParams *params, const int32_t *output_multiplier,
    const int32_t *output_shift, const RuntimeShape *input_shape,
    const int8_t *input_data, const RuntimeShape *filter_shape,
    const int8_t *filter_data, const RuntimeShape *bias_shape,
    const int32_t *bias_data, const RuntimeShape *output_shape,
    int8_t *output_data)
{
    // Get parameters.
    // TODO(b/141565753): Re-introduce ScopedProfilingLabel on Micro.
    const int stride_width = params->stride_width;
    const int stride_height = params->stride_height;
    const int dilation_width_factor = params->dilation_width_factor;
    const int dilation_height_factor = params->dilation_height_factor;
    const int pad_width = params->padding_values.width;
    const int pad_height = params->padding_values.height;
    const int depth_multiplier = params->depth_multiplier;
    const int32_t input_offset = params->input_offset;
    const int32_t output_offset = params->output_offset;
    const int32_t output_activation_min = params->quantized_activation_min;
    const int32_t output_activation_max = params->quantized_activation_max;

    const int batches = MatchingDim(input_shape, 0, output_shape, 0);
    const int output_depth = MatchingDim(filter_shape, 3, output_shape, 3);
    const int input_height = Dims(input_shape, 1);
    const int input_width = Dims(input_shape, 2);
    const int input_depth = Dims(input_shape, 3);
    const int filter_height = Dims(filter_shape, 1);
    const int filter_width = Dims(filter_shape, 2);
    const int output_height = Dims(output_shape, 1);
    const int output_width = Dims(output_shape, 2);

    for (int batch = 0; batch < batches; ++batch)
    {
        for (int out_y = 0; out_y < output_height; ++out_y)
        {
            for (int out_x = 0; out_x < output_width; ++out_x)
            {
                for (int in_channel = 0; in_channel < input_depth; ++in_channel)
                {
                    for (int m = 0; m < depth_multiplier; ++m)
                    {
                        const int output_channel = m + in_channel * depth_multiplier;
                        const int in_x_origin = (out_x * stride_width) - pad_width;
                        const int in_y_origin = (out_y * stride_height) - pad_height;
                        int32_t acc = 0;
                        for (int filter_y = 0; filter_y < filter_height; ++filter_y)
                        {
                            for (int filter_x = 0; filter_x < filter_width; ++filter_x)
                            {
                                const int in_x = in_x_origin + dilation_width_factor * filter_x;
                                const int in_y =
                                    in_y_origin + dilation_height_factor * filter_y;
                                // Zero padding by omitting the areas outside the image.
                                const int is_point_inside_image =
                                    (in_x >= 0) && (in_x < input_width) && (in_y >= 0) &&
                                    (in_y < input_height);
                                if (is_point_inside_image)
                                {
                                    int32_t input_val = input_data[Offset4(
                                        input_shape, batch, in_y, in_x, in_channel)];
                                    int32_t filter_val = filter_data[Offset4(
                                        filter_shape, 0, filter_y, filter_x, output_channel)];
                                    // Accumulate with 32 bits accumulator.
                                    // In the nudging process during model quantization, we force
                                    // real value of 0.0 be represented by a quantized value. This
                                    // guarantees that the input_offset is a int8_t, even though
                                    // it is represented using int32_t. int32_t += int8_t *
                                    // (int8_t - int8_t) so the highest value we can get from each
                                    // accumulation is [-127, 127] * ([-128, 127] -
                                    // [-128, 127]), which is [-32512, 32512]. log2(32512)
                                    // = 14.98, which means we can accumulate at least 2^16
                                    // multiplications without overflow. The accumulator is
                                    // applied to a filter so the accumulation logic will hold as
                                    // long as the filter size (filter_y * filter_x * in_channel)
                                    // does not exceed 2^16, which is the case in all the models
                                    // we have seen so far.
                                    // TODO(b/174275578): Add a check to make sure the
                                    // accumulator depth is smaller than 2^16.
                                    acc += filter_val * (input_val + input_offset);
                                }
                            }
                        }
                        if (bias_data)
                        {
                            acc += bias_data[output_channel];
                        }
                        acc = MultiplyByQuantizedMultiplier(
                            acc, output_multiplier[output_channel],
                            output_shift[output_channel]);
                        acc += output_offset;
                        acc = MAX(acc, output_activation_min);
                        acc = MIN(acc, output_activation_max);
                        output_data[Offset4(output_shape, batch, out_y, out_x,
                                            output_channel)] = (int8_t)(acc);
                    }
                }
            }
        }
    }
}

static DepthwiseParams PARAMS = {
    .stride_width = 1,
    .stride_height = 1,
    .dilation_width_factor = 1,
    .dilation_height_factor = 1,
    .padding_values = {
        .width = 0,
        .height = 0,
    },
    .depth_multiplier = 1,
    .input_offset = 128,
    .output_offset = 0,
    .quantized_activation_min = -128,
    .quantized_activation_max = 127,
};

static int32_t OUTPUT_MULTIPLIER[] = {
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
    1152862902,
};
static int32_t OUTPUT_SHIFT[] = {
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
    -8,
};

static RuntimeShape INPUT_SHAPE = {
    .size_ = 4,
    .dims_ = {1, 4, 1, 32, 0, 0},
};
static RuntimeShape FILTER_SHAPE = {
    .size_ = 4,
    .dims_ = {1, 4, 1, 32, 0, 1},
};
static RuntimeShape BIAS_SHAPE = {
    .size_ = 1,
    .dims_ = {32, 0, 0, 0, 0, 0},
};
static RuntimeShape OUTPUT_SHAPE = {
    .size_ = 4,
    .dims_ = {1, 1, 1, 32, 1, 4},
};

static int8_t INPUT_DATA[] = {
    60,
    57,
    62,
    68,
    56,
    34,
    34,
    42,
    63,
    57,
    28,
    26,
    36,
    24,
    7,
    25,
    31,
    0,
    29,
    35,
    1,
    11,
    1,
    30,
    27,
    18,
    12,
    19,
    9,
    8,
    -2,
    -3,
    59,
    61,
    60,
    63,
    52,
    30,
    30,
    44,
    63,
    57,
    24,
    22,
    29,
    23,
    -9,
    27,
    35,
    12,
    28,
    34,
    -2,
    18,
    10,
    28,
    25,
    26,
    24,
    13,
    6,
    15,
    -4,
    -5,
    49,
    57,
    61,
    59,
    42,
    37,
    38,
    45,
    62,
    53,
    19,
    17,
    34,
    25,
    -9,
    32,
    39,
    8,
    29,
    35,
    0,
    25,
    17,
    26,
    24,
    27,
    24,
    8,
    9,
    23,
    -8,
    -3,
    65,
    60,
    54,
    55,
    41,
    27,
    27,
    38,
    54,
    46,
    18,
    22,
    38,
    30,
    0,
    29,
    37,
    10,
    30,
    35,
    4,
    36,
    27,
    33,
    31,
    22,
    17,
    9,
    19,
    35,
    -2,
    1,
};
static int8_t FILTER_DATA[] = {
    -49,
    -59,
    43,
    -70,
    -27,
    47,
    1,
    92,
    -51,
    41,
    46,
    -51,
    -42,
    44,
    55,
    52,
    -59,
    63,
    68,
    -60,
    -73,
    56,
    60,
    48,
    76,
    54,
    -65,
    -46,
    63,
    -87,
    61,
    75,
    -125,
    -17,
    -98,
    -18,
    -29,
    61,
    -32,
    42,
    -77,
    -49,
    39,
    -55,
    -11,
    43,
    -18,
    71,
    -3,
    127,
    39,
    -70,
    -67,
    -16,
    -63,
    55,
    -44,
    37,
    38,
    -32,
    -23,
    37,
    31,
    45,
    82,
    52,
    -57,
    -54,
    50,
    -83,
    58,
    63,
    -90,
    -78,
    -96,
    6,
    -7,
    73,
    -13,
    20,
    -55,
    60,
    61,
    -42,
    -58,
    52,
    40,
    43,
    40,
    41,
    -42,
    -52,
    40,
    -50,
    42,
    25,
    -43,
    -31,
    54,
    14,
    62,
    -66,
    -46,
    -47,
    46,
    101,
    94,
    -62,
    -62,
    -29,
    -50,
    37,
    30,
    41,
    -49,
    -45,
    50,
    -55,
    46,
    38,
    -11,
    -38,
    42,
    13,
    64,
    -86,
    -32,
    -69,
};
static int32_t BIAS_DATA[32] = {
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
};

int8_t OUTPUT_DATA[32];

int8_t EXPECTED_OUTPUT[32] =
    {
        -55,
        -22,
        -23,
        -52,
        18,
        -14,
        -5,
        54,
        -70,
        4,
        27,
        -51,
        -42,
        41,
        -6,
        59,
        -30,
        83,
        39,
        -74,
        -39,
        9,
        25,
        61,
        20,
        30,
        -8,
        -35,
        43,
        -59,
        26,
        19,
};

#define LOCAL_SCALE_FACTOR 1639
void initialise_benchmark(void)
{
}

static int benchmark_body(unsigned int lsf, unsigned int gsf);

void warm_caches(int heat)
{
  int res = benchmark_body(heat, 1);

    return;
}

int benchmark(void)
{
  return benchmark_body(LOCAL_SCALE_FACTOR, GLOBAL_SCALE_FACTOR);
}

static int __attribute__((noinline))
benchmark_body(unsigned int lsf, unsigned int gsf)
{
  for (unsigned int lsf_cnt = 0; lsf_cnt < lsf; lsf_cnt++)
    for (unsigned int gsf_cnt = 0; gsf_cnt < gsf; gsf_cnt++)
      {
        DepthwiseConvPerChannel(&PARAMS, OUTPUT_MULTIPLIER, OUTPUT_SHIFT, &INPUT_SHAPE, INPUT_DATA, &FILTER_SHAPE, FILTER_DATA, &BIAS_SHAPE, BIAS_DATA, &OUTPUT_SHAPE, OUTPUT_DATA);
      }
  return 0;
}

int verify_benchmark(int r)
{
    for (int i = 0;
	 i < sizeof(EXPECTED_OUTPUT) / (sizeof(EXPECTED_OUTPUT[0]));
	 ++i)
      {
        if (EXPECTED_OUTPUT[i] != OUTPUT_DATA[i])
	  {
            return 0;
	  }
      }
    return 1;
}
