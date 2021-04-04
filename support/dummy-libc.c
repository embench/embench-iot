/* Dummy standard C library for the benchmarks

   Copyright (C) 2018-2019 Embecosm Limited

   Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

/* The purpose of this library is to measure the size of code excluding target
   dependent C library code. It only makes sense if it is used with
   -gc-sections. */

#include <time.h>
#include <stdio.h>

/* Avoid conflict with ferror defined as a macro, which is the case on some
   systems.  */
#ifdef ferror
#undef ferror
#endif


void *__locale_ctype_ptr;

int __errno;

char *_ctype_;
char *__ctype_ptr__;

struct _reent *_impure_ptr;

void __attribute__ ((noreturn))
abort (void)
{
  while (1)
    ;
}


void *
memcpy (void *dest __attribute__ ((unused)),
	const void *src __attribute__ ((unused)),
	size_t n __attribute__ ((unused)))
{
  return 0;
}


void *
memmove (void *dest __attribute__ ((unused)),
	 const void *src __attribute__ ((unused)),
	 size_t n __attribute__ ((unused)))
{
  return 0;
}


void *
memset (void *s __attribute__ ((unused)),
	int c __attribute__ ((unused)),
	size_t n __attribute__ ((unused)))
{
  return 0;
}

int
memcmp (const void *s1 __attribute__ ((unused)),
	const void *s2 __attribute__ ((unused)),
	size_t n __attribute__ ((unused)))
{
  return 0;
}


int
rand (void)
{
  return 0;
}


void
srand (unsigned int seed __attribute__ ((unused)))
{
}


void *
calloc (size_t nmemb __attribute__ ((unused)),
	size_t size __attribute__ ((unused)))
{
  return 0;
}


void *
malloc (size_t size __attribute__ ((unused)))
{
  return 0;
}


void
free (void *ptr __attribute__ ((unused)))
{
}


void __attribute__ ((noreturn))
__assert_func (const char *arg1 __attribute__ ((unused)),
	       int arg2 __attribute__ ((unused)),
	       const char *arg3 __attribute__ ((unused)),
	       const char *arg4 __attribute__ ((unused)))
{
  while (1)
    ;
}

size_t
strlen (const char *s __attribute__ ((unused)))
{
  return 0;
}


char *
strcpy (char *dest __attribute__ ((unused)),
	const char *src __attribute__ ((unused)))
{
  return 0;
}


char *
strchr (const char *s __attribute__ ((unused)),
	int c __attribute__ ((unused)))
{
  return 0;
}


long int
strtol (const char *nptr __attribute__ ((unused)),
	char **endptr __attribute__ ((unused)),
	int base __attribute__ ((unused)))
{
  return 0;
}


int
strcmp (const char *s1 __attribute__ ((unused)),
	const char *s2 __attribute__ ((unused)))
{
  return 0;
}

int
strncmp (const char *s1 __attribute__ ((unused)),
	 const char *s2, __attribute__ ((unused))
	 size_t n __attribute__ ((unused)))
{
  return 0;
}

char *
strcat (char *dest __attribute__ ((unused)),
	const char *src __attribute__ ((unused)))
{
  return 0;
}

int
printf (const char *format __attribute__ ((unused)), ...)
{
  return 0;
}

int
fprintf (FILE * stream __attribute__ ((unused)),
	 const char *format __attribute__ ((unused)), ...)
{
  return 0;
}

int
sprintf (char *str __attribute__ ((unused)),
	 const char *format __attribute__ ((unused)), ...)
{
  return 0;
}

#ifdef putchar
#undef putchar
#endif
int
putchar (int c __attribute__ ((unused)))
{
  return 0;
}


int
puts (const char *s __attribute__ ((unused)))
{
  return 0;
}

clock_t
clock (void)
{
  return (clock_t) 0;
}

int
atoi (const char *nptr __attribute__ ((unused)))
{
  return 0;
}

double
atof (const char *nptr __attribute__ ((unused)))
{
  return 0.0;
}

FILE *
fopen (const char *pathname __attribute__ ((unused)),
       const char *mode __attribute__ ((unused)))
{
  return NULL;
}

