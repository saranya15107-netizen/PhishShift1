import re

PATTERNS=[
 ("urgency","HIGH",2.5,re.compile(r"\b(urgent|immediately|act now|within \d+\s*(hours?|minutes?)|expires today|final warning)\b",re.I)),
 ("credential_harvest","HIGH",3.0,re.compile(r"\b(verify (your )?(identity|account|password)|confirm (your )?(password|account)|login to restore|enter your password|sign in immediately)\b",re.I)),
 ("suspicious_url","HIGH",2.8,re.compile(r"https?://[^\s<>]+",re.I)),
 ("financial_threat","HIGH",2.4,re.compile(r"\b(account (is )?(locked|suspended|blocked)|payment (failed|required|overdue)|pay (a )?(fee|fine)|avoid (account )?closure)\b",re.I)),
 ("impersonation","MEDIUM",2.0,re.compile(r"\b(bank support|IT helpdesk|administrator|payroll department|security team|customer support)\b",re.I)),
 ("reward_bait","MEDIUM",2.0,re.compile(r"\b(you have won|claim your prize|free gift|selected winner|claim reward)\b",re.I)),
 ("secrecy_or_bypass","MEDIUM",1.8,re.compile(r"\b(keep this confidential|do not tell anyone|bypass normal process|gift cards urgently)\b",re.I)),
]
def extract_risk_cues(message):
    text=message or ""; found=[]
    for category,severity,weight,pattern in PATTERNS:
        match=pattern.search(text)
        if match: found.append({"category":category,"severity":severity,"weight":weight,"snippet":match.group(0)[:120]})
    return found
def normalize_template(message):
    text=(message or "").lower()
    text=re.sub(r"https?://\S+","<url>",text)
    text=re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b","<email>",text)
    text=re.sub(r"\b\d{4,}\b","<num>",text)
    text=re.sub(r"\b\d{1,2}:\d{2}\b","<time>",text)
    text=re.sub(r"[^\w\s<>]"," ",text)
    return re.sub(r"\s+"," ",text).strip()
