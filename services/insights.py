"""Explainable insights calculated from user records; no bank connection or predictions."""
# Bring the listed helpers from services.core into this file.
from services.core import period, previous, totals, categories, money, saved


# Calculate explainable insight cards from transactions, budgets and savings goals.
def build_insights(rows, budgets, goals, month):
    # Keep records for the selected reporting month.
    current=period(rows,month)
    # Keep records for the previous month as the comparison baseline.
    old=period(rows,previous(month))
    # Calculate income, expenses and their difference in integer cents.
    income,expense,net=totals(current)
    # Start the list of insight cards returned to the dashboard.
    feed=[]
    def add(kind,title,message,action,target):
        # Store the card category, heading, explanation, button label and navigation target.
        feed.append(dict(kind=kind,title=title,message=message,action=action,target=target))
    # Show a helpful starting message when this month has no records.
    if not current:
        add('Getting started','Your insights start here','Add an income or expense, or scan a receipt. Insights use only the records you provide.','Add expense','capture')
    # Evaluate each saved budget for the selected month.
    for b in budgets:
        # Ignore budgets for other months and invalid zero limits.
        if b['month']!=month or b['limit']<=0: continue
        # Use all expenses for an overall budget, or only the matching category.
        spent=expense if b['category']=='All spending' else categories(current).get(b['category'],0)
        # Subtract spending from the limit; a negative result means overspending.
        remaining=b['limit']-spent
        # Choose an over-budget, nearly-used (80%) or remaining-budget heading.
        title='Over budget' if remaining<0 else ('Budget nearly used' if spent/b['limit']>=.8 else 'Budget remaining')
        add('Budgets',title,f"{b['category']}: {money(spent)} of {money(b['limit'])} used ({spent/b['limit']:.0%}). {money(abs(remaining))} {'over the limit' if remaining<0 else 'remaining'}.",'Review budget','budget')
    if current:
        add('Spending','Your recorded cash flow',f'{money(income)} income minus {money(expense)} expenses = {money(net)} for {month}. This is not your bank balance or savings.','Review transactions','ledger')
    # Compare months only when both contain recorded activity.
    if current and old:
        old_expense=totals(old)[1]
        # Avoid dividing by zero when the previous month has no expenses.
        if old_expense:
            # Subtract the previous total from the selected total.
            difference=expense-old_expense
            add('Spending','Monthly spending comparison',f"Recorded expenses are {money(abs(difference))} {'higher' if difference>0 else 'lower' if difference<0 else 'different'} than {previous(month)} ({abs(difference)/old_expense:.0%}). Selected: {money(expense)}; previous: {money(old_expense)}. Whole recorded months are compared; either month may be incomplete.",'Compare transactions','ledger')
        # Calculate previous-month expense totals for each category.
        prior_categories=categories(old)
        # Check categories from highest selected-month spending to lowest.
        for category,amount in sorted(categories(current).items(),key=lambda item:item[1],reverse=True):
            # Look up the previous amount, or use zero if that category was absent.
            baseline=prior_categories.get(category,0)
            # Report an increase only when a positive baseline exists.
            if baseline and amount>baseline:
                add('Spending',category+' spending increased',f'{money(amount)} recorded versus {money(baseline)} in {previous(month)}: {money(amount-baseline)} more. This compares recorded totals, not matched dates or prices.','Review expenses','ledger')
                # Stop after the first qualifying category increase to keep the feed short.
                break
    # Create one progress card per savings goal.
    for goal in goals:
        # Read the target amount, using zero if it is missing.
        target=goal.get('target',0)
        # Skip invalid targets to prevent division by zero.
        if target<=0: continue
        # Add contributions across all dates for this goal.
        amount=saved(goal)
        add('Savings',goal['name']+' progress',f"{money(amount)} of {money(target)} contributed ({amount/target:.0%}). {money(max(target-amount,0))} left to reach this goal. Contributions cover all dates.",'Manage savings','savings')
    # Suggest a monthly limit when records exist but no overall budget is set.
    if current and not any(b['month']==month and b['category']=='All spending' for b in budgets):
        add('Budgets','Set a spending limit','A monthly budget lets you compare recorded expenses with your own limit.','Set budget','budget')
    # Return the completed list; this function does not save or modify records.
    return feed
