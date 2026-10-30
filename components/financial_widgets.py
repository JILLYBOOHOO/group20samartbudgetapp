"""Supported Streamlit v2 financial display; Python owns all monetary values."""
# Bring the listed helpers from pathlib into this file.
from pathlib import Path
# Import streamlit so this file can use its functions and classes.
import streamlit as st
# Bring the listed helpers from services.core into this file.
from services.core import money

# Register and cache the custom visual card component.
@st.cache_resource
def renderer(css,js):
    root=Path(__file__).parent
    return st.components.v2.component("financial_glass",html='<section class="money-grid" aria-label="Financial overview"></section>',css=css,js=js)

# Prepare formatted amounts and chart history for the custom financial cards.
def financial_cards(items,light=False,history=None,progress=0):
    root=Path(__file__).parent
    return renderer((root/'financial_widgets.css').read_text(),(root/'financial_widgets.js').read_text())(data={"light":light,"history":history or {},"progress":progress,"items":[dict(tone=t,icon=i,label=l,cents=v,formatted=money(v),note=n) for t,i,l,v,n in items]},key="financial_overview",on_add_record_change=lambda:None)
