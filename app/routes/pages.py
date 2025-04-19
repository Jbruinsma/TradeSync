from flask import Blueprint, render_template, session, redirect, url_for
from app import user_db
from app.models.user import User

from app.forms.login_form import LoginForm
from app.forms.register_form import RegisterForm
from app.forms.brokerage_selection_form import BrokerageForm
from app.forms.oanda_account_info_form import NewOandaTradingAccount
from app.forms.master_account_form import MasterAccountForm
from app.forms.child_account_settings import ChildAccountSettingsForm
from app.forms.multiplier_settings import MultiplierSettings
from app.forms.fixed_lot_settings import FixedLotSettings

from app.models.brokerage.oanda_brokerage.oanda import OANDA
from app.models.master_account import MasterAccount
from app.models.child_account import ChildAccount


from app.utils.account_utils import get_accounts_sum, get_accounts_list, get_total_open_positions, format_value, format_growth
from app.utils.table_utils import get_table_values


page = Blueprint('page', __name__)


@page.route('/')
def index():
    session.clear()
    user_count = 0 if user_db.is_empty() else len(user_db._inorder_traversal(user_db.root))
    print(f'USER COUNT: {user_count}')
    return render_template('index.html', users_count=user_count)

@page.route('/login_portal', methods=['GET', 'POST'])
def login_portal():
    form = LoginForm()
    if form.validate_on_submit():
        print("FORM VALIDATED!")
        username = form.username.data
        password = form.password.data
        try:
            if user_db.contains(username) and user_db.search(username).val.verify_password(password):
                session.clear()
                session['username'] = username
                return redirect(url_for('page.dashboard'))
        except:
            return redirect(url_for('page.login_portal'))
    return render_template('loginPortal.html', form= form)

@page.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        if user_db.contains(username):
            return redirect(url_for('page.login_portal'))
        new_user = User(form.username.data, form.password.data)
        user_db.insert(username, new_user)
        session.clear()
        session['username'] = username
        return redirect(url_for('page.dashboard'))
    return render_template('registerPortal.html', form= form)

@page.route('/dashboard')
def dashboard():
    try:
        username = session['username']
        user = user_db.search(username).val
    except KeyError:
        return redirect(url_for('page.login_portal'))

    accounts = get_accounts_list(user)
    table_columns = ['status', 'custom name', 'balance', 'equity', 'open trades', 'open pl', 'day pl', 'week pl', 'month pl', 'total pl']
    table_info = get_table_values(table_columns, accounts)
    portfolio_value = format_value(user.get_portfolio_value())
    master_accounts_total, child_accounts_total = user.get_account_totals()

    # # DELETE LATER (EXPERIMENTAL)
    # for master_account in user.master_accounts.values():
    #     m_account = master_account
    #     order = master_account.brokerage.get_pending_orders()['orders'][0]
    #     print(f"MASTER ACCOUNT ORDERS: {order}")
    # new_order = m_account.brokerage.store_pending_orders(order['id'], order['instrument'], order['units'], order['type'], order['price'], order['stopLossOnFill']['price'], order['takeProfitOnFill']['price'])
    # new_order.compare(order)

    return render_template('dashboard.html',
                            account_username= username,
                            account_portfolio_value= portfolio_value,
                            user_master_accounts_total= master_accounts_total,
                            user_child_accounts_total= child_accounts_total,
                            accounts= table_info)

@page.route('/accounts')
def accounts():
    try:
        username = session['username']
        user = user_db.search(username).val
    except KeyError:
        return redirect(url_for('page.login_portal'))

    accounts = get_accounts_list(user)
    table_columns = ['status', 'account id', 'custom name', 'balance', 'role']
    table_info = get_table_values(table_columns, accounts)
    print(table_info)
    return render_template('accounts.html', accounts= table_info, account_username = username)

@page.route('/add_account_portal')
def add_account_portal():
    
    try:
        username = session['username']
    except KeyError:
        return redirect(url_for('page.login_portal'))

    if 'oanda_account_info' in session:
        session.pop('oanda_account_info')
    if 'new_child_account_settings' in session:
        session.pop('new_child_account_settings')
    if 'fixed_lot' in session:
        session.pop('fixed_lot')
    if 'multiplier_factor' in session:
        session.pop('multiplier_factor')

    return render_template('addAccountPortal.html', account_username = username)

