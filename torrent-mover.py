import shutil
import pathlib
import logging
import argparse
import bencodepy

def create_backup(src_path: str, dst_path: str):
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)

def list_rtorrent_files(src_path: pathlib.Path) -> list:
    files_to_process = []
    for entry in src_path.iterdir():
        if entry.is_file() and entry.suffix == '.rtorrent':
            files_to_process.append(entry)

    return files_to_process

def process_file(file_path: pathlib.Path, src_path: str, dst_path: str = "/test") -> bool:
    bencode_decoder = bencodepy.Bencode(encoding='utf-8')
    with open(file_path, 'rb') as fp:
        data = fp.read()

    try:
        decoded_data = bencode_decoder.decode(data)
    except bencodepy.exceptions.BencodeDecodeError as e:
        logging.debug(f"[-] Bencode.py error: {e}")
        return False
    
    if 'directory' not in decoded_data:
        logging.debug("[-] Couldn't find directory in decoded data")
        return False

    src_folder = decoded_data['directory']
    if src_path not in src_folder:
        logging.debug("[-] Couldn't find src directory in decoded data")
        return True

    decoded_data['directory'] = decoded_data['directory'].replace(src_path, dst_path)
    logging.debug(f"[*] Changing folder from {src_path} to {dst_path}")

    try:
        encoded_data = bencode_decoder.encode(decoded_data)
    except bencodepy.exceptions.BencodeEncodeError as e:
        logging.debug(f"[-] Bencode.py error: {e}")
        return False

    with open(file_path, 'wb') as fp:
        fp.write(encoded_data)
    
    return True

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=str, required=True)
    args = parser.parse_args()

    # Backup current directory
    logging.info(f"[*] Creating a backup for: {args.folder}")
    src_path = pathlib.Path(args.folder)
    src_dir = src_path.as_posix()
    create_backup(src_dir, f'{src_dir}_backup')
    logging.info("[*] Backup created succesfully")

    # Find all .rtorrent files
    files_to_process = list_rtorrent_files(src_path)

    # Process files
    for fn in files_to_process:
        logging.debug(f"[*] Processing file: {fn}")
        result = process_file(fn, '/downloads/rTorrent')

        if result:
            logging.debug(f"[+] Processed succesfully: {fn}")
        else:
            logging.debug(f"[-] Problem processing: {fn}")

if __name__ == "__main__":
    main()