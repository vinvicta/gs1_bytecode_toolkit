import sys
import re
import binascii
import argparse
import os

# ==============================================================================
# 1. KNOWLEDGE BASE
# ==============================================================================
# GS1 relies heavily on string comparison for function names. 
# This list helps the tokenizer identify function calls in the binary stream.
gs1_functions = {
    "addarray", "addcontrol", "addlines", "addmaterialmapping", "addnode",
    "addnodebypath", "addrow", "addtiledef", "addtiledef2", "addvars",
    "aindexof", "arccos", "arcsin", "attachplayertoobj", "attachterrain",
    "base64decode", "base64encode", "blockagain", "blockagainlocal", "boxcontains",
    "boxcontainsvector", "boxintersect", "boxoverlaps", "boxscale", "bringtofront",
    "buildmaterialmap", "callnpc", "callweapon", "canbecarried", "canbepulled",
    "canbepushed", "cancelevents", "cannotbecarried", "cannotbepulled", "cannotbepushed",
    "carryobject", "castray", "catchevent", "changeimgcolors", "changeimgmode",
    "changeimgpart", "changeimgvis", "changeimgzoom", "checksum", "clearControls",
    "clearall", "clearmodifiedflags", "clearnodes", "clearrectangle", "clearrows",
    "clearselection", "contains", "copyfrom", "copystrings", "cursoroff",
    "cursoron", "degtorad", "destroy", "detachplayer", "disabledefmovement",
    "disablemap", "disablepause", "disableselectweapons", "disableweapons", "dontblock",
    "dontblocklocal", "drawaslight", "drawimage", "drawimagerectangle", "drawimagestretched",
    "drawoverplayer", "drawunderplayer", "echo", "enabledefmovement", "enablefeatures",
    "enablemap", "enablepause", "enableselectweapons", "enableweapons", "escape",
    "escapestring", "explodebomb", "extractfilebase", "extractfileext", "extractfilepath",
    "fileexists", "filesize", "fileupdate", "findani", "findareanpcs",
    "findfiles", "findimg", "findlevel", "findnearestplayer", "findnearestplayers",
    "findnpcbyid", "findpathinarray", "findplayer", "findplayerbycommunityname", "findplayerbyid",
    "findtext", "findtextid", "findweapon", "format", "format2",
    "freefileresources", "freezeplayer", "get3dobjectat", "get3dobjectatmouse", "get3dobjectbyray", 
    "get3dobjectsbybox", "get3dscreenposition", "getExtension", "getactionname", "getanglesfromvector",
    "getascii", "getbasepackage", "getboxcenter", "getbrushpos", "getcurrentaction",
    "getdatablockvars", "getdesktopresolution", "getdisplaydevicelist", "getdownloadedupdatepackagesize", "getdownloadingpackage",
    "getdownloadingpackagescount", "getdropz", "getdynamicvarnames", "geteditvarnames", "getfilemodtime",
    "getfullname", "getfunctions", "gethttprequest", "getimgheight", "getimgpixel",
    "getimgwidth", "getkeycode", "getloginaccountname", "getmapx", "getmapy",
    "getmusicfilename", "getmusicstatus", "getmusictags", "getnearestplayer", "getnearestplayers",
    "getnode", "getnodeat", "getnodebypath", "getnumactions", "getnumtextures",
    "getpackagesdownloadcomplete", "getpackagesdownloaded", "getparent", "getplatform", "getresolutionlist",
    "getrowatpoint", "getrowidatpoint", "getrownumbyid", "getselectedid", "getselectednode",
    "getselectedrow", "getselectedtext", "getservername", "getstaticvarnames", "getstringkeys",
    "getterrainmaterials", "getterraintexture", "getterraintextureindex", "gettext", "gettextheight",
    "gettexturename", "gettextwidth", "gettileset", "gettilesettype", "gettotalupdatepackagesize",
    "getupdatepackage", "getvarnames", "getvectorfromangles", "getz", "globaltolocalcoord",
    "graalcontrolhasfocus", "hide", "hideimg", "hideimgs", "hidelocal",
    "hideplayer", "hidesword", "hitcompu", "hitnpc", "hitobjects",
    "hitplayer", "hurt", "ignoreevent", "ignoreevents", "insertarray",
    "insertrow", "isadminguild", "isclassloaded", "iscursoron", "isdevicefullscreenonly",
    "isdownloading", "isdownloadingfiles", "isfirstresponder", "isfullscreenmode", "isguildpm",
    "isidselected", "isimgrectangletransparent", "isinclass", "ismasspm", "ismusicplaying",
    "isobject", "isrowselected", "issoundplaying", "join", "keydown",
    "keydown2", "keydown2global", "keydownglobal", "keyname", "lay",
    "lay2", "leave", "lightscene", "loadclass", "loadfolder",
    "loadlines", "loadmap", "loadstring", "loadtranslation", "loadvars",
    "loadvarsfromarray", "loadxml", "loadxmlfromstring", "localtoglobalcoord", "lowercase",
    "ltmfs", "ltmmax", "ltmmin", "makefirstresponder", "makescreenshot2",
    "makevisible", "makevisiblebyid", "markemptysquares", "matrixcreate", "matrixcreatefromeuler",
    "matrixmulpoint", "matrixmultiply", "matrixmulvector", "md5", "message",
    "mirrorterrain", "mountshape", "move", "noplayerkilling", "objecttype",
    "onwall", "onwall2", "onwater", "onwater2", "openexternalhistory",
    "openexternalpm", "opengraalurl", "openurl", "openurl2", "performclick",
    "play", "play2", "play3d", "playlooped", "playlooped2",
    "pmswaiting", "popbasematerialinfo", "popdialog", "processaction", "pushbasematerialinfo",
    "pushdialog", "pushtoback", "putbomb", "putcomp", "putexplosion",
    "putexplosion2", "puthorse", "putleaps", "putnewcomp", "radtodeg",
    "randomstring", "redo", "reflectarrow", "removebomb", "removecompus",
    "removeexplo", "removehorse", "removeitem", "removerow", "removerowbyid",
    "removetiledefs", "replaceani", "requestfiledeletion", "requestfilerename", "requestfilesmove", 
    "requesthttp", "requesttext", "requesturl", "resetfocus", "resetselweights",
    "resize", "rotationadd", "rotationaddeuler", "rotationfromeuler", "rotationsub",
    "rotationtoeuler", "rowcount", "rungarbagecollector", "savelines", "savelog",
    "savestring", "savevars", "savevarstoarray", "savexml", "savexmltostring",
    "say", "say2", "scheduleevent", "screenx", "screeny",
    "select", "selectfilefordownload", "selectfileforupload", "sendrpgmessage", "sendtext",
    "sendtorc", "serverwarp", "setaction", "setani", "setbeltcolor",
    "setbitmap", "setbow", "setbrushpos", "setbrushsize", "setbrushtype",
    "setcharani", "setchargender", "setcoatcolor", "setcoloreffect", "setcontentcontrol",
    "setcursor2", "seteffect", "seteffectmode", "setflymode", "setfocus",
    "setfogcolors", "setgender", "sethead", "seticonsize", "setimg",
    "setimgpart", "setinteriorrendermode", "setletters", "setlonebasematerial", "setmap",
    "setminimap", "setmodel", "setmusicvolume", "setorbitmode", "setplayerdir",
    "setselectedbyid", "setselectedrow", "setshape", "setshape2", "setshield",
    "setshoecolor", "setshootparams", "setskincolor", "setskybandcolors", "setskybandsizes",
    "setsleevecolor", "setspritesimage", "setstatusimage", "setsuncolors", "setsword",
    "setterrainmaterials", "setterrainrendermode", "settext", "settimer", "setvalue",
    "setz", "setzoomeffect", "shoot", "shootarrow", "shootball",
    "shootfireball", "shootfireblast", "shootnuke", "show", "showani",
    "showani2", "showcharacter", "showimg", "showimg2", "showlocal",
    "showpm", "showpoly", "showpoly2", "showprofile", "showstats",
    "showtext", "showtext2", "showtop", "sort", "sortascending",
    "sortbyvalue", "sortdescending", "spyfire", "startrecordvideo", "stopmidi",
    "stopmusic", "stoprecordvideo", "stopsound", "strcmp", "strequals",
    "subarray2", "switchtoopengl", "synctimeofday", "tabfirst", "take",
    "take2", "takehorse", "takeplayercarry", "takeplayerhorse", "testbomb",
    "testexplo", "testhorse", "testitem", "testnpc", "testplayer",
    "testsign", "throwcarry", "tiletype", "timereverywhere", "timershow",
    "toweapons", "trace", "trigger", "triggeraction", "triggerserver",
    "undo", "unmountshape", "update3dterrain", "updateboard", "updateterrain",
    "updatevisibledistance", "uploadfile", "uppercase", "vectoradd", "vectorcross",
    "vectordist", "vectordot", "vectorlen", "vectornormalize", "vectororthobasis",
    "vectorscale", "vectorsub", "worldx", "worldy", "wraptext", "wraptext2",
    "onCreated", "onTimeout", "drawNPCLines", "hideNPCLines", "drawLine"
}