@page.route('/add_account/brokerage/<string:account_role>', methods=['GET', 'POST'])
def brokerage_selection(account_role):
    form = BrokerageForm()
    if form.validate_on_submit():
        print(form.data)
        trading_account_role = account_role
        trading_account_brokerage = form.brokerage.data
        print(trading_account_role, trading_account_brokerage)
        return redirect(url_for('page.account_info', account_role= str(trading_account_role), brokerage= str(trading_account_brokerage)))
    return render_template('brokerageSelection.html', form= form,)

@page.route('/account_info/<string:account_role>/<string:brokerage>', methods=['GET', 'POST'])
def account_info(account_role, brokerage):
    if brokerage == 'oanda':
        form= NewOandaTradingAccount()
    if form.validate_on_submit():
        print(form.data)
        session['trading_account_info'] = form.data
        session['trading_account_info']['brokerage'] = brokerage

        if account_role == 'child':
            return redirect(url_for('page.add_child_account', brokerage= brokerage))
        elif account_role == 'master':
            return redirect(url_for('page.add_master_account', brokerage= brokerage))
    return render_template('accountInfo.html', account_role = account_role, brokerage= brokerage, form= form)

@page.route('/add_master_account/<string:brokerage>', methods=['GET', 'POST'])
def add_master_account(brokerage):
    try:
        username = session['username']
    except KeyError:
        return redirect(url_for('page.login_portal'))
    
    form = MasterAccountForm()

    if form.validate_on_submit():
        try:
            new_account_info = session['trading_account_info']
        except KeyError:
            return redirect(url_for('page.login_portal'))

        user = user_db.search(username).val
        if user is None:
            return redirect(url_for('page.login_portal'))
        else:
            user.register_master_account(new_account_info, form)
            user_db.update(username, user)
            session.clear()
            session['username'] = username
            return redirect(url_for('page.dashboard'))

    return render_template('addMasterAccount.html', form=form, brokerage=brokerage, account_username=username)

@page.route('/add_child_account/<string:brokerage>', methods=['GET', 'POST'])
def add_child_account(brokerage):

    try:
        username = session['username']
    except KeyError:
        return redirect(url_for('page.login_portal'))

    form = ChildAccountSettingsForm()

    if form.validate_on_submit():
        session['new_child_account_settings'] = form.data
        if form.data['risk_type'] == 'fixed':
            return redirect(url_for('page.add_child_account_fixed_settings', brokerage= brokerage))
        elif form.data['risk_type'] == 'multiplier':
            return redirect(url_for('page.add_child_account_multiplier_settings', brokerage= brokerage))
        else:
            raise NameError(f'UNKNOWN RISK TYPE: "{form.data["risk_type"]}"')

    return render_template('addChildAccount.html', form= form, account_username = username)

@page.route('/add_child_account/risk_settings/multiplier_settings/<string:brokerage>', methods=['GET', 'POST'])
def add_child_account_multiplier_settings(brokerage):
    form = MultiplierSettings()

    if form.validate_on_submit():
        try:
            username = session['username']
            new_account_info = session['trading_account_info']
            new_child_account_settings = session['new_child_account_settings']
        except KeyError:
            return redirect(url_for('page.login_portal'))
        
        print(f'USERNAME: {username}')
        print(f'NEW ACCOUNT INFO: {new_account_info}')
        print(f'NEW CHILD ACCOUNT SETTINGS: {new_child_account_settings}')
        print(f'MULTIPLIER FACTOR: {form.data}')

        user = user_db.search(username).val
        if user is None:
            return redirect(url_for('page.login_portal'))
        else:

            success = user.register_child_account(new_account_info, new_child_account_settings, form.data)
            if success:
                user_db.update(username, user)
                session.clear()
                session['username'] = username
                return redirect(url_for('page.dashboard'))
            else:
                print("Error adding child account :(")

    return render_template('addChildRiskSettingsMultiplier.html',
                           form= form,
                           brokerage= brokerage)

@page.route('/add_child_account/risk_settings/fixed_settings/<string:brokerage>', methods=['GET', 'POST'])
def add_child_account_fixed_settings(brokerage):
    form = FixedLotSettings()
    if form.validate_on_submit():
        try:
            username = session['username']
            new_account_info = session['trading_account_info']
            new_child_account_settings = session['new_child_account_settings']
        except KeyError:
            return redirect(url_for('page.login_portal'))
        
        user = user_db.search(username).val
        if user is None:
            return redirect(url_for('page.login_portal'))
        else:
            user.register_child_account(new_account_info, new_child_account_settings, form.data)
            user_db.update(username, user)
            session.clear()
            session['username'] = username
            return redirect(url_for('page.dashboard'))

    return render_template('addChildRiskSettingsFixed.html',
                           form= form,
                           brokerage= brokerage)

