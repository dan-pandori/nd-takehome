"""The secret patterns of rvl_hygiene.py."""
import re

PAT = re.compile(rb"(hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{30,}|"
                 rb"AKIA[0-9A-Z]{16}|rpa_[A-Za-z0-9]{20,}|[A-Z_]*(TOKEN|API_KEY|SECRET)[A-Z_]*\s*=\s*\S{8,}|"
                 rb"-----BEGIN [A-Z ]*PRIVATE KEY-----)")
