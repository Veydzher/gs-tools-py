
class GSCodeProc:
    def __init__(self, in_name: str, in_args_num: int):
        self.name = in_name
        self.args_num = in_args_num

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self!s}({self.__dict__})"


class GSCodeProcToken:
    def __init__(self, opcode: int, name: str, args: list[int], local_jump_target_index=None, local_jump_token_offset=None):
        self.opcode = opcode
        self.name = name
        self.args = args
        self.local_jump_target_index = local_jump_target_index
        self.local_jump_token_offset = local_jump_token_offset

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self!s}({self.__dict__})"

    def to_json(self):
        return {
            "$type": self.__class__.__name__,
            **{k: v for k,v in self.__dict__.items() if v is not None}
        }


class GSStringToken:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self!s}({self.__dict__})"

    def to_json(self):
        return {
            "$type": self.__class__.__name__,
            "value": self.value
        }


class GSLabelToken:
    def __init__(self, target_msg_index: int, target_token_index: int, target_token_offset: int):
        self.target_msg_index = target_msg_index
        self.target_token_index = target_token_index
        self.target_token_offset = target_token_offset

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self!s}({self.__dict__})"

    def to_json(self):
        return {
            "$type": self.__class__.__name__,
            **self.__dict__
        }