@page.route('/view_account/<string:account_id>')
def view_account(account_id):
    try:
        username = session['username']
        user = user_db.search(username).val
        if account_id not in user.master_accounts:
            for master_account in user.master_accounts.values():
                if account_id not in master_account.child_account_ids:
                    return redirect(url_for('page.accounts'))
        trade_account = user.get_account(account_id)
        account_balance = trade_account.get_balance()
        formatted_account_balance = trade_account.format_balance()
        account_growth = trade_account.get_growth()
        formatted_account_growth = format_value(account_growth)
        account_growth_percentage = format_growth(account_balance, account_growth)
        open_positions = trade_account.get_open_positions()
        best_trade_pl = 0
        best_trade_pl_percentage = 0
    except KeyError:
        return redirect(url_for('page.login_portal'))
    
    return render_template('accountView.html',
                           account_id= account_id,
                           account_username= username,
                           formatted_account_balance= formatted_account_balance,
                           account_growth_percentage= account_growth_percentage, 
                           formatted_account_growth= formatted_account_growth,
                           open_positions= open_positions,
                           best_trade_pl= best_trade_pl,
                           best_trade_pl_percentage= best_trade_pl_percentage,
                           )
                        #    account_balance_val= account_balance_formatted,
                        #    account_pl_verb= account_pl_verb,
                        #    account_growth_val= account_growth,
                        #    account_pl_percentage= account_growth_percentage,
                        #    open_positions_val= open_positions,
                        #    account_username = username)

@page.route('/edit_account_settings/<string:account_id>', methods=['GET', 'POST'])
def edit_account_settings(account_id):
    try:
        username = session['username']
        user = user_db.search(username).val
        if account_id not in user.master_accounts:
            for master_account in user.master_accounts.values():
                if account_id not in master_account.child_account_ids:
                    return redirect(url_for('page.accounts'))
        trade_account = user.get_account(account_id)
        account_balance = trade_account.format_balance()
        custom_name = trade_account.custom_name
        account_api_key = trade_account.get_api_key()
    except KeyError:
        return redirect(url_for('page.login_portal'))

    if isinstance(trade_account, MasterAccount):
        general_account_info = {'accountOwner': username, 'accountEmail': "---", 'accountType': trade_account.brokerage.get_account_type()}
    elif isinstance(trade_account, ChildAccount):
        general_account_info = trade_account.get_account_info()

    if isinstance(trade_account, OANDA):
        brokerage = 'oanda'
    else:
        brokerage = 'unknown'

    return render_template('accountSettings.html',
                            account_name= custom_name,
                            account_id= account_id,
                            account_balance= account_balance,
                            account_equity= account_balance,
                            account_brokerage= brokerage,
                            account_info= general_account_info)

@page.route('/copier_settings')
def copier_settings():
    try:
        username = session['username']
        user = user_db.search(username).val
    except KeyError:
        return redirect(url_for('page.login_portal'))
    
    accounts = get_accounts_list(user)
    table_columns = ['custom name', 'account id', 'master account name', 'risk type', 'risk setting', 'role']
    table_info = get_table_values(table_columns, accounts)
    portfolio_value = format_value(user.get_portfolio_value())
    master_accounts_total, child_accounts_total = user.get_account_totals()
    total_open_positions = get_total_open_positions(user)

    return render_template('copierSettings.html', account_username= username, account_portfolio_value= portfolio_value, account_master_account_sum= master_accounts_total, account_child_account_sum= child_accounts_total, account_open_positions= total_open_positions, accounts= table_info)

@page.route('/copier_logs')
def copier_logs():
    try:
        username = session['username']
    except KeyError:
        return redirect(url_for('page.login_portal'))

    return render_template('copierLogs.html', account_username= username)

@page.route('/user_settings/<string:username>')
def user_settings(username):
    if not user_db.contains(username):
        return redirect(url_for('page.login_portal'))
    
    user = user_db.search(username).val
    join_date = user.get_formatted_join_date()
    accounts_sum = get_accounts_sum(user)
    open_trades_sum = 0
    
    return render_template('userSettings.html', account_username=username, account_join_date=join_date, user_account_amount=accounts_sum, user_account_open_trades_amount=open_trades_sum)

@page.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('page.index'))

