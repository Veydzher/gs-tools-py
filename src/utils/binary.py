from __future__ import annotations

import struct
from pathlib import Path

_ENDIANS = {"little": "<", "big": ">"}
_LENGTH_PREFIXES = ("s8", "u8", "s16", "u16", "s32", "u32", "s64", "u64")


class BinaryIOBase:
    def __init__(self, endian: str = "little"):
        self.endian = endian

    @property
    def endian(self) -> str:
        return self._endian_name

    @endian.setter
    def endian(self, value: str):
        if value not in _ENDIANS:
            raise ValueError(f"Invalid endian {value!r}; expected 'little' or 'big'")
        self._endian_name = value

    @property
    def order(self) -> str:
        return _ENDIANS[self._endian_name]


class BinaryReader(BinaryIOBase):
    def __init__(self, data: str | Path | bytes | bytearray, endian: str = "little"):
        super().__init__(endian)

        if isinstance(data, (bytes, bytearray)):
            self._stream = bytearray(data)
            self.file_path: Path | None = None
        elif isinstance(data, (str, Path)):
            path = data if isinstance(data, Path) else Path(data)
            try:
                self._stream = bytearray(path.read_bytes())
            except FileNotFoundError:
                raise FileNotFoundError(f"The following file not found!\n{path}") from None
            self.file_path = path

        self._position = 0

    def __len__(self) -> int:
        return len(self._stream)

    def __repr__(self) -> str:
        return f"BinaryReader(size={len(self._stream)}, position={self._position=}, endian={self.endian!r})"

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return None

    # -- position / bounds ---------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._stream)

    @property
    def remaining(self) -> int:
        return len(self._stream) - self._position

    @property
    def eof(self) -> bool:
        return self._position >= len(self._stream)

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        if not 0 <= value <= len(self._stream):
            raise ValueError(f"Invalid stream position {value}; must be between 0 and {len(self._stream)}")
        self._position = value

    def tell(self) -> int:
        return self._position

    def seek(self, value: int, whence: int = 0) -> int:
        if whence == 0:
            self.position = value
        elif whence == 1:
            self.position = self._position + value
        elif whence == 2:
            self.position = len(self._stream) - value
        else:
            raise ValueError("Invalid `whence` value! Should be in range 0-2.")
        return self._position

    def skip(self, size: int):
        self.position += size

    def align(self, alignment: int):
        if alignment <= 0:
            raise ValueError("alignment must be positive")
        self.skip((-self._position) % alignment)

    def peek(self, size: int) -> bytes:
        start = self._position
        data = self.read(size)
        self._position = start
        return data

    # -- raw bytes ------------------------------------------------------------

    def read(self, size: int) -> bytes:
        if size < 0:
            raise ValueError(f"Invalid `size` value! {size=}")
        end = self._position + size
        if end > len(self._stream):
            raise ValueError(
                f"Cannot read {size} bytes at position {self._position}: "
                f"only {self.remaining} byte(s) remaining"
            )
        data = bytes(self._stream[self._position:end])
        self._position = end
        return data

    def read_all(self) -> bytes:
        return self.read(self.remaining)

    # -- fixed-width scalars ---------------------------------------------------

    def _unpack(self, fmt_char: str):
        size = struct.calcsize(fmt_char)
        end = self._position + size
        if end > len(self._stream):
            raise ValueError(
                f"Cannot read {size} byte(s) at position {self._position}: "
                f"only {self.remaining} byte(s) remaining"
            )
        value = struct.unpack_from(
            self.order + fmt_char, buffer=self._stream, offset=self._position
        )[0]
        self._position = end
        return value

    def s8(self) -> int:
        return self._unpack("b")

    def u8(self) -> int:
        return self._unpack("B")

    def s16(self) -> int:
        return self._unpack("h")

    def u16(self) -> int:
        return self._unpack("H")

    def s32(self) -> int:
        return self._unpack("i")

    def u32(self) -> int:
        return self._unpack("I")

    def s64(self) -> int:
        return self._unpack("q")

    def u64(self) -> int:
        return self._unpack("Q")

    def f32(self) -> float:
        return self._unpack("f")

    def f64(self) -> float:
        return self._unpack("d")

    # -- arrays of fixed-width scalars -----------------------------------------

    def _unpack_array(self, fmt_char: str, count: int) -> tuple:
        if count < 0:
            raise ValueError(f"Invalid `count` value! {count}")
        if count == 0:
            return ()
        size = struct.calcsize(fmt_char) * count
        end = self._position + size
        if end > len(self._stream):
            raise ValueError(
                f"Cannot read {count} x {fmt_char!r} at position {self._position}: "
                f"only {self.remaining} byte(s) remaining"
            )
        values = struct.unpack_from(
            f"{self.order}{count}{fmt_char}", buffer=self._stream, offset=self._position
        )
        self._position = end
        return values

    def s8_array(self, count: int) -> tuple:
        return self._unpack_array("b", count)

    def u8_array(self, count: int) -> tuple:
        return self._unpack_array("B", count)

    def s16_array(self, count: int) -> tuple:
        return self._unpack_array("h", count)

    def u16_array(self, count: int) -> tuple:
        return self._unpack_array("H", count)

    def s32_array(self, count: int) -> tuple:
        return self._unpack_array("i", count)

    def u32_array(self, count: int) -> tuple:
        return self._unpack_array("I", count)

    def s64_array(self, count: int) -> tuple:
        return self._unpack_array("q", count)

    def u64_array(self, count: int) -> tuple:
        return self._unpack_array("Q", count)

    def f32_array(self, count: int) -> tuple:
        return self._unpack_array("f", count)

    def f64_array(self, count: int) -> tuple:
        return self._unpack_array("d", count)


    # -- strings ----------------------------------------------------------------

    def cstring(self, encoding: str = "utf-8") -> str:
        start = self._position
        idx = self._stream.find(b"\x00", start)
        if idx == -1:
            raise ValueError("Unterminated string: no null byte before end of stream")
        data = bytes(self._stream[start:idx])
        self._position = idx + 1
        return data.decode(encoding)

    def fixed_string(self, size: int, encoding: str = "utf-8", strip_null: bool = True) -> str:
        data = self.read(size)
        if strip_null:
            data = data.split(b"\x00", 1)[0]
        return data.decode(encoding)

    def pascal_string(self, length_type: str = "u8", encoding: str = "utf-8") -> str:
        if length_type not in _LENGTH_PREFIXES:
            raise ValueError(f"length_type must be one of {_LENGTH_PREFIXES}")
        length = getattr(self, length_type)()
        return self.read(length).decode(encoding)


