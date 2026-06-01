"""CVSS v3.1 calculator + CVE database."""
from __future__ import annotations
import math
from typing import Optional

AV = {"N":0.85,"A":0.62,"L":0.55,"P":0.20}
AC = {"L":0.77,"H":0.44}
PR = {"N":{"U":0.85,"C":0.85},"L":{"U":0.62,"C":0.68},"H":{"U":0.27,"C":0.50}}
UI = {"N":0.85,"R":0.62}
IMP = {"N":0.0,"L":0.22,"H":0.56}

class CVSSCalculator:
    @staticmethod
    def calculate(vector: str) -> float:
        m = {}
        for p in vector.split("/"):
            if ":" in p: k,v = p.split(":",1); m[k.strip()] = v.strip()
        av = AV.get(m.get("AV","N"),0.85)
        ac = AC.get(m.get("AC","L"),0.77)
        s = m.get("S","U")
        pr = PR.get(m.get("PR","N"),{}).get("C" if s=="C" else "U",0.85)
        ui = UI.get(m.get("UI","N"),0.85)
        c,i,a = IMP.get(m.get("C","N"),0), IMP.get(m.get("I","N"),0), IMP.get(m.get("A","N"),0)
        iss = 1-((1-c)*(1-i)*(1-a))
        impact = 6.42*iss if s=="U" else 7.52*(iss-0.029)-3.25*((iss-0.02)**15)
        expl = 8.22*av*ac*pr*ui
        if impact <= 0: return 0.0
        score = min(impact+expl,10.0) if s=="U" else min(1.08*(impact+expl),10.0)
        return round(math.ceil(score*10)/10,1)
    @staticmethod
    def severity(score: float) -> str:
        if score >= 9: return "critical"
        if score >= 7: return "high"
        if score >= 4: return "medium"
        if score > 0: return "low"
        return "info"

class CVEDatabase:
    def __init__(self, data_dir="data/cve"): self._cache = {}
    def lookup(self, cve_id: str) -> Optional[dict]:
        return self._cache.get(cve_id)
    def search_by_product(self, product: str) -> list: return []
