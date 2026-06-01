"""Strict scope enforcement."""
from __future__ import annotations
import ipaddress, fnmatch
from typing import Optional
import structlog
logger = structlog.get_logger(__name__)

class ScopeEnforcer:
    def __init__(self, scope_file=""):
        self._allowed_domains: list[str] = []
        self._allowed_ips: list[str] = []
        self._denied_domains: list[str] = []
        self._denied_ips: list[str] = []
        self._strict = True
        if scope_file: self.load_file(scope_file)
    @property
    def strict(self): return self._strict
    @strict.setter
    def strict(self, v): self._strict = v
    def load_file(self, filepath):
        try:
            for line in open(filepath):
                line = line.strip()
                if line and not line.startswith("#"): self.add_allowed(line)
        except FileNotFoundError: pass
    def add_allowed(self, entry):
        (self._allowed_ips if self._is_ip(entry) else self._allowed_domains.append(entry.lower()))
    def add_denied(self, entry):
        (self._denied_ips if self._is_ip(entry) else self._denied_domains.append(entry.lower()))
    def remove(self, entry):
        entry = entry.lower()
        for lst in [self._allowed_domains, self._allowed_ips]:
            if entry in lst: lst.remove(entry)
    def validate(self, target): return self.is_in_scope(target)
    def is_in_scope(self, target):
        t = target.lower().strip()
        if self._is_denied(t): return False
        if self._is_ip(t): return self._check_ip(t)
        return self._check_domain(t)
    def _is_denied(self, t):
        for d in self._denied_domains:
            if fnmatch.fnmatch(t, d) or fnmatch.fnmatch(t, f"*.{d}"): return True
        if self._is_ip(t):
            for d in self._denied_ips:
                try:
                    if ipaddress.ip_address(t) in ipaddress.ip_network(d, strict=False): return True
                except ValueError: continue
        return False
    def _check_domain(self, domain):
        for a in self._allowed_domains:
            if domain == a: return True
            if a.startswith("*."):
                s = a[2:]
                if domain == s or domain.endswith("." + s): return True
            if fnmatch.fnmatch(domain, a): return True
        return not self._strict
    def _check_ip(self, ip):
        try:
            addr = ipaddress.ip_address(ip)
            for a in self._allowed_ips:
                try:
                    if addr in ipaddress.ip_network(a, strict=False): return True
                except ValueError: continue
        except ValueError: pass
        return not self._strict
    @staticmethod
    def _is_ip(v):
        try:
            ipaddress.ip_address(v); return True
        except ValueError:
            try:
                ipaddress.ip_network(v, strict=False); return True
            except ValueError: return False
