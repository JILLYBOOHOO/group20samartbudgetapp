"""Parse receipt fields conservatively; never treat an address/item price as a total."""
import re
from datetime import datetime
from decimal import Decimal


def receipt_draft(text):
    from services.capture import suggest
    draft=suggest('',kind='Expense')
    lines=[re.sub(r'\s+',' ',line).strip() for line in text.splitlines() if line.strip()]
    clean=re.sub(r'\b(sub)?tota[ \t]*[i1|](?!\w)',lambda m:(m.group(1) or '')+'total',text,flags=re.I)
    total=None; subtotal=None; tax=None; raw_total=None; notes=[]
    def number(value):
        value=value.strip()
        # Tesseract often reads a small decimal point as a comma. Exactly two
        # trailing digits denote cents; a three-digit group remains thousands.
        if re.fullmatch(r'\d+,\d{2}',value): value=value.replace(',','.')
        if not re.fullmatch(r'(?:\d+|\d{1,3}(?:,\d{3})+)\.\d{2}',value): return None
        return Decimal(value.replace(',',''))
    # Restrict amounts to labelled receipt lines. Never use the first dollar price.
    for line in clean.splitlines():
        match=re.search(r'^\s*(grand\s+total|total(?:\s+(?:due|amount|payable))?|amount\s+due|sub\s*total|tax)\b\s*[:=]?\s*(?:JMD|JM?\s*[$S]|[$S])?\s*([\d,]+(?:[.,]\s*\d{2})?)\s*$',line,re.I)
        if not match: continue
        label,value=match.groups();value=value.replace(' ','');amount=number(value)
        if 'sub' in label.lower():subtotal=amount
        elif label.lower()=='tax':tax=amount
        else:raw_total=value;total=amount
    # A dropped decimal can be restored only when independently corroborated.
    if total is None and raw_total and raw_total.isdigit() and subtotal is not None and tax is not None:
        expected=subtotal+tax
        if Decimal(raw_total)/100==expected:
            total=expected;notes.append('OCR omitted the total decimal point; restored using subtotal plus tax.')
    if total is not None and subtotal is not None and tax is not None and total!=subtotal+tax:
        notes.append('The recognised total does not match subtotal plus tax. Confirm the original receipt.')
        total=None
    draft['amount_text']=f'{total:.2f}' if total is not None and total>0 else ''
    if not draft['amount_text']:notes.append('A reliable receipt total was not found. Enter it from the original; item prices were not used.')
    # Numeric receipt dates: use an unambiguous order, otherwise ask for review.
    match=re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b',text)
    date_found=False
    if match:
        a,b,year=map(int,match.groups())
        if a>12:order='%d/%m/%Y'
        elif b>12:order='%m/%d/%Y'
        else:order=None;notes.append('Receipt date order is ambiguous. Confirm day and month.')
        if order:
            try:draft['date']=datetime.strptime(f'{a}/{b}/{year}',order).date().isoformat();date_found=True
            except ValueError:pass
    iso=re.search(r'\b\d{4}-\d{2}-\d{2}\b',text)
    if iso:
        try:draft['date']=datetime.strptime(iso.group(),'%Y-%m-%d').date().isoformat();date_found=True
        except ValueError:pass
    if not date_found:notes.append('Receipt date was not confidently read; the form date needs your confirmation.')
    # Prefer a named merchant in the footer when a graphical logo was not read.
    merchant=re.search(r'thank\s+you\s+for\s+shopping\s+at\s+(.+?)(?:!|we\s+appreciate|$)',text,re.I|re.S)
    description=''
    if merchant:description=re.sub(r'\s+',' ',merchant.group(1)).strip(' .!')
    if not description:
        for line in lines[:5]:
            if re.search(r'\d|\b(street|road|city|state|zip|receipt|date|store|register)\b',line,re.I):continue
            if len(line)>2:description=line;break
    draft['description']=description or 'Receipt purchase'
    draft['extraction_notes']=notes
    return draft
