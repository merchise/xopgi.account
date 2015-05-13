## -*- coding: utf-8 -*-
<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            ${css}

            .list_table .act_as_row {
                margin-top: 10px;
                margin-bottom: 10px;
                font-size:10px;
            }

            .account_line {
                font-weight: bold;
                font-size: 15px;
                background-color:#F0F0F0;
            }

            .account_line .act_as_cell {
                height: 30px;
                vertical-align: bottom;
            }

        </style>
    </head>
    <body>
        <%!
        def amount(text):
            return text.replace('-', '&#8209;')  # replace by a non-breaking hyphen (it will not word-wrap between hyphen and numbers)

        def display_line(all_comparison_lines):
            return any([line.get('balance') for line in all_comparison_lines])
        %>

        <%setLang(user.lang)%>

        <%
        initial_balance_text = {'initial_balance': _('Computed'), 'opening_balance': _('Opening Entries'), False: _('No')}
        %>

        <div class="act_as_table data_table">
            <div class="act_as_row labels">
                <div class="act_as_cell">${_('Chart of Account')}</div>
                <div class="act_as_cell">${_('Fiscal Year')}</div>
                <div class="act_as_cell">
                    %if filter_form(data) == 'filter_date':
                        ${_('Dates Filter')}
                    %else:
                        ${_('Periods Filter')}
                    %endif
                </div>
                <div class="act_as_cell">${_('Accounts Filter')}</div>
                <div class="act_as_cell">${_('Partners Filter')}</div>
                <div class="act_as_cell">${_('Target Moves')}</div>
                <div class="act_as_cell">${_('Initial Balance')}</div>
            </div>
            <div class="act_as_row">
                <div class="act_as_cell">${ chart_account.name }</div>
                <div class="act_as_cell">${ fiscalyear.name if fiscalyear else '-' }</div>
                <div class="act_as_cell">
                    ${_('From:')}
                    %if filter_form(data) == 'filter_date':
                        ${formatLang(start_date, date=True) if start_date else u'' }
                    %else:
                        ${start_period.name if start_period else u''}
                    %endif
                    ${_('To:')}
                    %if filter_form(data) == 'filter_date':
                        ${ formatLang(stop_date, date=True) if stop_date else u'' }
                    %else:
                        ${stop_period.name if stop_period else u'' }
                    %endif
                </div>
                <div class="act_as_cell">
                    %if accounts(data):
                        ${', '.join([account.code for account in accounts(data)])}
                    %else:
                        ${_('All')}
                    %endif
                </div>
                <div class="act_as_cell">${display_partner_account(data)}</div>
                <div class="act_as_cell">${ display_target_move(data) }</div>
                <div class="act_as_cell">${ initial_balance_text[initial_balance_mode] }</div>
            </div>
        </div>

        <%

        partners = {}
        currency_comp = currency_company

        %>
        %for current_account in objects:
            <% partners_in_account = partners_order_accounts[current_account.id] %>
##                <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1000px;">${currency_comp['currency_name']}</div>
                %for partner in partners_in_account:
                  %if partner[0]:
                     %if partner not in partners:
                          <% partners[partner] = [current_account] %>
                     %else:
                         <% partners[partner].append(current_account) %>
                     %endif
                  %endif
                %endfor
##                <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1000px;">${partners}</div>
        %endfor



##     %for current_account in objects:
##        <% partners_in_account = partners_order_accounts[current_account.id] %>
##            %for partner in partners_in_account:
##               ##Preg a manuel, pq no coge el none
##               %if partner[0] != "None":
##                   %if partner[0] not in partners:
##                      <% partners[partner[0]] = [current_account.id] %>
##                   %else:
##                      <% partners[partner[0]].append(current_account.id) %>
##                   %endif
##               %endif
##            %endfor
##     %endfor

       ## <% sorted(partners.keys())%>
##        <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 690px;">${ partners}</div>



        %for partner in sorted(partners):
            ##%for current_account in allaccounts:
                <%
                    total_initial_balance = 0.0
                    total_debit = 0.0
                    total_credit = 0.0
                    total_balance = 0.0


                   ## partners_order = partners_order_accounts[current_account.id]
                   ## (partner_code_name, partner_id, partner_ref, partner_name) in partners_order
                %>
                 ##   <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 690px;">${partner}</div>
