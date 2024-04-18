CFLAGS = -static -mcpu=cortex-m4 -mthumb -I./Include -DSTM32F407xx -O2
.PHONY: clean

libstartup.a: startup.out system.out
	arm-none-eabi-ar rcs $@ $^

startup.out: startup_stm32f407xx.s
	arm-none-eabi-gcc -c -o $@ $< $(CFLAGS)
system.out: system_stm32f4xx.c
	arm-none-eabi-gcc -c -o $@ $< $(CFLAGS)

clean:
	rm libstartup.a startup.out system.out
