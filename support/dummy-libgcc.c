/* Dummyy libgcc for the benchmarks

   Copyright (C) 2018-2019 Embecosm Limited

   Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

/* The purpose of this library is to measure the size of code excluding target
   dependent libgcc code. It only makes sense if it is used with
   -gc-sections. */


/* Missing ARM emulation functions */

#ifdef __arm__

unsigned long long
__aeabi_ui2d (unsigned int value __attribute__ ((unused)))
{
  return 0;
}

float
__aeabi_ui2f (unsigned int value __attribute__ ((unused)))
{
  return 0;
}

double
__aeabi_dmul (double FirstValue __attribute__ ((unused)),
	      double SecondValue __attribute__ ((unused)))
{
  return 0.0;
}


unsigned int
__aeabi_d2uiz (double Value __attribute__ ((unused)))
{
  return 0;
}


double
__aeabi_dadd (double FirstValue __attribute__ ((unused)),
	      double SecondValue __attribute__ ((unused)))
{
  return 0.0;
}


double
__aeabi_dsub (double FirstValue __attribute__ ((unused)),
	      double SecondValue __attribute__ ((unused)))
{
  return 0.0;

}


int
__aeabi_d2iz (double Value __attribute__ ((unused)))
{
  return 0;
}


double
__aeabi_ddiv (double Dividend __attribute__ ((unused)),
	      double Divisor __attribute__ ((unused)))
{
  return 0.0;
}


int
__aeabi_dcmplt (double Left __attribute__ ((unused)),
		double Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_dcmpeq (double Left __attribute__ ((unused)),
		double Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_dcmpge (double Left __attribute__ ((unused)),
		double Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_dcmple (double Left __attribute__ ((unused)),
		double Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_dcmpun (double a __attribute__ ((unused)),
		double b __attribute__ ((unused)))
{
  return 0;
}


double
__aeabi_i2d (int Value __attribute__ ((unused)))
{
  return 0.0;
}


int
__aeabi_dcmpgt (double Left __attribute__ ((unused)),
		double Right __attribute__ ((unused)))
{
  return 0;
}


float
__aeabi_fadd (float FirstValue __attribute__ ((unused)),
	      float SecondValue __attribute__ ((unused)))
{
  return 0.0;
}


int
__aeabi_fcmpeq (float Left __attribute__ ((unused)),
		float Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_fcmpge (float Left __attribute__ ((unused)),
		float Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_fcmple (float Left __attribute__ ((unused)),
		float Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_fcmpgt (float Left __attribute__ ((unused)),
		float Right __attribute__ ((unused)))
{
  return 0;
}


int
__aeabi_fcmplt (float Left __attribute__ ((unused)),
		float Right __attribute__ ((unused)))
{
  return 0;
}


float
__aeabi_fsub (float FirstValue __attribute__ ((unused)),
	      float SecondValue __attribute__ ((unused)))
{
  return 0.0;
}


float
__aeabi_i2f (int Value __attribute__ ((unused)))
{
  return 0.0;
}


float
__aeabi_fmul (float FirstValue __attribute__ ((unused)),
	      float SecondValue __attribute__ ((unused)))
{
  return 0.0;
}


float
__aeabi_fdiv (float Dividend __attribute__ ((unused)),
	      float Divisor __attribute__ ((unused)))
{
  return 0.0;
}


int
__aeabi_f2iz (float Value __attribute__ ((unused)))
{
  return 0;
}


unsigned int
__aeabi_f2uiz (float Value __attribute__ ((unused)))
{
  return 0;
}


float
__aeabi_d2f (double Value __attribute__ ((unused)))
{
  return 0.0;
}


double
__aeabi_f2d (float Value __attribute__ ((unused)))
{
  return 0.0;
}


typedef struct
{
  unsigned long long int quot;
  unsigned long long int rem;
} uldivmod_t;

uldivmod_t
__aeabi_uldivmod (unsigned long long int numerator __attribute__ ((unused)),
		  unsigned long long int denominator __attribute__ ((unused)))
{
  uldivmod_t v = { 0, 0 };

  return v;
}

#else /* !__ARM__ */

/* Generic libgcc functions */

double
__adddf3 (double a __attribute__ ((unused)),
	  double b __attribute__ ((unused)))
{
  return 0.0;
}


float
__addsf3 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0.0;
}


long double
__addtf3 (long double a __attribute__ ((unused)),
	  long double b __attribute__ ((unused)))
{
  return 0.0;
}


double
__divdf3 (double a __attribute__ ((unused)),
	  double b __attribute__ ((unused)))
{
  return 0.0;
}


float
__divsf3 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0.0;
}


int
__divsi3 (int a __attribute__ ((unused)), int b __attribute__ ((unused)))
{
  return 0;
}


int
__mulsi3 (int a __attribute__ ((unused)), int b __attribute__ ((unused)))
{
  return 0;
}


long double
__divtf3 (long double a __attribute__ ((unused)),
	  long double b __attribute__ ((unused)))
{
  return 0.0;
}


int
__eqdf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__eqsf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


long double
__extenddftf2 (double a __attribute__ ((unused)))
{
  return 0.0;
}


double
__extendsfdf2 (float a __attribute__ ((unused)))
{
  return 0.0;
}


int
__fixdfsi (double a __attribute__ ((unused)))
{
  return 0;
}


int
__fixsfsi (float a __attribute__ ((unused)))
{
  return 0;
}


unsigned int
__fixunsdfsi (double a __attribute__ ((unused)))
{
  return 0;
}


unsigned int
__fixunssfsi (float a __attribute__ ((unused)))
{
  return 0;
}


double
__floatsidf (int i __attribute__ ((unused)))
{
  return 0.0;
}


float
__floatsisf (int i __attribute__ ((unused)))
{
  return 0.0;
}


double
__floatunsidf (unsigned int i __attribute__ ((unused)))
{
  return 0.0;
}


float
__floatunsisf (unsigned int i __attribute__ ((unused)))
{
  return 0.0;
}


int
__gedf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__gesf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


int
__gtdf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__gtsf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


int
__ledf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__lesf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


int
__ltdf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__ltsf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


int
__lttf2 (long double a __attribute__ ((unused)),
	 long double b __attribute__ ((unused)))
{
  return 0;
}


int
__modsi3 (int a __attribute__ ((unused)),
	  int b __attribute__ ((unused)))
{
  return 0;
}


double
__muldf3 (double a __attribute__ ((unused)),
	  double b __attribute__ ((unused)))
{
  return 0.0;
}


long int
__muldi3 (long int a __attribute__ ((unused)),
	  long int b __attribute__ ((unused)))
{
  return 0;
}


float
__mulsf3 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0.0;
}


long double
__multf3 (long double a __attribute__ ((unused)),
	  long double b __attribute__ ((unused)))
{
  return 0.0;
}


int
__nedf2 (double a __attribute__ ((unused)), double b __attribute__ ((unused)))
{
  return 0;
}


int
__nesf2 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0;
}


double
__subdf3 (double a __attribute__ ((unused)),
	  double b __attribute__ ((unused)))
{
  return 0.0;
}


float
__subsf3 (float a __attribute__ ((unused)), float b __attribute__ ((unused)))
{
  return 0.0;
}


long double
__subtf3 (long double a __attribute__ ((unused)),
	  long double b __attribute__ ((unused)))
{
  return 0.0;
}


float
__truncdfsf2 (double a __attribute__ ((unused)))
{
  return 0.0;
}


double
__trunctfdf2 (long double a __attribute__ ((unused)))
{
  return 0.0;
}


unsigned long
__udivdi3 (unsigned long a __attribute__ ((unused)),
	   unsigned long b __attribute__ ((unused)))
{
  return 0.0;
}


unsigned long
__umoddi3 (unsigned long a __attribute__ ((unused)),
	   unsigned long b __attribute__ ((unused)))
{
  return 0.0;
}


unsigned int
__umodsi3 (unsigned int a __attribute__ ((unused)),
	  unsigned int b __attribute__ ((unused)))
{
  return 0;
}


int
__unorddf2 (double a __attribute__ ((unused)),
	    double b __attribute__ ((unused)))
{
  return 0;
}


int
__unordsf2 (float a __attribute__ ((unused)),
	    float b __attribute__ ((unused)))
{
  return 0;
}


#endif /* __arm__ */

#ifdef __riscv
void
__riscv_save_0 ()
{
}

void
__riscv_save_1 ()
{
}

void
__riscv_save_2 ()
{
}

void
__riscv_save_3 ()
{
}

void
__riscv_save_4 ()
{
}

void
__riscv_save_5 ()
{
}

void
__riscv_save_6 ()
{
}

void
__riscv_save_7 ()
{
}

void
__riscv_save_8 ()
{
}

void
__riscv_save_9 ()
{
}

void
__riscv_save_10 ()
{
}

void
__riscv_save_11 ()
{
}

void
__riscv_save_12 ()
{
}

void
__riscv_restore_0 ()
{
}

void
__riscv_restore_1 ()
{
}

void
__riscv_restore_2 ()
{
}

void
__riscv_restore_3 ()
{
}

void
__riscv_restore_4 ()
{
}

void
__riscv_restore_5 ()
{
}

void
__riscv_restore_6 ()
{
}

void
__riscv_restore_7 ()
{
}

void
__riscv_restore_8 ()
{
}

void
__riscv_restore_9 ()
{
}

void
__riscv_restore_10 ()
{
}

void
__riscv_restore_11 ()
{
}

void
__riscv_restore_12 ()
{
}
#endif

/* Extra functions just for AVR */
#ifdef __AVR__
long long
__adddi3 (long long a __attribute__ ((unused)),
	  long long b __attribute__ ((unused)))
{
  return 0LL;
}

long long
__adddi3_s8 (long long a __attribute__ ((unused)),
	     signed char b __attribute__ ((unused)))
{
  return 0LL;
}

long long
__ashldi3 (long long a __attribute__ ((unused)),
	   int b __attribute__ ((unused)))
{
  return 0LL;
}

long long
__ashrdi3 (long long a __attribute__ ((unused)),
	   int b __attribute__ ((unused)))
{
  return 0LL;
}

long
__bswapsi2 (long a __attribute__ ((unused)))
{
  return 0L;
}

int
__cmpdi2 (long long a __attribute__ ((unused)),
	  long long b __attribute__ ((unused)))
{
  return 0;
}

int
__cmpdi2_s8 (long long a __attribute__ ((unused)),
	     signed char b __attribute__ ((unused)))
{
  return 0;
}

long
__divmodhi4 (int a __attribute__ ((unused)),
	     int b __attribute__ ((unused)))
{
  return 0L;
}

long long
__divmodsi4 (long a __attribute__ ((unused)),
	     long b __attribute__ ((unused)))
{
  return 0LL;
}

long long
__lshrdi3 (long long a __attribute__ ((unused)),
	   int b __attribute__ ((unused)))
{
  return 0LL;
}

long
__mulshisi3 (long a __attribute__ ((unused)),
	     long b __attribute__ ((unused)))
{
  return 0L;
}

long long
__negdi2 (long long a __attribute__ ((unused)))
{
  return 0LL;
}

long long
__subdi3 (long long a __attribute__ ((unused)),
	  long long b __attribute__ ((unused)))
{
  return 0LL;
}

void
__tablejump2__(long long a __attribute__ ((unused)))
{
}

unsigned long
__udivmodhi4 (unsigned int a __attribute__ ((unused)),
	      unsigned int b __attribute__ ((unused)))
{
  return 0L;
}

unsigned long long
__udivmodsi4 (unsigned long a __attribute__ ((unused)),
	     unsigned long b __attribute__ ((unused)))
{
  return 0LL;
}

unsigned long
__usmulhisi3 (long a __attribute__ ((unused)),
	      unsigned long b __attribute__ ((unused)))
{
  return 0L;
}

unsigned long
__umulhisi3 (unsigned long a __attribute__ ((unused)),
	     unsigned long b __attribute__ ((unused)))
{
  return 0L;
}
#endif

#ifdef __arc__

#define HIDDEN_FUNC(name)			\
  void  __st_r13_to_ ## name			\
  (void)					\
  {						\
  }						\
  void  __ld_r13_to_ ## name			\
  (void)					\
  {						\
  }						\
  void  __ld_r13_to_ ## name ## _ret		\
  (void)					\
  {						\
  }

  HIDDEN_FUNC(r15)
  HIDDEN_FUNC(r16)
  HIDDEN_FUNC(r17)
  HIDDEN_FUNC(r18)
  HIDDEN_FUNC(r19)
  HIDDEN_FUNC(r20)
  HIDDEN_FUNC(r21)
  HIDDEN_FUNC(r22)
  HIDDEN_FUNC(r23)
  HIDDEN_FUNC(r24)
  HIDDEN_FUNC(r25)

#undef HIDDEN_FUNC
#endif /* __arc__ */

/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