# Standard GS1 Variables
gs1_variables = {
    "allfeatures", "allplayerscount", "allrenderobjecttypes", "allstats", "canspin",
    "carriesblackstone", "carriesbush", "carriesnpc", "carriessign", "carriesstone",
    "carriesvase", "downloadfile", "downloadpos", "downloadsize", "editingmission",
    "emoticonchar", "focusx", "focusy", "ghostsnear", "graalplugincookie",
    "graalversion", "gravity", "installedlanguages", "isapplicationactive",
    "iscarrying", "isfocused", "isgraal3d", "isgraalplugin", "isleader", "isonmap",
    "isopengl", "isrecordingvideo", "jpegquality", "lastdownloadfile",
    "leftmousebutton", "leftmousebuttonglobal", "levelorgx", "levelorgy",
    "lighteffectsenabled", "middlemousebutton", "middlemousebuttonglobal",
    "mousebuttons", "mousebuttonsglobal", "mousepitch", "mousescreenx",
    "mousescreeny", "mousewheeldelta", "mousex", "mousey", "mouseyaw", "musiclen",
    "musicpos", "particleeffectsenabled", "rightmousebutton", "rightmousebuttonglobal",
    "screenheight", "screenwidth", "scriptedcontrols", "scriptedplayerlist",
    "scriptlogwritetoreadonly", "selectedlistplayers", "selectedsword",
    "selectedweapon", "servername", "serverstartconnect", "serverstartparams",
    "shotbybaddy", "shotbyplayer", "showterraingrid", "spritesimage", "statusimage",
    "timevar", "timevar2", "timevar3", "wasshooted", "waterheight", "weapons",
    "weaponsenabled", "weathereffectsenabled", "worldclockstopped", "worldhour",
    "worldminute", "worldminutesofday", "worldrealsecondsperday", "npcs", "npc",
    "player", "this", "client", "server", "ani", "aniparams", "attr", "colors", 
    "ap", "arrows", "body", "bodyimg", "bombs", "chat", "darts", "dir", "dontsave", 
    "glovepower", "gralats", "head", "headimg", "hearts", "height", "hidetoclients", 
    "horseimg", "hurtdx", "hurtdy", "hurtpower", "id", "image", "level", "name", 
    "nick", "npcsindex", "rupees", "save", "shield", "shieldimg", "shieldpower", 
    "sprite", "sword", "swordimg", "swordpower", "visible", "width", "x", "y", "z", 
    "account", "attached", "attachid", "attachtype", "deaths", "fullhearts", "guild", 
    "headset", "hp", "isfemale", "ismale", "kills", "language", "languagedomain", 
    "lastdead", "logintime", "maxhp", "movementlimit", "mp", "onlinetime", "pause", 
    "paused", "platform", "rating", "ratingd", "trial", "upgradestatus", "version",
    "red", "green", "blue", "alpha", "thickness", "zoom", "polygon", "index", 
    "dimensions", "layer", "findimg"
}

