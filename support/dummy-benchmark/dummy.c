#define MAGIC 0xBE
void
initialise_benchmark (void)
{
}



void
warm_caches (int  heat)
{
}


int
benchmark (void)
{
  return MAGIC;
}


int
verify_benchmark (int r)
{
  return r == MAGIC;
}
#undef MAGIC