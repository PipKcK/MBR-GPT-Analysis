#!/usr/bin/env python3

import hashlib
import os
import csv
import uuid
import sys

def calculate_hash(file_path, algorithm):
	h = hashlib.new(algorithm)
	with open(file_path, 'rb') as file:
		while True:
			chunk = file.read(h.block_size)
			if not chunk:
				break
			h.update(chunk)
	return h.hexdigest()

def create_hash(file_path):
	file_name = os.path.basename(file_path)
	
	md5_hash = calculate_hash(filepath, 'md5')
	sha256_hash = calculate_hash(filepath, 'sha256')
	
	f_md5 = open(f'MD5-{file_name}.txt', 'w')
	f_md5.write(md5_hash)
	f_md5.close()

	f_sha256 = open(f'SHA-256-{file_name}.txt', 'w')
	f_sha256.write(sha256_hash)
	f_sha256.close()
	
def check_partition_type(file_path):
    with open(file_path, 'rb') as file:
        mbr_signature = file.read(0x200)[-2:]
        gpt_signature = file.read(8)
    if mbr_signature == b'\x55\xAA' and gpt_signature == b'EFI PART':
        return "GPT"
    elif mbr_signature == b'\x55\xAA':
        return "MBR"
    elif gpt_signature == b'EFI PART':
        return "GPT"
    else:
        return None
        
def print_sector(file_path, start_sector, set='hex', offset=0):
    with open(file_path, 'rb') as file:
        file.seek(start_sector * 512 + int(offset))
        data = file.read(16)

        if set == 'hex':
            print(data.hex())
        elif set == 'ASCII':
            ascii_data = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
            print(ascii_data)

def get_value(key, filename='PartitionTypes.csv'):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == key:
                return f"({key}) {row[1]}"
	
def extract_partition_tables(file_path, partition_type, offset):
    partition_tables = []

    with open(file_path, 'rb') as file:
        if partition_type == "MBR":
            file.seek(0x1BE)

            for i in range(4):
                entry = file.read(16)
                partition_type = entry[4]
                start_address = int.from_bytes(entry[8:12], byteorder='little')
                num_sectors = int.from_bytes(entry[12:16], byteorder='little')

                partition_tables.append({
                    'type': partition_type,
                    'start_address': start_address,
                    'num_sectors': num_sectors
                })

            for table in partition_tables:
                print(get_value(f'{table["type"]:02X}'), end=", ")
                print(f'{table["start_address"]}, {table["num_sectors"]}')

            i = 1
            for table in partition_tables:
                if i < len(offset)+1:
                    print(f"Partition {i}:")
                    print(f"16 bytes of boot record from offset {offset[i-1]} :", end=" ")
                    print_sector(file_path, table["start_address"], "hex", offset[i-1])
                    print(f"ASCII :", end="\t\t\t\t         ")
                    print_sector(file_path, table["start_address"], "ASCII", offset[i-1])
                    i += 1
                else:
                    break

        elif partition_type == "GPT":
            for i in range(4):
                file.seek(0x400 + i * 128)

                entry = file.read(128)

                partition_type_guid = str(uuid.UUID(bytes=entry[0:16])).replace('-', '')
                start_address = int.from_bytes(entry[32:40], byteorder='little')
                end_address = int.from_bytes(entry[40:48], byteorder='little')
                partition_name = entry[56:128].decode('utf-16-le').rstrip('\x00')

                partition_tables.append({
                    'partition_number': i + 1,
                    'partition_type_guid': partition_type_guid,
                    'start_address_hex': f'0x{start_address:X}',
                    'end_address_hex': f'0x{end_address:X}',
                    'start_address_dec': start_address,
                    'end_address_dec': end_address,
                    'partition_name': partition_name
                })

            for table in partition_tables:
                print(f"Partition number: {table['partition_number']}")
                print(f"Partition Type GUID : {table['partition_type_guid']}")
                print(f"Starting LBA address in hex: {table['start_address_hex']}")
                print(f"Ending LBA address in hex: {table['end_address_hex']}")
                print(f"Starting LBA address in Decimal: {table['start_address_dec']}")
                print(f"Ending LBA address in Decimal: {table['end_address_dec']}")
                print(f"Partition name: {table['partition_name']}")
                print("")

    return partition_tables	

# Main Function

filepath = sys.argv[2]
offset = []
offset.extend([sys.argv[4], sys.argv[5], sys.argv[6]])

create_hash(filepath)

ptype = check_partition_type(filepath)

extract_partition_tables(filepath, ptype, offset)