gs1_keywords = {
    "true", "false", "null", "if", "for", "while", "else", "return", "break",
    "continue", "with", "temp", "new", "this"
}

# ==============================================================================
# 2. CORE CLASSES
# ==============================================================================

class GS1ParserBase:
    """
    Base parser for GS1 Containers.
    GS1 is 'Tokenized Source', meaning it stores readable strings separated by
    binary delimiters (Action Gaps).
    """
    def __init__(self, data):
        self.data = data
        self.cursor = 0
        self.tokens = []

    def parse(self):
        # 1. Skip Header if present
        # Many GS1 containers start with 00 00 00 01 followed by 4 bytes of length/flags
        if len(self.data) > 8:
            self.cursor = 8
        
        # 2. Extract Token Strings
        # We look for sequences of printable ASCII characters (SPACE to ~).
        # The bytes between these matches are the 'Opcodes' or 'Gaps'.
        string_pattern = re.compile(b'[ -~]{1,}')
        last_end = self.cursor

        for match in string_pattern.finditer(self.data):
            # If the match starts before our cursor (unlikely), skip it
            if match.start() < self.cursor: continue
            
            # The GAP is the binary data between the last string and this one.
            # In GS1, this gap contains instructions like "End of Line", "Assignment", etc.
            gap = self.data[last_end:match.start()]
            
            # The VALUE is the actual code token (e.g., "if", "x", "100")
            s_value = match.group().decode('ascii')
            
            self.tokens.append({
                "type": self._categorize(s_value),
                "value": s_value,
                "opcode": gap,
                "offset": match.start()
            })
            
            last_end = match.end()

    def _categorize(self, text):
        """Heuristic to determine token type based on Knowledge Base."""
        if text in gs1_functions: return "FUNCTION"
        if text in gs1_variables: return "VARIABLE"
        if text in gs1_keywords: return "KEYWORD"
        if text.startswith("//#"): return "DIRECTIVE"
        if re.match(r'^\d+(\.\d+)?$', text): return "NUMBER"
        if text in ["(", ")", "{", "}", ";", ",", ".", "="]: return "SYNTAX"
        if text in ["[", "]"]: return "SYNTAX"
        if text in ["+=", "-=", "*=", "/=", "==", "!=", ">=", "<=", "&&", "||", "%", "+", "-", "*", "/", ">", "<"]: return "OPERATOR"
        return "STRING"

