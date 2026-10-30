# Bring the listed helpers from datetime into this file.
from datetime import date
# Bring the listed helpers from pathlib into this file.
from pathlib import Path
# Import os so this file can use its functions and classes.
import os
# Import importlib so this file can use its functions and classes.
import importlib
# Import streamlit so this file can use its functions and classes.
import streamlit as st
# Bring the listed helpers from services.core into this file.
from services.core import Store, seed
# Refresh stateless UI helpers when their source changes, including on servers
# whose file watcher keeps imported modules cached. Financial services stay loaded.
refresh_dependents=False
for module_name in ['components.financial_widgets','components.design','components.spending_speed','screens.capture','screens.pages','components.shell']:
    ui_module=importlib.import_module(module_name)
    # Read the helper file modification time to detect source changes.
    source_stamp=Path(ui_module.__file__).stat().st_mtime_ns
    if refresh_dependents or getattr(ui_module,'_ui_source_stamp',None)!=source_stamp:
        # Reload an updated UI helper so the next render uses its latest code.
        importlib.reload(ui_module)
        # Read the helper file modification time to detect source changes.
        ui_module._ui_source_stamp=source_stamp
        refresh_dependents=True
# Bring the listed helpers from screens.pages into this file.
from screens.pages import dashboard, transactions, documents, knowledge, chat
# Bring the listed helpers from screens.capture into this file.
from screens.capture import open_capture, request_capture
# Bring the listed helpers from components.design into this file.
from components.design import apply_theme, brand
# Bring the listed helpers from components.shell into this file.
from components.shell import topbar, mobile_nav

# Set the browser-tab name, icon and wide page layout.
st.set_page_config(page_title='SmartBudget JA', page_icon='◈', layout='wide')
# Check whether cloud_app.py launched this as an isolated online practice session.
cloud_demo=globals().get('CLOUD_DEMO',False)
if cloud_demo:
    # Import tempfile so this file can use its functions and classes.
    import tempfile
    # Check the remembered session state before showing or running this section.
    if '_cloud_workspace' not in st.session_state:
        st.session_state['_cloud_workspace']=tempfile.TemporaryDirectory(prefix='smartbudget-session-')
        from services.demo_data import initialize_demo
        initialize_demo(Store(st.session_state['_cloud_workspace'].name), Path(__file__).parent / 'demo_data')
    store=Store(st.session_state['_cloud_workspace'].name)
else:
    # Choose the persistent data folder; SMARTBUDGET_DATA can override the default.
    store = Store(os.environ.get('SMARTBUDGET_DATA', str(Path(__file__).parent / 'data')))
# Start the cloud demo on the sample month so its example records are visible.
default_month=date.today().strftime('%Y-%m')
if cloud_demo:
    demo_rows=store.load('transactions')
    if demo_rows: default_month=max(row['date'][:7] for row in demo_rows)
for key, value in {'screen': 'Dashboard', 'month': default_month, 'theme': 'Dark', 'messages': [], 'quick_type': 'Income'}.items():
    # Initialise this session value only if it does not already exist; preserve it across reruns.
    st.session_state.setdefault(key, value)
# Handle expected failures here so the app can show a readable error.
try:
    seed(store)
    # Put the following controls inside st.sidebar.
    with st.sidebar:
        brand()
        st.radio('Navigate', ['Dashboard', 'Income & Expenses', 'Documents', 'Knowledge Base', 'Ask SmartBudget'], key='screen',label_visibility='collapsed',format_func=lambda x:{'Dashboard':'⌂   Dashboard','Income & Expenses':'▧   Income & Expenses','Documents':'▤   Receipts & Documents','Knowledge Base':'▣   Knowledge Base','Ask SmartBudget':'✧   Ask SmartBudget'}[x])
        # Navigate to the dashboard and open the requested budget or savings manager.
        def open_finance_panel(panel):
            st.session_state.screen='Dashboard'
            st.session_state.manage_finances=True
            st.session_state.pop('budget_open',None)
            st.session_state.pop('contribution_open',None)
            st.session_state.savings_open=panel=='Goals'
            if panel=='Budgets': st.session_state.budget_open=True
        # Put the following controls inside st.container(key='sidebar_analytics').
        with st.container(key='sidebar_analytics'):
            st.caption('ANALYTICS')
            # Draw an action button; on_click specifies what happens when it is pressed.
            st.button('Budgets',icon=':material/account_balance_wallet:',on_click=open_finance_panel,args=('Budgets',),width='stretch')
            # Draw an action button; on_click specifies what happens when it is pressed.
            st.button('Savings goals',icon=':material/flag:',on_click=open_finance_panel,args=('Goals',),width='stretch')
            # Draw an action button; on_click specifies what happens when it is pressed.
            st.button('Transaction history',icon=':material/bar_chart:',on_click=lambda:st.session_state.update(screen='Income & Expenses'),width='stretch')
        st.divider()
        st.caption('Single-user • Local storage • JMD')
        # Import json so this file can use its functions and classes.
        import json
        # Offer a file download without changing the financial records.
        st.download_button('Export all records', json.dumps({k: store.load(k) for k in ['transactions', 'budgets', 'goals', 'documents', 'knowledge', 'settings']}, indent=2), 'smartbudget-backup.json', 'application/json')
    # Force dark mode; there is no light-mode selector.
    st.session_state.theme = 'Dark'
    apply_theme(False)
    # Put the following controls inside st.container(key='mobile_brand').
    with st.container(key='mobile_brand'):
        brand()
    topbar(store)
    # Check the remembered session state before showing or running this section.
    if st.session_state.get('notice'):
        st.success(st.session_state.pop('notice'))
    # Look up the selected screen function and call it with the shared data store.
    {'Dashboard': dashboard, 'Income & Expenses': transactions, 'Documents': documents, 'Knowledge Base': knowledge, 'Ask SmartBudget': chat}[st.session_state.screen](store)
    mobile_nav()
    open_capture(store)
# Catch this type of failure instead of continuing with invalid data.
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.info('Your original files have been preserved. Check data files and folder permissions before retrying.')


