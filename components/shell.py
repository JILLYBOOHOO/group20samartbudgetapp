# Bring the listed helpers from datetime into this file.
from datetime import date
# Import streamlit so this file can use its functions and classes.
import streamlit as st
# Bring the listed helpers from services.core into this file.
from services.core import previous
# Bring the listed helpers from screens.capture into this file.
from screens.capture import request_capture

# Change the current screen stored in this visitor session.
def navigate(screen):
    st.session_state.screen=screen

# Show search and reporting-month controls, then search the local records.
def topbar(store):
    months={st.session_state.month,date.today().strftime('%Y-%m')}
    cursor=date.today().strftime('%Y-%m')
    for _ in range(35):
        cursor=previous(cursor);months.add(cursor)
    months.update(r['date'][:7] for r in store.load('transactions'))
    months=sorted(months,reverse=True)
    # Put the following controls inside st.container(key='topbar').
    with st.container(key='topbar'):
        a,b=st.columns([3,1.3],vertical_alignment='bottom')
        query=a.text_input('Search SmartBudget',placeholder='Search transactions, receipts and knowledge…',key='global_search',label_visibility='collapsed',icon=':material/search:')
        selected=b.selectbox('Reporting month',months,index=months.index(st.session_state.month),format_func=lambda x:date.fromisoformat(x+'-01').strftime('%B %Y'),label_visibility='collapsed',key='reporting_month')
        st.session_state.month=selected
    if query.strip():
        q=query.strip().lower()
        collections=[('transactions','Income & Expenses',['description','category','source']),('documents','Documents',['name','text']),('knowledge','Knowledge Base',['title','text','topic'])]
        # Put the following controls inside st.expander('Search results',expanded=True).
        with st.expander('Search results',expanded=True):
            found=False
            for kind,screen,fields in collections:
                matches=[r for r in store.load(kind) if q in ' '.join(str(r.get(f,'')) for f in fields).lower()][:3]
                if matches:
                    found=True
                    st.caption(screen+' · '+' / '.join(str(r.get('description') or r.get('name') or r.get('title'))[:100] for r in matches))
                    # Draw an action button; on_click specifies what happens when it is pressed.
                    st.button('Open '+screen,key='global_'+kind,on_click=navigate,args=(screen,))
            if not found: st.caption('No matching local records. Try a category, merchant or source title.')

# Show compact navigation buttons for smaller screens.
def mobile_nav():
    """Supported native controls; shown below content on small screens, not fake HTML links."""
    # Put the following controls inside st.container(key='mobile_nav').
    with st.container(key='mobile_nav'):
        cols=st.columns(5)
        for col,label,screen in zip(cols,['Home','Ledger','Scan','Docs','Ask'],['Dashboard','Income & Expenses',None,'Documents','Ask SmartBudget']):
            if screen:
                col.button(label,key='mobile_'+label,on_click=navigate,args=(screen,),width='stretch')
            else:
                col.button('Scan receipt',key='mobile_Scan',on_click=request_capture,args=('Camera',),width='stretch',type='primary')