/* AVR defines a dummy version in the header already */
#ifndef __AVR__
int
fflush (FILE * stream __attribute__ ((unused)))
{
  return 0;
}
#endif

int
ferror (FILE * stream __attribute__ ((unused)))
{
  return 0;
}

int
fileno (FILE * stream __attribute__ ((unused)))
{
  return 0;
}

int
fscanf (FILE * stream __attribute__ ((unused)),
	const char *format __attribute__ ((unused)), ...)
{
  return 0;
}

int
sscanf (const char *str __attribute__ ((unused)),
	const char *format __attribute__ ((unused)), ...)
{
  return 0;
}

void
qsort (void *base __attribute__ ((unused)),
       size_t nmemb __attribute__ ((unused)),
       size_t size __attribute__ ((unused)),
       int (*compar) (const void *, const void *) __attribute__ ((unused)))
{
}

int
fgetc (FILE * stream __attribute__ ((unused)))
{
  return 0;
}

#ifdef getc
#undef getc
#endif
int
getc (FILE * stream __attribute__ ((unused)))
{
  return 0;
}

int
ungetc (int c, FILE * stream __attribute__ ((unused)))
{
  return 0;
}

int
fputc (int ch __attribute__ ((unused)),
       FILE * stream __attribute__ ((unused)))
{
  return 0;
}

#ifdef putc
#undef putc
#endif
int
putc (int ch __attribute__ ((unused)), FILE * stream __attribute__ ((unused)))
{
  return 0;
}

char *
fgets (char *s __attribute__ ((unused)),
       int size __attribute__ ((unused)),
       FILE * stream __attribute__ ((unused)))
{
  return NULL;
}

int
fclose (FILE * stream __attribute__ ((unused)))
{
  return 0;
}

size_t
fwrite (const void *ptr __attribute__ ((unused)),
	size_t size __attribute__ ((unused)),
	size_t nmemb __attribute__ ((unused)),
	FILE * stream __attribute__ ((unused)))
{
  return 0;
}

int
fputs (const char *s __attribute__ ((unused)),
       FILE * stream __attribute__ ((unused)))
{
  return 0;
}

size_t
fread (void *ptr __attribute__ ((unused)),
       size_t size __attribute__ ((unused)),
       size_t nmemb __attribute__ ((unused)),
       FILE * stream __attribute__ ((unused)))
{
  return 0;
}

void __attribute__ ((noreturn)) exit (int status __attribute__ ((unused)))
{
  while (1);
}

char *
getenv (const char *name __attribute__ ((unused)))
{
  return 0;
}

void *
memchr (const void *s __attribute__ ((unused)),
	int c __attribute__ ((unused)), size_t n __attribute__ ((unused)))
{
  return 0;
}

unsigned short int **
__ctype_b_loc (void)
{
  return 0;
}

unsigned short int **
__ctype_tolower_loc (void)
{
  return 0;
}

int
tolower (int c __attribute__ ((unused)))
{
  return 0;
}

/* Extra bits just for AVR */
#ifdef __AVR__

int
isspace (int c __attribute__ ((unused)))
{
  return 0;
}

int
isxdigit (int c __attribute__ ((unused)))
{
  return 0;
}

#endif

/* Extra bits just for ARM */
#ifdef __arm__

void
__aeabi_memclr4 (void *dest __attribute__ ((unused)),
		 size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memclr8 (void *dest __attribute__ ((unused)),
		 size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memclr (void *dest __attribute__ ((unused)),
		size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memcpy4 (void *dest __attribute__ ((unused)),
		 const void *source __attribute__ ((unused)),
		 size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memcpy (void *dest __attribute__ ((unused)),
		const void *source __attribute__ ((unused)),
		size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memmove4 (void *dest __attribute__ ((unused)),
		  const void *source __attribute__ ((unused)),
		  size_t n __attribute__ ((unused)))
{
}

void
__aeabi_memmove (void *dest __attribute__ ((unused)),
		 const void *source __attribute__ ((unused)),
		 size_t n __attribute__ ((unused)))
{
}

#endif /* __arm__ */

/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
