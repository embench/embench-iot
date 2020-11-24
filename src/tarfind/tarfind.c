/*
 * This benchmark simulates the search in a TAR archive
 * for a set of filenames
 *
 * Created by Julian Kunkel for Embench-iot
 * Licensed under MIT
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#include "support.h"

#define LOCAL_SCALE_FACTOR 10

// number of files in the archive
#define ARCHIVE_FILES 100

/* BEEBS heap is just an array */
#define HEAP_SIZE 25700
static char heap[HEAP_SIZE];

void
initialise_benchmark (void)
{
}


static int benchmark_body (int rpt);

void
warm_caches (int  heat)
{
  benchmark_body (heat);
  return;
}


int
benchmark (void)
{
  return benchmark_body (LOCAL_SCALE_FACTOR * CPU_MHZ);
}

// this is the basic TAR header format which is in ASCII
typedef struct {
  char filename[100];
  char mode[8];  // file mode
  char uID[8];   // user id
  char gID[8];   // group id
  char size[12]; // in bytes octal base
  char mtime[12]; // numeric Unix time format (octal)
  char checksum[8]; // for the header, ignored herew2
  char isLink;
  char linkedFile[100];
} tar_header_t;


static int __attribute__ ((noinline))
benchmark_body (int rpt)
{
  int i;
  int p;

  init_heap_beebs ((void *) heap, HEAP_SIZE);

  // always create 100 files in the archive
  int files = 100;
  tar_header_t * hdr = malloc_beebs(sizeof(tar_header_t) * files);
  for (i = 0; i < files; i++){
    // create record
    tar_header_t * c = & hdr[i];
    // initialize here for cache efficiency reasons
    memset(c, 0, sizeof(tar_header_t));
    int flen = 5 + i % 94; // vary file lengths
    c->isLink = '0';
    for(p = 0; p < flen; p++){
      c->filename[p] = rand_beebs() % 26 + 65;
    }
    c->size[0] = '0';
  }

  int found = 0; // number of times a file was found
  // actual benchmark, strcmp with a set of rpt files
  // the memory access here is chosen inefficiently on purpose
  for (p = 0; p < rpt; p++){
    // chose the position of the file to search for from the mid of the list
    char * search = hdr[(p + ARCHIVE_FILES/2) % ARCHIVE_FILES].filename;

    // for each filename iterate through all files until found
    for (i = 0; i < files; i++){
      tar_header_t * cur = & hdr[i];
      // implementation of strcmp
      char *c1;
      char *c2;
      for (c1 = hdr[i].filename, c2 = search; (*c1 != '\0' && *c2 != '\0' && *c1 == *c2) ; c1++, c2++);
      // complete match?
      if(*c1 == '\0' && *c2 == '\0'){
        // printf("Found: %s = %s\n", search, hdr[i].filename);
        found++;
        break;
      }
    }
  }

  free_beebs(hdr);

  return found == rpt;
}


int
verify_benchmark (int r)
{
  return r == 1;
}
