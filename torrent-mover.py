import shutil
import pathlib
import logging
import argparse
import bencodepy

DEBUG = False
PATH_KEYS = {
    # rTorrent
    '.rtorrent': [b'directory'],
    # qBittorrent
    '.fastresume': [b'qBt-savePath', b'save_path']
}

def create_backup(src_path: str, dst_path: str):
    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)

def list_session_files(sessions_path: pathlib.Path) -> list:
    files_to_process = []
    for entry in sessions_path.iterdir():
        if entry.is_file() and entry.suffix in PATH_KEYS:
            files_to_process.append(entry)

    return files_to_process

def process_file(file_path: pathlib.Path, src_path: str, dst_path: str) -> bool:
    src_path_encoded = src_path.encode('utf-8')
    dst_path_encoded = dst_path.encode('utf-8')

    with open(file_path, 'rb') as fp:
        data = fp.read()

    try:
        decoded_data = bencodepy.decode(data)
    except bencodepy.exceptions.BencodeDecodeError as e:
        logging.debug(f"[-] Bencode.py error: {e}")
        return False

    found = False
    for value in PATH_KEYS.values():
        for key in value:
            found = True
            break

    if not found:
        logging.debug("[-] Couldn't find any key in decoded data")
        return False

    if file_path.suffix not in PATH_KEYS:
        logging.debug("[-] Couldn't find src directory in decoded data")
        return False

    keys_to_change = PATH_KEYS[file_path.suffix]

    for key in keys_to_change:
        src_folder = decoded_data[key]
        if src_path_encoded not in src_folder:
            logging.debug("[-] Couldn't find src directory in decoded data")
            return True

        decoded_data[key] = decoded_data[key].replace(src_path_encoded, dst_path_encoded)

    logging.debug(f"[*] Changing folder from {src_path} to {dst_path}")

    try:
        encoded_data = bencodepy.encode(decoded_data)
    except bencodepy.exceptions.BencodeEncodeError as e:
        logging.debug(f"[-] Bencode.py error: {e}")
        return False

    with open(file_path, 'wb') as fp:
        fp.write(encoded_data)
    
    return True

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    if DEBUG:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    example_text = f"""Example:
python {pathlib.Path(__file__).name} --src /downloads/rTorrent/Temp/ --dst /downloads/rTorrent/Movies/ /config/rTorrent/session"""

    parser = argparse.ArgumentParser(add_help=False, epilog=example_text)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='')
    parser.add_argument('sessions_folder', type=str, help="This is the rTorrent sessions folder")
    parser.add_argument('--src', type=str, required=True, help="Set source path to change from")
    parser.add_argument('--dst', type=str, required=True, help="Set destination path to change to")
    parser.add_argument('--no-backup', default=False, action='store_true', help="Don't create a backup folder for sessions data")
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')
    args = parser.parse_args()

    if (args.src.endswith('/') and not args.dst.endswith('/')) or \
        (args.dst.endswith('/') and not args.src.endswith('/')):
        logging.error("[-] Make sure to set both src and dst with matching slashes")
        return

    # Check if folder exists
    sessions_path = pathlib.Path(args.sessions_folder)
    if not sessions_path.exists():
        logging.error("[-] Selected sessions folder doesn't exist")
        return

    # Find all session files
    files_to_process = list_session_files(sessions_path)

    # Check if files were found
    if len(files_to_process) == 0:
        logging.error("[-] No session files found. Are you sure you specified the sessions folder?")
        return

    input("[*] Please stop your torrent client (rTorrent / qBittorrent) instance before continuing! (Press any key)")

    if not args.no_backup:
        # Backup current directory
        logging.info(f"[*] Creating a backup for: {args.sessions_folder}")
        session_dirname = sessions_path.as_posix()

        # Let user decide if to overwrite an old backup
        if pathlib.Path(f'{session_dirname}_backup').exists():
            user_choice = input("[-] Backup folder already exists. Do you want to overwrite? [y/N] ")
            if user_choice.lower() == 'y':
                create_backup(session_dirname, f'{session_dirname}_backup')
                logging.info("[*] Backup created succesfully")
            else:
                logging.info("[*] Chose not to overwrite backup")
        else:
            create_backup(session_dirname, f'{session_dirname}_backup')
            logging.info("[*] Backup created succesfully")
    else:
        logging.info("[*] Skipping backup folder")

    # Process files
    logging.info("[*] Processing files..")
    for fn in files_to_process:
        logging.debug(f"[*] Processing file: {fn}")
        result = process_file(fn, args.src, args.dst)

        if result:
            logging.debug(f"[+] Processed succesfully: {fn}")
        else:
            logging.debug(f"[-] Problem processing: {fn}")

    logging.info("[*] Finished processing files")

if __name__ == "__main__":
    main()