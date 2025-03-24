import pathlib
import json

from symphony_model_checker.symphony.behavior import behavior_parse
# from symphony_model_checker.symphony.summary import summaryMain
from symphony_model_checker.symphony.summarize import Summarize

def brief_kv(js):
    return (brief_string(js["key"]), brief_string(js["value"]))

def brief_idx(js):
    return "[" + brief_string(js) + "]"

def brief_string(js):
    type = js["type"]
    if type == "address":
        if "func" not in js:
            return "None"
        result = "?"
        func = js["func"]
        args = js["args"]
        if func["type"] == "pc":
            if int(func["value"]) == -1:
                result += args[0]["value"]
                args = args[1:]
            elif int(func["value"]) == -2:
                result += "@" + args[0]["value"]
                args = args[1:]
            else:
                result += brief_string(func)
        else:
            result += brief_string(func)
        return result + "".join([ brief_idx(kv) for kv in args ])
    v = js["value"]
    if type == "bool":
        return v
    if type == "int":
        return str(v) if isinstance(v, int) else v
    if type == "atom":
        return json.dumps(v, ensure_ascii=False)
    if type == "set":
        if v == []:
            return "{}"
        lst = [ brief_string(val) for val in v ]
        return "{ " + ", ".join(lst) + " }"
    if type == "list":
        if v == []:
            return "[]"
        lst = [ brief_string(val) for val in v ]
        return "[ " + ", ".join(lst) + " ]"
    if type == "dict":
        if v == []:
            return "{:}"
        lst = [ brief_kv(kv) for kv in v ]
        keys = [ k for k,v in lst ]
        if keys == [str(i) for i in range(len(v))]:
            return "[ " + ", ".join([v for k,v in lst]) + " ]" 
        else:
            return "{ " + ", ".join([k + ": " + v for k,v in lst]) + " }" 
    if type == "pc":
        return "PC(%s)"%v
    if type == "context":
        return "CONTEXT(" + str(v["pc"]) + ")"

def brief_print_vars(d):
    print("{", end="")
    first = True
    for k, v in d.items():
        if first:
            first = False
        else:
            print(",", end="")
        print(" %s: %s"%(k, brief_string(v)), end="")
    print(" }")

def brief_print_range(start, end):
    if start == end:
        return "%d"%(start)
    if start + 1 == end:
        return "%d,%d"%(start, end)
    return "%d-%d"%(start, end)

class Brief:
    def __init__(self):
        self.tid = None
        self.name = None
        self.start = 0
        self.steps = ""
        self.interrupted = False
        self.lastmis = {}
        self.shared = {}
        self.failure = ""

    def flush(self):
        if self.tid is not None:
            print("T%s: %s ["%(self.tid, self.name), end="")
            if self.steps != "":
                self.steps += ","
            self.steps += brief_print_range(self.start, int(self.lastmis["pc"]))
            print(self.steps + "] ", end="")
            brief_print_vars(self.shared)

    def print_macrostep(self, mas):
        mis = mas["microsteps"]
        if mas["tid"] != self.tid:
            self.flush()
            self.tid = mas["tid"]
            self.name = mas["name"]
            self.interrupted = False
            self.lastmis = mis[0]
            self.start = int(self.lastmis["pc"])
            if "shared" in self.lastmis:
                self.shared = self.lastmis["shared"]
            lastpc = 0
            self.steps = ""
            begin = 1
        else:
            begin = 0
        for i in range(begin, len(mis)):
            if "shared" in mis[i]:
                self.shared = mis[i]["shared"]
            if self.interrupted:
                if self.steps != "":
                    self.steps += ","
                self.steps += brief_print_range(self.start, int(self.lastmis["pc"]))
                self.start = int(mis[i]["pc"])
                self.steps += ",interrupt"
            elif "choose" in mis[i]:
                if self.steps != "":
                    self.steps += ","
                self.steps += brief_print_range(self.start, int(mis[i]["pc"]))
                self.steps += "(choose %s)"%brief_string(mis[i]["choose"])
                self.start = int(mis[i]["pc"]) + 1
            elif "print" in mis[i]:
                if self.steps != "":
                    self.steps += ","
                self.steps += brief_print_range(self.start, int(mis[i]["pc"]))
                self.steps += "(print %s)"%brief_string(mis[i]["print"])
                self.start = int(mis[i]["pc"]) + 1
            elif int(mis[i]["pc"]) != int(self.lastmis["pc"]) + 1:
                if self.steps != "":
                    self.steps += ","
                self.steps += brief_print_range(self.start, int(self.lastmis["pc"]))
                self.start = int(mis[i]["pc"])
            self.lastmis = mis[i]
            if "failure" in self.lastmis:
                self.failure = self.lastmis["failure"]
            self.interrupted = "interrupt" in self.lastmis and self.lastmis["interrupt"] == "True"

    def run(self, outputfiles, behavior):
        with open(outputfiles["hco"], encoding='utf-8') as f:
            print("* Phase 6: loading", outputfiles["hco"])
            top = json.load(f, strict=False)
            assert isinstance(top, dict)
            if top["issue"] == "No issues":
                behavior_parse(top, False, outputfiles, behavior)
            else:
                se = Summarize()
                se.run(outputfiles, top)

            # print()
            # p = pathlib.Path(outputfiles["htm"]).resolve()
            # url = "file://" + str(p)
            # print("open " + url + " for detailed information, or use the SymphonyGUI")

            # print("Issue:", top["issue"])
            # assert isinstance(top["macrosteps"], list)
            # for mes in top["macrosteps"]:
            #     self.print_macrostep(mes)
            # self.flush()
            # print(self.failure)
            # print("* Phase 7: print failure summary")
            # print(summaryMain(outputfiles, top))
