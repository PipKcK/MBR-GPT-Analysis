all:
	cp main.py boot_info
	chmod +x boot_info
clean:
	rm boot_info
	rm SHA-256-gpt_sample.raw.txt
	rm MD5-gpt_sample.raw.txt