class BinaryWriter(BinaryIOBase):
    def __init__(self, endian: str = "little", data: bytes | bytearray = b""):
        super().__init__(endian)
        self._stream = bytearray(data)
        self._position = 0

    def __len__(self) -> int:
        return len(self._stream)

    def __repr__(self) -> str:
        return f"BinaryWriter(size={len(self._stream)}, position={self._position=}, endian={self.endian!r})"

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return None

    # -- position / bounds ---------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._stream)

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value: int):
        if not 0 <= value <= len(self._stream):
            raise ValueError(f"Invalid stream position {value}; must be between 0 and {len(self._stream)}")
        self._position = value

    def tell(self) -> int:
        return self._position

    def seek(self, value: int, whence: int = 0) -> int:
        if whence == 0:
            self.position = value
        elif whence == 1:
            self.position = self._position + value
        elif whence == 2:
            self.position = len(self._stream) - value
        else:
            raise ValueError("Invalid `whence` value! Should be in range 0-2.")
        return self._position

    def align(self, alignment: int, fill: bytes = b"\x00"):
        if alignment <= 0:
            raise ValueError("alignment must be positive")
        pad = (-self._position) % alignment
        if pad:
            self.write(fill * pad)

    def padding(self, size: int, value: bytes = b"\x00"):
        self.write(value * size)

    # -- output -----------------------------------------------------------------

    def getvalue(self) -> bytes:
        return bytes(self._stream)

    def save(self, path: str | Path):
        """Write the buffer to `path`, overwriting it if it already exists."""
        Path(path).write_bytes(self.getvalue())

    # -- raw bytes ------------------------------------------------------------

    def write(self, value: bytes | bytearray):
        """Write `value` at the current position, overwriting existing bytes
        in place and extending the buffer only if it runs past the end."""
        end = self._position + len(value)
        if end > len(self._stream):
            self._stream.extend(b"\x00" * (end - len(self._stream)))
        self._stream[self._position:end] = value
        self._position = end

    # -- fixed-width scalars ---------------------------------------------------

    def _pack(self, fmt_char: str, value):
        fmt = self.order + fmt_char
        size = struct.calcsize(fmt)
        end = self._position + size
        if end > len(self._stream):
            self._stream.extend(b"\x00" * (end - len(self._stream)))
        struct.pack_into(fmt, self._stream, self._position, value)
        self._position = end

    def s8(self, value: int):
        self._pack("b", value)

    def u8(self, value: int):
        self._pack("B", value)

    def s16(self, value: int):
        self._pack("h", value)

    def u16(self, value: int):
        self._pack("H", value)

    def s32(self, value: int):
        self._pack("i", value)

    def u32(self, value: int):
        self._pack("I", value)

    def s64(self, value: int):
        self._pack("q", value)

    def u64(self, value: int):
        self._pack("Q", value)

    def f32(self, value: float):
        self._pack("f", value)

    def f64(self, value: float):
        self._pack("d", value)


    # -- arrays of fixed-width scalars -----------------------------------------

    def _pack_array(self, fmt_char: str, values):
        values = tuple(values)
        fmt = f"{self.order}{len(values)}{fmt_char}"
        size = struct.calcsize(fmt)
        end = self._position + size
        if end > len(self._stream):
            self._stream.extend(b"\x00" * (end - len(self._stream)))
        struct.pack_into(fmt, self._stream, self._position, *values)
        self._position = end

    def s8_array(self, values):
        self._pack_array("b", values)

    def u8_array(self, values):
        self._pack_array("B", values)

    def s16_array(self, values):
        self._pack_array("h", values)

    def u16_array(self, values):
        self._pack_array("H", values)

    def s32_array(self, values):
        self._pack_array("i", values)

    def u32_array(self, values):
        self._pack_array("I", values)

    def s64_array(self, values):
        self._pack_array("q", values)

    def u64_array(self, values):
        self._pack_array("Q", values)

    def f32_array(self, values):
        self._pack_array("f", values)

    def f64_array(self, values):
        self._pack_array("d", values)


    # -- strings ----------------------------------------------------------------

    def cstring(self, value: str, encoding: str = "utf-8"):
        self.write(value.encode(encoding) + b"\x00")

    def fixed_string(self, value: str, size: int, encoding: str = "utf-8", fill: bytes = b"\x00"):
        data = value.encode(encoding)
        if len(data) > size:
            raise ValueError(f"Encoded string ({len(data)} bytes) exceeds fixed size {size}")
        self.write(data + fill * (size - len(data)))

    def pascal_string(self, value: str, length_type: str = "u8", encoding: str = "utf-8"):
        if length_type not in _LENGTH_PREFIXES:
            raise ValueError(f"length_type must be one of {_LENGTH_PREFIXES}")
        data = value.encode(encoding)
        getattr(self, length_type)(len(data))
        self.write(data)
