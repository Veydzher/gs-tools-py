from src.gs.classes import GSCodeProc, GSCodeProcToken, GSStringToken

CHAR_CONVERSIONS = {
    "１": "1", "２": "2",
    "３": "3", "４": "4",
    "５": "5", "６": "6",
    "７": "7", "８": "8",
    "９": "9", "０": "0",

    "Ａ": "A", "Ｂ": "B", "ａ": "a", "ｂ": "b",
    "Ｃ": "C", "Ｄ": "D", "ｃ": "c", "ｄ": "d",
    "Ｅ": "E", "Ｆ": "F", "ｅ": "e", "ｆ": "f",
    "Ｇ": "G", "Ｈ": "H", "ｇ": "g", "ｈ": "h",
    "Ｉ": "I", "Ｊ": "J", "ｉ": "i", "ｊ": "j",
    "Ｋ": "K", "Ｌ": "L", "ｋ": "k", "ｌ": "l",
    "Ｍ": "M", "Ｎ": "N", "ｍ": "m", "ｎ": "n",
    "Ｏ": "O", "Ｐ": "P", "ｏ": "o", "ｐ": "p",
    "Ｑ": "Q", "Ｒ": "R", "ｑ": "q", "ｒ": "r",
    "Ｓ": "S", "Ｔ": "T", "ｓ": "s", "ｔ": "t",
    "Ｕ": "U", "Ｖ": "V", "ｕ": "u", "ｖ": "v",
    "Ｗ": "W", "Ｘ": "X", "ｗ": "w", "ｘ": "x",
    "Ｙ": "Y", "Ｚ": "Z", "ｙ": "y", "ｚ": "z",

    "\u3000": " ",
    "．": ".", "，": ",",
    "＇": "'", "！": "!",
    "（": "(", "）": ")",
    "－": "-", "／": "/",
    "？": "?", "∠": "_",
    "［": "[", "］": "]",
    "“": "\"", "”": "\"",
    "＂": "\"", "―": "-",
    "‘": "'", "’": "'",
    "：": ":", "；": ";",
    "＊": "*", "＄": "$",

    "Ы": "©",
    "∋": "è", "∈": "é",
    "∀": "á", "∧": "à",
    "⊆": "ç", "⊂": "Ç",
    "↑": "î", "α": "â",
    "↓": "ï", "ε": "ê"

    # { "Ц", "û" },
    # { "л", "ñ" },
}

def en_to_half(string: str):
    for en, half in CHAR_CONVERSIONS.items():
        string = string.replace(en, half)

    return string

def half_to_en(string: str):
    for en, half in CHAR_CONVERSIONS.items():
        string = string.replace(half, en)

    return string

ESCAPE_REPLACEMENTS = {
    "\r\n": "\\r\\n",
    "\r": "\\r",
    "\n": "\\n",
    "\t": "\\t",
    "\"": "\\\""
}

def escape(string: str):
    for unescaped, escaped in ESCAPE_REPLACEMENTS.items():
        string = string.replace(unescaped, escaped)

    return string

def unescape(string: str):
    for unescaped, escaped in ESCAPE_REPLACEMENTS.items():
        string = string.replace(escaped, unescaped)

    return string

def get_token_size(token):
    match token:
        case GSStringToken():
            return len(unescape(token.value))
        case GSCodeProcToken():
            return len(token.args) + 1
        case _:
            return 0

def resolve_position(tokens, target_u16_idx):
    walked_pos = 0
    for t, token in enumerate(tokens):
        size = get_token_size(token)
        if walked_pos <= target_u16_idx < walked_pos + size:
            return t, target_u16_idx - walked_pos
        walked_pos += size
    return len(tokens), 0

def resolve_byte_offset(tokens, token_idx, token_offset):
    u16_pos = sum(get_token_size(t) for t in tokens[:token_idx])
    return (u16_pos + token_offset) * 2

