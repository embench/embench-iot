/* xgboost benchmark

   Contributor Zachary Susskind <zsusskind@utexas.edu>
   Contributor Konrad Moron <konrad.moron@tum.de>

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later
   */
#ifndef __XGBOOST_H__
#define __XGBOOST_H__
#include <stdint.h>
#define SAMPLES_IN_FILE 128
#define SAMPLE_SIZE 64
#define NUM_CLASSES 10
#define NUM_TREES 40
uint8_t predict(const uint8_t *x);
extern const uint8_t X_test[SAMPLES_IN_FILE][SAMPLE_SIZE];
extern const uint8_t Y_test[SAMPLES_IN_FILE];
#endif