class GS1Disassembler(GS1ParserBase):
    """Debug tool to view the Raw Token Stream."""
    def run(self):
        self.parse()
        print(f"[-] Disassembling {len(self.data)} bytes...\n")
        
        # Attempt to read version from header
        version = int.from_bytes(self.data[0:4], 'big') if len(self.data) > 4 else 0
        print(f"=== HEADER: Ver {version} ===\n")
        
        print(f"{'OFFSET':<8} | {'CATEGORY':<12} | {'VALUE / ACTION'}")
        print("-" * 65)

        for t in self.tokens:
            # Print the Gap (Opcode) if it exists
            if len(t['opcode']) > 0:
                hex_op = binascii.hexlify(t['opcode']).decode('ascii').upper()
                if len(hex_op) > 20: hex_op = hex_op[:20] + "..."
                print(f"0x{t['offset']-len(t['opcode']):04X}   | [OPCODE]     | {{ {hex_op} }}")
            
            # Print the Token
            print(f"0x{t['offset']:04X}   | {t['type']:<12} | \"{t['value']}\"")


class GS1Decompiler(GS1ParserBase):
    """
    Reconstructs high-level GS1 source code from the token stream.
    Since GS1 is tokenized, we mostly just need to add proper spacing and indentation.
    """
    def run(self, output_file=None):
        self.parse()
        print(f"[-] Decompiling {len(self.tokens)} tokens into Source Code...\n")
        
        source_code = ""
        indent_level = 0
        indent_str = "  " # 2 spaces per indent
        
        last_type = None
        last_val = ""
        
        for t in self.tokens:
            val = t['value']
            typ = t['type']
            
            prefix = ""
            suffix = ""
            
            # 1. Indentation & Block Handling
            if val == "}":
                indent_level = max(0, indent_level - 1)
                prefix = "\n" + (indent_str * indent_level)
            elif val == "{":
                suffix = "\n" + (indent_str * (indent_level + 1))
                
            # 2. Spacing Rules (Heuristics for readability)
            if last_type == "KEYWORD" and val != ";":
                prefix = " "
            elif typ == "OPERATOR" or last_type == "OPERATOR":
                if val not in ["++", "--"]: 
                    prefix = " "
            elif last_val == ",":
                prefix = " "
                
            # 3. Newline Rules
            if last_val == ";":
                prefix = "\n" + (indent_str * indent_level)
            if last_val == "{": 
                indent_level += 1
                prefix = (indent_str * indent_level)
            if val == "}" and last_val != ";":
                prefix = "\n" + (indent_str * indent_level)

            # 4. Special Cases
            if typ == "DIRECTIVE": suffix = "\n"
            if val == "." or last_val == ".": prefix = ""
            if val == "(" and last_type in ["FUNCTION", "KEYWORD", "VARIABLE", "STRING"]:
                if last_type == "KEYWORD": prefix = " "
                else: prefix = ""

            source_code += prefix + val + suffix
            
            last_type = typ
            last_val = val

        print("=== DECOMPILED SOURCE START ===")
        print(source_code)
        print("=== DECOMPILED SOURCE END ===\n")
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(source_code)
            print(f"[+] Saved decompiled source to {output_file}")


