/* xgboost benchmark

   Contributor Zachary Susskind <zsusskind@utexas.edu>
   Contributor Konrad Moron <konrad.moron@tum.de>

   This file is part of Embench.

   SPDX-License-Identifier: GPL-3.0-or-later
   */
#include <stdint.h>
#include <stddef.h>

#include "xgboost.h"

#define LOCAL_SCALE_FACTOR 2

static int benchmark_body(int rpt);

void warm_caches(int heat)
{
    int res = benchmark_body(heat);

    return;
}

int benchmark(void)
{
    return benchmark_body(LOCAL_SCALE_FACTOR * CPU_MHZ);
}

static int __attribute__((noinline))
benchmark_body(int rpt)
{
    // Run inference with all samples specified in xgboost.c
    {
        volatile size_t correct = 0;
        for (int i = 0; i < rpt / 10; ++i)
        {
            for (size_t i = 0; i < SAMPLES_IN_FILE; i++)
            {
                uint8_t predicted = predict(X_test[i]);
                uint8_t label = Y_test[i];
                if (predicted == label)
                    correct++;
            }
        }
        return correct;
    }
}

void initialise_benchmark(void)
{
}

// r is the number of errors therefore if r = 0 then output a 1 for correct

int verify_benchmark(int r)
{
    return r >= SAMPLES_IN_FILE * (LOCAL_SCALE_FACTOR * CPU_MHZ / 12);
}
