/* BEEBS arraysort benchmark

   This version, copyright (C) 2014-2019 Embecosm Limited and University of
   Bristol

   Contributor James Pallister <james.pallister@bristol.ac.uk>
   Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <string.h>
#include "support.h"
#include "sglib.h"

/* This scale factor will be changed to equalise the runtime of the
   benchmarks. */
#define LOCAL_SCALE_FACTOR 29

/* BEEBS heap is just an array */

#define HEAP_SIZE 8192
static char heap[HEAP_SIZE] __attribute__((aligned));

/* General array to sort for all ops */

static const int array[100] = {
  14, 66, 12, 41, 86, 69, 19, 77, 68, 38,
  26, 42, 37, 23, 17, 29, 55, 13, 90, 92,
  76, 99, 10, 54, 57, 83, 40, 44, 75, 33,
  24, 28, 80, 18, 78, 32, 93, 89, 52, 11,
  21, 96, 50, 15, 48, 63, 87, 20,  8, 85,
  43, 16, 94, 88, 53, 84, 74, 91, 67, 36,
  95, 61, 64,  5, 30, 82, 72, 46, 59,  9,
   7,  3, 39, 31,  4, 73, 70, 60, 58, 81,
  56, 51, 45,  1,  6, 49, 27, 47, 34, 35,
  62, 97,  2, 79, 98, 25, 22, 65, 71,  0
};

/* Array quicksort declarations */

int array2[100];

/* Doubly linked list declarations */

typedef struct dllist
{
  int i;
  struct dllist *ptr_to_next;
  struct dllist *ptr_to_previous;
} dllist;

#define DLLIST_COMPARATOR(e1, e2) (e1->i - e2->i)

SGLIB_DEFINE_DL_LIST_PROTOTYPES (dllist, DLLIST_COMPARATOR, ptr_to_previous,
				 ptr_to_next)
SGLIB_DEFINE_DL_LIST_FUNCTIONS (dllist, DLLIST_COMPARATOR, ptr_to_previous,
				ptr_to_next)

dllist *the_list;

/* Hash table declarations */

#define HASH_TAB_SIZE  20

typedef struct ilist
{
  int i;
  struct ilist *next;
} ilist;

ilist *htab[HASH_TAB_SIZE];

#define ILIST_COMPARATOR(e1, e2)    (e1->i - e2->i)

unsigned int
ilist_hash_function (ilist * e)
{
  return (e->i);
}

SGLIB_DEFINE_LIST_PROTOTYPES (ilist, ILIST_COMPARATOR, next)
SGLIB_DEFINE_LIST_FUNCTIONS (ilist, ILIST_COMPARATOR, next)
SGLIB_DEFINE_HASHED_CONTAINER_PROTOTYPES (ilist, HASH_TAB_SIZE,
					  ilist_hash_function)
SGLIB_DEFINE_HASHED_CONTAINER_FUNCTIONS (ilist, HASH_TAB_SIZE,
					 ilist_hash_function)

/* Queue declarations */

#define MAX_PARAMS 101

typedef struct iq
{
  int a[MAX_PARAMS];
  int i, j;
} iq;

SGLIB_DEFINE_QUEUE_FUNCTIONS (iq, int, a, i, j, MAX_PARAMS)

/* RB Tree declarations */

typedef struct rbtree
{
  int n;
  char color_field;
  struct rbtree *left;
  struct rbtree *right;
} rbtree;

#define CMPARATOR(x,y) ((x->n)-(y->n))

SGLIB_DEFINE_RBTREE_PROTOTYPES (rbtree, left, right, color_field, CMPARATOR)
SGLIB_DEFINE_RBTREE_FUNCTIONS (rbtree, left, right, color_field, CMPARATOR)


int
verify_benchmark (int res)
{
  static const int array_exp[100] = {
     0,  1,  2,  3,  4,  5,  6,  7,  8,  9,
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99
  };

  int i = 0;
  dllist *l;
  struct ilist ii, *nn;

  /* Doubly linked list check */

  for (l = sglib_dllist_get_first (the_list); l != NULL; l = l->ptr_to_next)
    {
      if (l->i != i)
	return 0;
      i++;
    }

  /* Hashtable check */

  for (i = 0; i < 100; i++)
    {
      ii.i = array[i];
      nn = sglib_hashed_ilist_find_member (htab, &ii);

      if ((nn == NULL) || (nn->i != array[i]))
	return 0;
    }

  return (15050 == res) && check_heap_beebs ((void *) heap)
    && (0 == memcmp (array2, array_exp, 100 * sizeof (array[0])));
}


