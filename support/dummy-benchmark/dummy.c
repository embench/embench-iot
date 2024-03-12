#define MAGIC 0xBE
void __attribute__ ((noinline))
initialise_benchmark (void)
{
}



void __attribute__ ((noinline))
warm_caches (int  heat)
{
}


int __attribute__ ((noinline))
benchmark (void)
{
  return MAGIC;
}


int __attribute__ ((noinline))
verify_benchmark (int r)
{
  return r == MAGIC;
}
#undef MAGIC