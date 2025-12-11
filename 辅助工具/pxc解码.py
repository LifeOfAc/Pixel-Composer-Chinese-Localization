import zlib
import json
import os
import sys

def extract_json_from_pxc(input_file):
    with open(input_file, 'rb') as f:
        buffer = f.read()

    zlib_start = buffer.find(b'\x78\x9C')
    zlib_end = len(buffer)
    for i in range(len(buffer) - 1, zlib_start, -1):
        if buffer[i] != 0x00:
            zlib_end = i + 1
            break
    compressed_data = buffer[zlib_start:zlib_end]
    try:
        decompressed = zlib.decompress(compressed_data)
    except zlib.error as e:
        raise ValueError(f"zlib解压失败: {e}")
    clean_data = decompressed.decode('utf-8', errors='ignore').rstrip('\x00')
    json_data = json.loads(clean_data)
    file_dir, file_name = os.path.split(input_file)
    name_without_ext = os.path.splitext(file_name)[0]
    output_file = os.path.join(file_dir, name_without_ext + '.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"JSON已保存到: {output_file}")

if __name__ == "__main__":
    extract_json_from_pxc(sys.argv[1] if len(sys.argv) > 1 else './黑色.pxc')