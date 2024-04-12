/*
 * Copyright (c) 2018-2020, Jianjia Ma
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * Change Logs:
 * Date           Author       Notes
 * 2019-02-05     Jianjia Ma   The first version
 * 2019-04-18     Jianjia Ma   use callback to save layer's output
 */

#include <stdint.h>

#include "nnom.h"

#include "weights.h"

nnom_model_t *model;
int8_t *input;
void initialise_benchmark(void)
{
	model = nnom_model_create();
	input = 0;
	memcpy(nnom_input_data, input, sizeof(nnom_input_data));
}

static int benchmark_body(int rpt);

void warm_caches(int heat)
{
	int res = benchmark_body(heat);

	return;
}

int benchmark(void)
{
	return benchmark_body(CPU_MHZ);
}

static int __attribute__((noinline))
benchmark_body(int rpt)
{
	model_run(model);
}

int verify_benchmark(int r)
{
	model_delete(model);
	return 11433 == r;
}