##                partners_order = partners_order_accounts[current_account.id]
##
##                # do not display accounts without partners
##                if not partners_order:
##                    continue

                ##comparisons = comparisons_accounts[current_account.id]

##                # in multiple columns mode, we do not want to print accounts without any rows
##                if comparison_mode in ('single', 'multiple'):
##                    all_comparison_lines = [comp['partners_amounts'][partner_id[1]]
##                                          for partner_id in partners_order
##                                          for comp in comparisons]
##                    if not display_line(all_comparison_lines):
##                        continue
##
##                current_partner_amounts = partners_amounts_accounts[current_account.id]

##                    if comparison_mode in ('single', 'multiple'):
##                        comparison_total = {}
##                        for i, comp in enumerate(comparisons):
##                            comparison_total[i] = {'balance': 0.0}

           ## %endfor

           <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1080px;">${partner[0]}</div>
##           <div class="account_title bg" style="margin-top: 20px; font-size: 12px; width: 1080px;">${amount_currency(data)}</div>

           <div class="act_as_table list_table">

               <div class="act_as_thead">
                    <div class="act_as_row labels">
                        ## account name
                        <div class="act_as_cell" style="width: 80px;">${_('Account')}</div>
                        ## code
##                      <div class="act_as_cell first_column" style="width: 20px;">${_('Code / Ref')}</div>
                        ## debit
                        <div class="act_as_cell amount" style="width: 12px;">${_('Debit')}</div>
                        ## credit
                        <div class="act_as_cell amount" style="width: 12px;">${_('Credit')}</div>
                        ## currency balance
                        <div class="act_as_cell amount" style="width: 18px;">${_('Balance')}</div>

##                        %if comparison_mode == 'no_comparison' or not fiscalyear:
##                            ${_('Balance')}
##                        %else:
##                            ${_('Balance %s') % (fiscalyear.name,)}
##                        %endif
##                        </div>

                        %if amount_currency(data):
                            ## currency balance
##                            <div class="act_as_cell amount" style="width: 18px;">${_('Curr. Balance')}</div>
                            ## balance
##                            <div class="act_as_cell amount" style="width: 18px;">${_('Balance')}</div>
                            ## curency code
                            <div class="act_as_cell amount" style="width: 12px;">${_('Curr.')}</div>
##                        %else:
##                            <div class="act_as_cell amount" style="width: 18px;">${_('Balance')}</div>
##
                        %endif


                    </div>
               </div>

               <div class="act_as_tbody">



                   %for data_account in partners[partner]:


                        <%

                            data_partner_balance = partners_amounts_accounts[data_account['id']][partner[1]]
##                            a = partners_amounts_accounts[data_account['id']][partner[1]]['balance']
##                              a = partner

                        %>


                        <div class="act_as_row lines">

                            <div class="act_as_cell">${data_account.code} -${data_account.name}</div>

##                            <div class="act_as_cell">${data_account.code} - ${data_account.name}

##                                ${data_account. if data_account else _('Unallocated') }
##                            </div>

##                            <div class="act_as_cell">${partners_amounts_accounts[data_account.id][partner_id]} -${'prueba1'}</div>
##                            <div class="act_as_cell">${partners_amounts_accounts.get(data_account.id).get(partner_id)} -${'prueba2'}</div>

##                           <div class="act_as_cell">${data_account} -${'prueba1'}</div>


##                          <div class="act_as_cell amount">${data_partner_balance.get('currency_debit', 0.0)}</div>
                            <div class="act_as_cell amount">${data_partner_balance.get('currency_debit', 0.0)}</div>
                            <div class="act_as_cell amount">${data_partner_balance.get('currency_credit', 0.0)}</div>
                            <div class="act_as_cell amount">${data_partner_balance.get('balance_currency', 0.0)}</div>
                            %if amount_currency(data):
##                            <div class="act_as_cell" style="text-align: right; ">${data_account[account.id].get(p_id, [])}</div>
##                              <div class="act_as_cell amount">${60}</div>
                              <div class="act_as_cell amount">${data_partner_balance.get('currency_name') if data_partner_balance.get('currency_id') else currency_comp['currency_name']}</div>
                            %endif
                        </div>

                   %endfor




               </div>



           </div>



        %endfor






    </body>
</html>
