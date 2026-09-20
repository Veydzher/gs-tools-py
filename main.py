import argparse
from pathlib import Path

from src.gs.mdt_file import MdtFile


def main():
    parser = argparse.ArgumentParser(description="Gyakuten Saiban Data Manipulation Tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    decode_parser = subparsers.add_parser("decode", help="decode encrypted/decrypted .mdt file to .json file")
    decode_parser.add_argument("input_file", type=Path, help="Path to .mdt file")
    decode_parser.add_argument("--out", type=Path, help="output path for .json file")

    encode_parser = subparsers.add_parser("encode", help="encode .json file to encrypted/decrypted .mdt")
    encode_parser.add_argument("input_file", type=Path, help="Path to .json file")
    encode_parser.add_argument("--encrypt", action="store_true", help="whether to encrypt .mdt file")
    encode_parser.add_argument("--out", type=Path, help="output path for .mdt file")

    export_parser = subparsers.add_parser("export", help="export strings from .mdt/.json file to .csv file")
    export_parser.add_argument("input_file", type=Path, help="Path to .mdt/.json file")
    export_parser.add_argument("--out", type=Path, help="output path for .csv file")

    import_parser = subparsers.add_parser("import", help="import strings from .csv file to .mdt/.json file")
    import_parser.add_argument("input_csv", type=Path, help="Path to .csv file")
    import_parser.add_argument("input_file", type=Path, help="Path to .mdt/.json file")
    import_parser.add_argument("--encrypt", action="store_true", help="whether to encrypt .mdt file")
    import_parser.add_argument("--out", type=Path, help="output path for .mdt/.json file")

    args = parser.parse_args()

    match args.command:
        case "decode":
            out = (args.out if args.out is not None else args.input_file.with_suffix(".json")).resolve()

            mdt_file = MdtFile(args.input_file)
            mdt_file.decode()
            mdt_file.export_as_json(out)
            print(f"[CLI] Successfully exported as JSON: {out}")

        case "encode":
            out = (args.out if args.out is not None else args.input_file.with_suffix(".mdt")).resolve()

            mdt = MdtFile.build_from_json(args.input_file)
            mdt.encode(out, args.encrypt)

            if args.encrypt:
                print(f"[MDT] Successfully encoded and encrypted MDT file: {out}")
            else:
                print(f"[MDT] Successfully encoded MDT file: {out}")

        case "export":
            out = (args.out if args.out is not None else args.input_file.with_suffix(".csv")).resolve()
            suffix = args.input_file.suffix

            match suffix:
                case ".mdt":
                    mdt_file = MdtFile(args.input_file)
                    mdt_file.decode()
                    mdt_file.export_strings_to_csv(out)

                case ".json":
                    mdt_file = MdtFile.build_from_json(args.input_file)
                    mdt_file.export_strings_to_csv(out)

                case _:
                    raise ValueError(f"[CLI] Invalid input file's suffix: {suffix}")

            print(f"[CLI] Succesfully exported strings from {suffix.upper().lstrip('.')} file to CSV file: {out}")

        case "import":
            out = (args.out if args.out is not None else args.input_file).resolve()
            suffix = args.input_file.suffix

            match suffix:
                case ".mdt":
                    mdt_file = MdtFile(args.input_file)
                    mdt_file.decode()
                    mdt_file.import_strings_from_csv(args.input_csv)
                    mdt_file.encode(out, args.encrypt)

                case ".json":
                    mdt_file = MdtFile.build_from_json(args.input_file)
                    mdt_file.import_strings_from_csv(args.input_csv)
                    mdt_file.export_as_json(out)

                case _:
                    raise ValueError(f"[CLI] Invalid input file's suffix: {suffix}")

            print(f"[CLI] Succesfully imported strings from CSV file to {suffix.upper().lstrip('.')} file: {out}")

        case _:
            raise ValueError(f"[CLI] Invalid command: {args.command}")

if __name__ == "__main__":
    main()