class GS1Assembler:
    """
    Compiles text source into the GS1 Binary Format.
    This creates the 'Gap + String' structure the engine expects.
    """
    def __init__(self, source_text):
        self.source = source_text

    def run(self):
        print("[-] Compiling Source to GS1 Binary Structure...")
        
        # Regex to split source into tokens (Keywords, Operators, Strings, Numbers)
        token_pattern = re.compile(
            r'(//#CLIENTSIDE)|' 
            r'(/\*[\s\S]*?\*/)|' 
            r'(//.*?$)|' 
            r'("(?:\\.|[^"\\])*")|' 
            r'(\b\d+(?:\.\d+)?\b)|' 
            r'([a-zA-Z_]\w*)|' 
            r'(==|!=|<=|>=|&&|\|\||\+\+|--|\+=|-=|\*=|/=|<<|>>)|'
            r'([+\-*/%=<>!&|^~?:.,;(){}\[\]])' 
        , re.MULTILINE)

        tokens = []
        clientside_flag = False

        for match in token_pattern.finditer(self.source):
            if match.group(1): # Directive
                tokens.append(match.group(1))
                if "CLIENTSIDE" in match.group(1): clientside_flag = True
            elif match.group(2) or match.group(3): continue # Skip Comments
            else: 
                tokens.append(match.group(0))

        # Build Standard GS1 Header
        # 00 00 00 01 = Version / Magic
        # 00 00 00 04 = Unknown (Length/Flag)
        header = bytearray(binascii.unhexlify("00000001000000040000000000000000"))
        if clientside_flag: print("[*] Marked as CLIENTSIDE")

        payload = bytearray(header)
        for token in tokens:
            # We inject '16F0' as a generic opcode separator.
            # In a true compiler, this might vary based on the token type,
            # but 16F0 is the most common delimiter seen in standard GS1 scripts.
            payload.extend(binascii.unhexlify("16F0")) 
            payload.extend(token.encode('ascii'))
            payload.append(0x00) # Null terminator for string token
            
        return payload

# ==============================================================================
# 3. MAIN ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="GS1 Toolkit v1.0 (Retargeted from GS2)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--disasm', action='store_true', help="Show Disassembly (Tokens + Opcodes)")
    group.add_argument('-D', '--decompile', action='store_true', help="Reconstruct High-Level Source Code")
    group.add_argument('-a', '--asm', action='store_true', help="Compile Source Code to Binary")
    
    parser.add_argument('input', nargs='?', help="File path OR literal string")
    parser.add_argument('-o', '--output', help="Output file path")
    
    args = parser.parse_args()

    # --- INPUT READING ---
    raw_input = b""

    if args.input and os.path.exists(args.input):
        with open(args.input, 'rb') as f:
            raw_input = f.read()
    elif args.input:
        raw_input = args.input.encode('utf-8')
    else:
        print("[!] Error: No input provided.")
        return

    # --- MAGIC HEADER DETECTION ---
    if args.disasm or args.decompile:
        # Standard GS containers usually start with this magic sequence.
        magic_v1 = b'\x00\x00\x00\x01'
        idx = raw_input.find(magic_v1)
        if idx > 0:
            print(f"[*] Container Header detected. Skipping {idx} bytes.")
            raw_input = raw_input[idx:]

    # --- EXECUTE MODES ---
    if args.disasm:
        disassembler = GS1Disassembler(raw_input)
        disassembler.run()

    elif args.decompile:
        decompiler = GS1Decompiler(raw_input)
        decompiler.run(args.output)

    elif args.asm:
        try:
            txt = raw_input.decode('utf-8')
        except:
            print("[!] Assembler input must be text.")
            return
        assembler = GS1Assembler(txt)
        bytecode = assembler.run()
        
        if args.output:
            with open(args.output, 'wb') as f:
                f.write(bytecode)
            print(f"[+] Compiled binary saved to {args.output}")
        else:
            print(binascii.hexlify(bytecode).decode('ascii'))

if __name__ == "__main__":
    main()