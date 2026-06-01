"""Tool Registry - 44+ security tools."""
from __future__ import annotations
import asyncio, shutil
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
import structlog
logger = structlog.get_logger(__name__)

@dataclass
class SecurityTool:
    name: str; description: str; category: str
    cmd_template: list[str]
    parse_func: Callable[[dict], list] = field(default_factory=lambda: lambda r: [r])
    timeout: int = 300; requires_root: bool = False; installed: bool = False
    def build_command(self, target, extra_args=None):
        cmd = [target if p == "{target}" else p for p in self.cmd_template]
        if extra_args:
            for k,v in extra_args.items(): cmd.extend([f"--{k}", str(v)])
        return cmd

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, SecurityTool] = {}
        self._register_all()
    def register(self, tool):
        tool.installed = shutil.which(tool.cmd_template[0]) is not None
        self._tools[tool.name] = tool
    def get_tool(self, name): return self._tools.get(name)
    def list_tools(self, category=None, installed_only=False):
        tools = list(self._tools.values())
        if category: tools = [t for t in tools if t.category == category]
        if installed_only: tools = [t for t in tools if t.installed]
        return tools
    @property
    def installed_count(self): return sum(1 for t in self._tools.values() if t.installed)
    @property
    def total_count(self): return len(self._tools)
    async def execute(self, name, target, extra_args=None, timeout=None):
        tool = self._tools.get(name)
        if not tool: return {"error": f"Unknown tool: {name}"}
        if not tool.installed: return {"error": f"Not installed: {name}"}
        cmd = tool.build_command(target, extra_args)
        timeout = timeout or tool.timeout
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            result = {"tool": name, "target": target, "returncode": proc.returncode,
                      "stdout": stdout.decode(errors="replace"),
                      "stderr": stderr.decode(errors="replace")}
            result["findings"] = tool.parse_func(result)
            return result
        except asyncio.TimeoutError:
            proc.kill()
            return {"error": f"Timeout after {timeout}s", "tool": name}
        except Exception as exc:
            return {"error": str(exc), "tool": name}
    def _register_all(self):
        tools = [
            SecurityTool("nikto","Web server scanner","web",["nikto","-h","{target}"],timeout=300),
            SecurityTool("dirsearch","Directory brute-forcer","web",["dirsearch","-u","{target}","-e","*"],timeout=600),
            SecurityTool("gobuster","Directory/DNS brute-forcer","web",["gobuster","dir","-u","{target}","-w","/usr/share/wordlists/dirb/common.txt"],timeout=600),
            SecurityTool("ffuf","Fast web fuzzer","web",["ffuf","-u","{target}/FUZZ","-w","/usr/share/wordlists/dirb/common.txt"],timeout=600),
            SecurityTool("dalfox","XSS scanner","web",["dalfox","url","{target}"],timeout=300),
            SecurityTool("sqlmap","SQL injection scanner","web",["sqlmap","-u","{target}","--batch"],timeout=600),
            SecurityTool("commix","Command injection exploiter","web",["commix","-u","{target}","--batch"],timeout=300),
            SecurityTool("nuclei","Template-based vuln scanner","web",["nuclei","-u","{target}","-severity","critical,high,medium"],timeout=600),
            SecurityTool("wpscan","WordPress scanner","web",["wpscan","--url","{target}","--enumerate","u,p,t"],timeout=600),
            SecurityTool("joomscan","Joomla scanner","web",["joomscan","-u","{target}"],timeout=300),
            SecurityTool("whatweb","Tech identifier","web",["whatweb","{target}","-a","3"],timeout=60),
            SecurityTool("wafw00f","WAF fingerprinting","web",["wafw00f","{target}"],timeout=60),
            SecurityTool("nmap","Network mapper","network",["nmap","-sV","-sC","-T4","-p-","{target}"],timeout=600),
            SecurityTool("nmap_quick","Fast port scan","network",["nmap","-sV","-T4","{target}"],timeout=300),
            SecurityTool("naabu","Fast port scanner","network",["naabu","-host","{target}"],timeout=300),
            SecurityTool("masscan","Mass port scanner","network",["masscan","{target}","-p1-65535","--rate=1000"],timeout=300),
            SecurityTool("dnsx","DNS toolkit","network",["dnsx","-d","{target}","-a","-aaaa","-cname","-mx"],timeout=120),
            SecurityTool("subfinder","Subdomain discovery","osint",["subfinder","-d","{target}","-all"],timeout=300),
            SecurityTool("amass","OSINT enumeration","osint",["amass","enum","-passive","-d","{target}"],timeout=600),
            SecurityTool("findomain","Subdomain enumerator","osint",["findomain","-t","{target}"],timeout=300),
            SecurityTool("assetfinder","Domain finder","osint",["assetfinder","--subs-only","{target}"],timeout=120),
            SecurityTool("chaos","Chaos data discovery","osint",["chaos","-d","{target}"],timeout=120),
            SecurityTool("theharvester","Email/subdomain OSINT","osint",["theharvester","-d","{target}","-b","all"],timeout=300),
            SecurityTool("sublist3r","Subdomain enumerator","osint",["sublist3r","-d","{target}"],timeout=120),
            SecurityTool("hydra","Login cracker","password",["hydra","-L","/usr/share/wordlists/users.txt","-P","/usr/share/wordlists/passwords.txt","{target}","http-post-form"],timeout=600),
            SecurityTool("ncrack","Auth cracker","password",["ncrack","-p","80,443","{target}"],timeout=600),
            SecurityTool("hashcat","GPU hash cracker","password",["hashcat","-m","0","{target}","/usr/share/wordlists/rockyou.txt"],timeout=600),
            SecurityTool("cewl","Custom wordlist gen","password",["cewl","{target}","-d","3","-m","6"],timeout=120),
            SecurityTool("prowler_aws","AWS security scanner","cloud",["prowler","aws","--severity","critical,high"],timeout=600),
            SecurityTool("scout_suite","Multi-cloud audit","cloud",["scout","aws"],timeout=600),
            SecurityTool("arjun","HTTP parameter discovery","api",["arjun","-u","{target}"],timeout=300),
            SecurityTool("paramspider","Parameter mining","api",["paramspider","-d","{target}"],timeout=300),
            SecurityTool("x8","Hidden parameter discovery","api",["x8","-u","{target}"],timeout=300),
            SecurityTool("graphqlmap","GraphQL injector","api",["graphqlmap","-u","{target}"],timeout=300),
            SecurityTool("checksec","Binary security check","binary",["checksec","--file={target}"],timeout=60),
            SecurityTool("apktool","Android decompiler","binary",["apktool","d","{target}"],timeout=120),
            SecurityTool("jadx","Android decompiler","binary",["jadx","-d","{target}_jadx","{target}"],timeout=120),
            SecurityTool("searchsploit","Exploit-DB search","exploit",["searchsploit","{target}"],timeout=60),
            SecurityTool("routersploit","Router exploiter","exploit",["rsf","{target}"],timeout=300),
            SecurityTool("nosqlmap","NoSQL injection","exploit",["nosqlmap","-t","{target}"],timeout=300),
            SecurityTool("ssrfmap","SSRF toolkit","exploit",["ssrfmap","-u","{target}"],timeout=300),
            SecurityTool("smuggler","HTTP smuggling toolkit","exploit",["smuggler","-u","{target}"],timeout=300),
            SecurityTool("trufflehog","Secret scanner","osint",["trufflehog","git","{target}","--json"],timeout=300),
            SecurityTool("gitleaks","Git secret scanner","osint",["gitleaks","detect","--source","{target}","--verbose"],timeout=300),
            SecurityTool("katana","Fast crawler","web",["katana","-u","{target}","-jc","-d","3"],timeout=300),
            SecurityTool("gau","Get All URLs","web",["gau","--subs","{target}"],timeout=120),
            SecurityTool("waybackurls","Wayback URLs","web",["waybackurls","{target}"],timeout=120),
        ]
        for t in tools: self.register(t)
        logger.info("tools_registered", total=self.total_count, installed=self.installed_count)

_registry = None
def get_registry():
    global _registry
    if _registry is None: _registry = ToolRegistry()
    return _registry
