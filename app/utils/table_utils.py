from app.models.master_account import MasterAccount
from app.models.child_account import ChildAccount


def get_table_values(table_columns, accounts):
    table_values = []
    for account in accounts:
        table_info = {}
        try:
            summary = account.brokerage.get_summary()['account']
            if isinstance(account, MasterAccount):
                role = 'master'
            elif isinstance(account, ChildAccount):
                role = 'child'
        except:
            print(f"Error getting summary for account: {account.account_id}")
        for column in table_columns:
            if column == 'status':
                    table_info['status'] = 'Active' if summary is not None else 'Disconnected'
            elif column == 'account id':
                table_info['accountId'] = account.account_id
            elif column == 'custom name':
                custom_name = account.custom_name
                table_info['customName'] = custom_name
            elif column == 'balance':
                table_info['balance'] = "{:,.1f}".format(float(summary['balance']))
            elif column == 'equity':
                        #print("ADD EQUITY BACKEND")
                table_info['equity'] = '---'
            elif column == 'open trades':
                table_info['openTrades'] = summary['openTradeCount']
            elif column == 'open pl':
                        # print("ADD OPEN PL BACKEND")
                table_info['openPl'] = '---'
            elif column == 'day pl':
                        # print("ADD DAY PL BACKEND")
                table_info['dayPl'] = '---'
            elif column == 'week pl':
                        # print("ADD WEEK PL BACKEND")
                table_info['weekPl'] = '---'
            elif column == 'month pl':
                        # print("ADD MONTH PL BACKEND")
                table_info['monthPl'] = '---'
            elif column == 'total pl':
                table_info['totalPl'] = float(summary['pl'])
            elif column == 'role':
                table_info['role'] = role
            elif column == 'master account name':
                if role == 'child':
                    for account_ in accounts:
                        if account_.account_id == account.master_account_id:
                            table_info['masterAccountName'] = account_.custom_name
                else:
                    table_info['masterAccountName'] = "---"
            elif column == 'risk type':
                if role == 'child':
                    table_info['riskType'] = account.get_risk_type()
                else:
                    table_info['riskType'] = "---"
            elif column == 'risk setting':
                if role == 'child':
                    table_info['riskSetting'] = account.get_risk_setting()
                else:
                    table_info['riskSetting'] = '---'
                    # elif column == '':
                    #     table_info[column] = account['']
            else:
                print('got unexpected column:', column)
        table_values.append(table_info)
    return table_values
