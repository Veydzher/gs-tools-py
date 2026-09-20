import csv
import json
from pathlib import Path

from src.gs.classes import GSCodeProcToken, GSLabelToken, GSStringToken
from src.gs.crypto_file import CryptoFile
from src.gs.helpers import (
    CODE_PROCS,
    en_to_half,
    escape,
    get_token_size,
    half_to_en,
    resolve_byte_offset,
    resolve_position,
    unescape,
)
from src.utils.binary import BinaryReader, BinaryWriter


class MdtFile:
    def __init__(self, input_data: str | Path | None = None):
        if input_data is not None:
            self.reader = BinaryReader(input_data)

        self.messages: list[list] = []

    @property
    def file_path(self):
        return self.reader.file_path

    def is_encrypted(self):
        prev_pos = self.reader.position
        self.reader.seek(2)
        result = self.reader.u16() != 0
        self.reader.seek(prev_pos)
        return result

    @classmethod
    def from_file(cls, input_data: str | Path):
        obj = cls(input_data)
        obj.decode()
        return obj

    def decode(self):
        if self.is_encrypted():
            self.reader._stream = CryptoFile.decrypt(self.reader._stream)

        message_count = self.reader.u16()
        dummy = self.reader.u16()
        if dummy != 0:
            raise ValueError(f"dummy={dummy}... Something is wrong here...")

        message_offsets = [
            self.reader.u32()
            for _ in range(message_count)
        ]

        label_count = 0
        for idx in range(message_count-1):
            curr_off = message_offsets[idx]
            next_off = message_offsets[idx+1]
            if next_off < curr_off or next_off > self.reader.size or curr_off > self.reader.size:
                label_count = len(message_offsets[idx+1:])
                break

        message_count -= label_count

        # print(
        #     f"Number of messages: {message_count}\n"
        #     f"Number of labels: {label_count}\n"
        #     f"Total: {message_count + label_count}"
        # )

        message_sizes = [
            message_offsets[idx+1] - message_offsets[idx]
            for idx in range(message_count-1)
        ]

        message_sizes.append(self.reader.size - message_offsets[message_count - 1])

        for idx in range(message_count):
            self.reader.seek(message_offsets[idx])

            self.messages.append([])

            while self.reader.position < self.reader.size and self.reader.position - message_offsets[idx] < message_sizes[idx]:
                op = self.reader.u16()
                if op < 128:
                    code_proc = CODE_PROCS[op]
                    args = [
                        self.reader.u16()
                        for _ in range(code_proc.args_num)
                    ]
                    self.messages[idx].append(GSCodeProcToken(op, code_proc.name, args))
                else:
                    string = ""
                    while self.reader.position < self.reader.size and op >= 128:
                        op -= 128
                        string += op.to_bytes(4, "little").decode("utf-32-le")
                        op = self.reader.u16()

                    string = en_to_half(string)
                    self.messages[idx].append(GSStringToken(string))
                    if self.reader.position < self.reader.size:
                        self.reader.seek(-2, 1)

            for token in self.messages[idx]:
                if isinstance(token, GSCodeProcToken) and token.opcode == 0x35:
                    flag_word, raw_target = token.args
                    if not (flag_word & 0x80):  # bit 7 clear = local jump
                        target_u16_idx = raw_target // 2
                        tok_idx, tok_off = resolve_position(self.messages[idx], target_u16_idx)
                        token.local_jump_target_index = tok_idx
                        token.local_jump_token_offset = tok_off

        for idx in range(message_count, message_count + label_count):
            raw = message_offsets[idx]
            target_msg_no = raw >> 16
            raw_byte_offset = raw & 0xFFFF
            target_u16_idx = raw_byte_offset // 2

            target_token_idx = 0
            token_off = 0
            if target_msg_no < len(self.messages):
                target_token_idx, token_off = resolve_position(self.messages[target_msg_no], target_u16_idx)

            self.messages.append([GSLabelToken(target_msg_no, target_token_idx, token_off)])

        print(f"[MDT] Successfully decoded {self.file_path.name}!")

    def encode(self, out_path: str | Path | None = None, encrypt: bool = False):
        if not self.messages:
            print("[MDT] No messages to encode!")
            return

        if out_path is None:
            raise ValueError("[MDT] Provide valid path to MDF file for encoding!")

        if not isinstance(out_path, Path):
            out_path = Path(out_path)

        bw = BinaryWriter()
        bw.u16(len(self.messages))
        bw.u16(0)

        labels = [[entry] for msg in self.messages for entry in msg if isinstance(entry, GSLabelToken)]
        message_count = len(self.messages)

        # Write Messages Offsets
        file_msg_offset = bw.position + (message_count * 4)
        if message_count > 0:
            bw.u32(file_msg_offset)

        message_count -= len(labels)

        last_offset = file_msg_offset
        for msg in self.messages[:message_count - 1]:
            message_size = 0
            for token in msg:
                size = get_token_size(token) * 2
                message_size += size

            last_offset += message_size
            bw.u32(last_offset)

        # Write Labels Offsets
        for label in labels:
            for token in label:
                byte_offset = 0
                if token.target_msg_index < len(self.messages):
                    target_tokens = self.messages[token.target_msg_index]
                    byte_offset = resolve_byte_offset(
                        target_tokens, token.target_token_index, token.target_token_offset
                    )

                packed = (token.target_msg_index << 16) | byte_offset
                bw.u32(packed)

        # Write Data
        for msg in self.messages:
            for token in msg:
                match token:
                    case GSStringToken():
                        converted = half_to_en(unescape(token.value))
                        for chr in converted:
                            int_chr = int.from_bytes(chr.encode("utf-32-le"), "little")
                            encoded_chr = int_chr + 128
                            bw.u16(encoded_chr)

                    case GSCodeProcToken():
                        bw.u16(token.opcode)
                        if token.opcode == 0x35 and token.local_jump_target_index is not None:
                            flag_word = token.args[0]
                            u16_pos = 0
                            for t in msg[:token.local_jump_target_index]:
                                u16_pos += get_token_size(t)
                            u16_pos += token.local_jump_token_offset
                            bw.u16(flag_word)
                            bw.u16(u16_pos * 2)
                        else:
                            for arg in token.args:
                                bw.u16(arg)

        out_data = bw.getvalue()
        if encrypt:
            out_data = CryptoFile.encrypt(out_data)

        out_path.write_bytes(out_data)

    def export_as_json(self, out_path: str | Path | None = None, debug=False):
        if not self.messages:
            print("[MDT] No messages to export!")
            return

        if out_path is None:
            out_path = self.file_path.with_suffix(".json")

        if not isinstance(out_path, Path):
            out_path = Path(out_path)

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as jf:
                if not debug:
                    result = []
                    for msg in self.messages:
                        message = []
                        for entry in msg:
                            message.append(entry.to_json())
                        result.append(message)
                else:
                    result = {}
                    for idx, msg in enumerate(self.messages):
                        result.setdefault(idx, [])
                        if debug:
                            for e_idx, entry in enumerate(msg):
                                result[idx].append({e_idx: entry.to_json()})
                        else:
                            for entry in msg:
                                result[idx].append(entry.to_json())

                json.dump(result, jf, ensure_ascii=False, indent=2)
        except Exception as exc:
            raise exc from exc

    @classmethod
    def build_from_json(cls, in_path: str | Path | None = None, is_debug: bool = False):
        if in_path is None:
            raise ValueError("[MDT] Provide a valid path to JSON file!")

        if not isinstance(in_path, Path):
            in_path = Path(in_path)

        defined_types = {
            "GSCodeProcToken": lambda **kwargs: GSCodeProcToken(**kwargs),
            "GSStringToken": lambda **kwargs: GSStringToken(**kwargs),
            "GSLabelToken": lambda **kwargs: GSLabelToken(**kwargs),
        }

        mdt = MdtFile()

        try:
            with in_path.open(encoding="utf-8") as js:
                json_data = json.load(js)

                mdt.messages = []
                if not is_debug:
                    for idx, msg in enumerate(json_data):
                        mdt.messages.append([])
                        for entry in msg:
                            obj = defined_types[entry["$type"]]
                            new = obj(**{k: v for k, v in entry.items() if k != "$type"})
                            mdt.messages[idx].append(new)
                else:
                    for idx, msg in json_data.items():
                        mdt.messages.append([])
                        for idx, entry in msg.items():
                            obj = defined_types[entry["$type"]]
                            new = obj(**{k: v for k, v in entry.items() if k != "$type"})
                            mdt.messages[idx].append(new)

            return mdt
        except Exception as exc:
            raise exc from exc

    def export_strings_to_csv(self, csv_path: str | Path | None = None):
        if csv_path is None:
            csv_path = Path(self.file_path.with_suffix(".csv"))
        elif not isinstance(csv_path, Path):
            csv_path = Path(csv_path)

        if csv_path.stem == ".":
            raise ValueError("[MDT] Enter valid output csv file path!")

        contents = []
        for m_idx, msg in enumerate(self.messages):
            for t_idx, token in enumerate(msg):
                if isinstance(token, GSStringToken):
                    contents.append((f"{m_idx}.{t_idx}", token.value))

        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["ID", "Source string", "Translation"],
                quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            for c in contents:
                writer.writerow({
                    "ID": c[0],
                    "Source string": c[1],
                    "Translation": ""
                })

        return len(contents)

    def import_strings_from_csv(self, csv_path):
        translations = {}
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                idx = row["ID"]
                source = row["Source string"]
                translation = row["Translation"]
                translations[idx] = translation if translation != "" else source

        count = 0
        for i, new_content in translations.items():
            m_idx, t_idx = tuple(map(int, i.split(".")))
            if m_idx < len(self.messages):
                msg = self.messages[m_idx]
                if t_idx < len(msg):
                    token = msg[t_idx]
                    if isinstance(token, GSStringToken):
                        token.value = new_content
                        count += 1
                    else:
                        print(f"[MDT] Found no GSStringToken at {i}!")

        return count