void
initialise_benchmark (void)
{
}



static int benchmark_body (int  rpt);

void
warm_caches (int  heat)
{
  int  res = benchmark_body (heat);

  return;
}


int
benchmark (void)
{
  return benchmark_body (LOCAL_SCALE_FACTOR * CPU_MHZ);
}


static int __attribute__ ((noinline))
benchmark_body (int rpt)
{
  volatile int cnt;
  int i;

  for (i = 0; i < rpt; i++)
    {
      int i;
      dllist *l;
      struct ilist ii, *nn, *ll;
      struct sglib_hashed_ilist_iterator it;
      int ai, aj, n;
      int a[MAX_PARAMS];
      struct rbtree e, *t, *the_tree, *te;
      struct sglib_rbtree_iterator it2;

      /* Array quicksort */

      memcpy (array2, array, 100 * sizeof (array[0]));
      SGLIB_ARRAY_SINGLE_QUICK_SORT (int, array2, 100,
				     SGLIB_NUMERIC_COMPARATOR);

      /* Doubly linked list */

      init_heap_beebs ((void *) heap, HEAP_SIZE);
      the_list = NULL;

      for (i = 0; i < 100; ++i)
	{
	  l = malloc_beebs (sizeof (dllist));
	  l->i = array[i];
	  sglib_dllist_add (&the_list, l);
	}

      sglib_dllist_sort (&the_list);

      cnt = 0;

      for (l = sglib_dllist_get_first (the_list); l != NULL;
	   l = l->ptr_to_next)
	cnt++;

      /* Hash table */

      sglib_hashed_ilist_init (htab);

      for (i = 0; i < 100; i++)
	{
	  ii.i = array[i];
	  if (sglib_hashed_ilist_find_member (htab, &ii) == NULL)
	    {
	      nn = malloc_beebs (sizeof (struct ilist));
	      nn->i = array[i];
	      sglib_hashed_ilist_add (htab, nn);
	    }
	}

      for (ll = sglib_hashed_ilist_it_init (&it, htab);
	   ll != NULL; ll = sglib_hashed_ilist_it_next (&it))
	{
	  cnt++;
	}

      /* Queue */

      // echo parameters using a queue
      SGLIB_QUEUE_INIT (int, a, ai, aj);
      for (i = 0; i < 100; i++)
	{
	  n = array[i];
	  SGLIB_QUEUE_ADD (int, a, n, ai, aj, MAX_PARAMS);
	}
      while (!SGLIB_QUEUE_IS_EMPTY (int, a, ai, aj))
	{
	  cnt += SGLIB_QUEUE_FIRST_ELEMENT (int, a, ai, aj);
	  SGLIB_QUEUE_DELETE (int, a, ai, aj, MAX_PARAMS);
	}

      // print parameters in descending order
      SGLIB_HEAP_INIT (int, a, ai);
      for (i = 0; i < 100; i++)
	{
	  n = array[i];
	  SGLIB_HEAP_ADD (int, a, n, ai, MAX_PARAMS,
			  SGLIB_NUMERIC_COMPARATOR);
	}
      while (!SGLIB_HEAP_IS_EMPTY (int, a, ai))
	{
	  cnt += SGLIB_HEAP_FIRST_ELEMENT (int, a, ai);
	  SGLIB_HEAP_DELETE (int, a, ai, MAX_PARAMS,
			     SGLIB_NUMERIC_COMPARATOR);
	}

      /* RB Tree */

      the_tree = NULL;
      for (i = 0; i < 100; i++)
	{
	  e.n = array[i];
	  if (sglib_rbtree_find_member (the_tree, &e) == NULL)
	    {
	      t = malloc_beebs (sizeof (struct rbtree));
	      t->n = array[i];
	      sglib_rbtree_add (&the_tree, t);
	    }
	}

      for (te = sglib_rbtree_it_init_inorder (&it2, the_tree);
	   te != NULL; te = sglib_rbtree_it_next (&it2))
	{
	  cnt += te->n;
	}
    }

  return cnt;
}


/*
   Local Variables:
   mode: C
   c-file-style: "gnu"
   End:
*/