CODE_PROCS = [
    GSCodeProc("CodeProc_00", 0),
    GSCodeProc("NewLine", 0),
    GSCodeProc("ReadKey", 0),   # page command
    GSCodeProc("SetTextColor", 1),  # args: colorIndex
    GSCodeProc("SkipIfButtonPressed", 1),   # args: unknown
    GSCodeProc("PlayBGM", 2),   # args: trackId, unknown
    GSCodeProc("ControlSE", 2), # args: seId, flag
    GSCodeProc("ReadKey_1", 0),   # page command
    GSCodeProc("CodeProc_08", 2),   # page command
    GSCodeProc("CodeProc_09", 3),   # page command
    GSCodeProc("ReadKey_2", 1),   # page command, args: unknown
    GSCodeProc("SetMessageTime", 1),    # args: framesPerChar
    GSCodeProc("Wait", 1),  # args: frames
    GSCodeProc("Exit", 0),  # page command
    GSCodeProc("SetSpeakerId", 1),  # args: speakerId
    GSCodeProc("SetTukkomi", 2),    # args: tukkomiNo, tukkomiFlag
    GSCodeProc("SetGSFlag", 1), # args: packedFlag
    GSCodeProc("CodeProc_11", 0),
    GSCodeProc("PlayFadeCtrl", 3),  # args: fadeType, duration, alpha
    GSCodeProc("SetItemPlateCtrl", 1),  # args: itemId
    GSCodeProc("CloseItemPlateCtrl", 0),
    GSCodeProc("CodeProc_15", 0),   # page command
    GSCodeProc("NextScenario", 0),
    GSCodeProc("AddRecord", 1), # args: recordId
    GSCodeProc("DeleteRecord", 1),  # args: recordId
    GSCodeProc("UpdateRecord", 2),  # args: recordId, unknown
    GSCodeProc("CourtScroll", 4),   # args: unknown x4
    GSCodeProc("SetBackground", 1), # args: backgroundId
    GSCodeProc("SetMessageWindowState", 1),   # args: windowState (0–4)
    GSCodeProc("ScrollBackground", 1),  # args: unknown
    GSCodeProc("PlayCharacterAnimation", 3),    # args: charSlot, newPose, prevPose
    GSCodeProc("StopCutUpScroll", 0),
    GSCodeProc("SetNextNumber", 1), # args: nextMessageNo
    GSCodeProc("CodeProc_21", 0),
    GSCodeProc("FadeOutBGM", 2),    # args: _unused, fadeTarget
    GSCodeProc("ReplayBGM", 2), # args: unknown x2
    GSCodeProc("CodeProc_24", 0),
    GSCodeProc("CodeProc_25", 1),   # args: unknown
    GSCodeProc("SetStatusFlag", 1), # args: flagValue
    GSCodeProc("Quake", 2), # args: intensity, type
    GSCodeProc("CodeProc_28", 1),   # args: unknown
    GSCodeProc("SetQuestioningState", 1),   # args: mode (enter/exit/first)
    GSCodeProc("ConditionalSetNext", 3),   # page command, args: flag, nextIfTrue, nextIfFalse
    GSCodeProc("DoDamage", 0),
    GSCodeProc("SetNextAndClear", 1),   # args: nextMessageNo
    GSCodeProc("ReadKey_3", 0),   # page command
    GSCodeProc("ClearText", 0), # page command
    GSCodeProc("PlayObjectAnimation", 2),   # args: objectId, unknown
    GSCodeProc("SetMessageSE", 1),  # args: seId
    GSCodeProc("CharFade", 2),  # args: unknown x2
    GSCodeProc("MapData", 2),   # args: unknown x2
    GSCodeProc("MapData_1", 5), # args: unknown x5
    GSCodeProc("CodeProc_34", 1),   # args: unknown
    GSCodeProc("ConditionalGoto", 2),   # args: flagWord, target
    GSCodeProc("Goto", 1),  # args: labelNo
    GSCodeProc("SetTalkDataSw", 2), # args: unknown x2
    GSCodeProc("SetActiveCharacterAnimation", 1),   # args: unknown
    GSCodeProc("LoadSprite", 1),    # args: spriteId
    GSCodeProc("SetMapIconPosition", 3),    # args: unknown x3
    GSCodeProc("SetMapIconParameters", 2),  # args: unknown x2
    GSCodeProc("MapIconBlink", 1),  # args: unknown
    GSCodeProc("MapIconVisible", 1),    # args: unknown
    GSCodeProc("StartPointMiniGame", 1),   # args: sitekiNo
    GSCodeProc("UpdatePointMiniGame", 0),
    GSCodeProc("SetStatusPointCursolOff", 0),
    GSCodeProc("SetSubWindowReqTMain", 0),
    GSCodeProc("SetSoundFlag", 1),  # args: flag
    GSCodeProc("SetLifeGauge", 1), # args: value
    GSCodeProc("Judgment", 1),  # args: verdict
    GSCodeProc("CodeProc_15_1", 0),   # page command
    GSCodeProc("CutIn", 1), # args: unknown
    GSCodeProc("VolumeChangeBGM", 2),   # args: unknown x2
    GSCodeProc("SetMessageBoardPos", 2),    # args: unknown x2
    GSCodeProc("CodeProc_49", 0),
    GSCodeProc("CheckGuilty", 1),   # args: unknown
    GSCodeProc("CodeProc_4B", 1),  # args: unknown
    GSCodeProc("IsBackgroundScrolling", 0),
    GSCodeProc("CodeProc_4D", 2),  # args: unknown x2
    GSCodeProc("CodeProc_4E", 1),  # args: unknown
    GSCodeProc("SetPsylockData", 7),    # args: unknown x7
    GSCodeProc("ClearPsylock", 1),  # args: psylockId
    GSCodeProc("RoomSeqChange", 2), # args: unknown x2
    GSCodeProc("SetSubWindowReqMagatamaMenuOn", 1), # args: unknown
    GSCodeProc("DisablePsyMenu", 0),
    GSCodeProc("SetLifeGauge_1", 2),    # args: unknown x2
    GSCodeProc("SetBackgroundEx", 1),   # args: unknown
    GSCodeProc("CodeProc_56", 2),   # args: unknown x2
    GSCodeProc("SetPsylockNumber", 1),   # args: psyNo
    GSCodeProc("PsylockDispResetStatic", 0),
    GSCodeProc("AddPsylock", 1),    # args: lockId
    GSCodeProc("RemovePsylock", 1), # args: lockId
    GSCodeProc("TanteiMenuRecov", 2),   # args: unknown x2
    GSCodeProc("MosaicRun", 3), # args: unknown x3
    GSCodeProc("CodeProc_5D", 0),
    GSCodeProc("CodeProc_5E", 0),
    GSCodeProc("MonochromeSet", 3), # args: unknown x3
    GSCodeProc("SetPsylockItem", 4),   # args: unknown x4
    GSCodeProc("AddPsylockItem", 3),   # args: unknown x3
    GSCodeProc("PsylockToNormalBackground", 0),
    GSCodeProc("PsylockRedisp", 0),
    GSCodeProc("CodeProc_64", 1),   # args: unknown
    GSCodeProc("SetBackgroundParts", 2),    # args: unknown x2
    GSCodeProc("SetPsylockBGM", 3),   # args: unknown x3
    GSCodeProc("MessageInit", 0),
    GSCodeProc("CodeProc_68", 0),
    GSCodeProc("PlayBackgroundAnimation", 2),   # args: objType, animId
    GSCodeProc("LoadScenario", 1),  # args: scenarioId
    GSCodeProc("SetAllWork", 3),    # args: unknown x3
    GSCodeProc("CodeProc_6C", 0),
    GSCodeProc("CodeProc_6D", 1),   # args: unknown
    GSCodeProc("SetStatusThreeLine", 1),    # args: unknown
    GSCodeProc("SetBkEndMess", 1),  # args: unknown
    GSCodeProc("CodeProc_70", 3),   # args: unknown x3
    GSCodeProc("SetPsylockUnlockResult", 3),    # args: _unused, resultFlag, _unused
    GSCodeProc("CodeProc_Dummy", 0),
    GSCodeProc("CodeProc_Dummy_1", 0),
    GSCodeProc("SetSubWindowReq", 2),   # sbyte action, sbyte param
    GSCodeProc("SetVideo", 4),  # args: unknown x4
    GSCodeProc("SetFacePlate", 2),  # action, faceId
    GSCodeProc("FadeOutSE", 2), # args: unknown x2
    GSCodeProc("Goto_1", 1),    # args: labeNo
    GSCodeProc("CodeProc_15_2", 0),
    GSCodeProc("GotoIfGameOver", 1),    # args: labelNo
    GSCodeProc("ControlDIcon", 2),   # args: action, iconId
    GSCodeProc("GS2UpdateSc3Opening", 0),
    GSCodeProc("GS2HanabiraMove", 1),   # args: unknown
    GSCodeProc("GS2SpotlightMoveFocus", 1), # args: unknown
    GSCodeProc("DrawIconText", 1),  # args: unknown
    # GSCodeProc("CodeProc_80", 0),
]
