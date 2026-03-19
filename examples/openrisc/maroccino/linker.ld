INCLUDE generated/output_format.ld
INCLUDE generated/regions.ld

ENTRY(_start)


SECTIONS
{
	.text :
	{
		_ftext = .;
                /* Make sure crt0 files come first, and they, and the isr */
                /* don't get disposed of by greedy optimisation */
                *crt0*(.text)
                KEEP(*crt0*(.text))
                KEEP(*(.text.isr))

		*(.text .stub .text.* .gnu.linkonce.t.*)
		_etext = .;
	} > main_ram

	.rodata : ALIGN(8)
	{
		_frodata = .;
		*(.rodata .rodata.* .gnu.linkonce.r.*)
		*(.rodata1)
		*(.got .got.*)
		*(.toc .toc.*)

		/* Make sure the file is aligned on disk as well
		   as in memory; CRC calculation requires that. */
		FILL(0);
		. = ALIGN(8);
		_erodata = .;
	} > main_ram

	.commands : ALIGN(8)
	{
		PROVIDE_HIDDEN (__bios_cmd_start = .);
		KEEP(*(.bios_cmd))
		PROVIDE_HIDDEN (__bios_cmd_end = .);
	} > main_ram 

	.data : ALIGN(8)
	{
		_fdata = .;
		*(.data .data.* .gnu.linkonce.d.*)
		*(.data1)
		*(.sdata .sdata.* .gnu.linkonce.s.*)

		/* Make sure the file is aligned on disk as well
		   as in memory; CRC calculation requires that. */
		FILL(0);
		. = ALIGN(8);
		_edata = .;
	} > main_ram

	.bss : ALIGN(8) SUBALIGN(8)
	{
		_fbss = .;
		*(.dynsbss)
		*(.sbss .sbss.* .gnu.linkonce.sb.*)
		*(.scommon)
		*(.dynbss)
		*(.bss .bss.* .gnu.linkonce.b.*)
		*(COMMON)
		. = ALIGN(8);
		_ebss = .;
		_end = .;
	} > main_ram
	. = ALIGN(8);
	PROVIDE(__heap_start = . );

	/DISCARD/ :
	{
		*(.eh_frame)
		*(.comment)
	}
}

PROVIDE(__heap_end = ORIGIN(main_ram) + LENGTH(main_ram));

PROVIDE(_fstack = ORIGIN(sram) + LENGTH(sram));

PROVIDE(_fdata_rom = LOADADDR(.data));
PROVIDE(_edata_rom = LOADADDR(.data) + SIZEOF(.data));
