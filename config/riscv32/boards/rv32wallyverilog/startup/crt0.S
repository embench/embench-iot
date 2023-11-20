.section ".text.start"
.globl _start
_start:

.option push
.option norelax
  la gp, __global_pointer$
.option pop

  // enable floating-point
  li t0, 0x2000
  csrs mstatus, t0  // mstatus.FS = 01 to enable floating-point

  // set the thread pointer
  la  tp, _end + 63
  and tp, tp, -64

  // set the stack pointer 128k
  li t0, 0x0002000
  add sp, tp, t0

  la t0, __bss_start
  andi t1, t0, 3 # skips initializing .bss if its not aligned
  bne t1, zero, bssdone
  la t1, __BSS_END__

bssinit: #initializing .bss section to zeros
  sw x0, 0(t0)
  addi t0, t0, 4
  blt t0, t1, bssinit
bssdone:
  jal main

  .align 2

.global write_tohost
write_tohost:
    la t2, begin_signature
    lw t3, startcycle 
    lw t4, stopcycle
    lw t5, startinst
    lw t6, stopinst
    sw t3, 0(t2)
    sw t4, 4(t2)
    sw t5, 8(t2)
    sw t6, 12(t2)
    la t1, tohost
    slli a0, a0, 1 # 1 for success, 3 for failure
    addi t0, a0, 1
    sw t0, 16(t2)      # put the success code in the signature      
    sw t0, 0(t1)        # send success code tohost

self_loop:
    j self_loop         # wait

.global stop_trigger
stop_trigger:
  la t2, stopcycle
  j record_trigger

.global start_trigger
start_trigger:
  la t2, startcycle

record_trigger:
  csrr t0, mcycle
  csrr t1, minstret
  sw t0, 0(t2)
  sw t1, 4(t2)
  ret

.data
startcycle: .word 0
startinst: .word 0
stopcycle: .word 0
stopinst: .word 0

.section ".tohost"
.align 6
.globl tohost
tohost: .dword 0
.align 6
.globl fromhost
fromhost: .dword 0
.align 6
.globl begin_signature
begin_signature: .dword 0
    .fill 4,3,0x00000000  #initiate as zero  
end_signature: .dword 0

# Initialize stack with room for 512 bytes
.bss
    .space 512
topofstack:
