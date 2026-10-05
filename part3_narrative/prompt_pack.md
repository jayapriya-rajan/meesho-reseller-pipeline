# Prompt Pack

## Trigger
Use this if the output from is_flagged on a category is "flagged"

## Input list
{category}, {month}, {prev_month}, {previous_revenue}, {current_revenue}, {mom_pct}

## Prompt
Provide a brief update on {category} for the regional manager
The revenue for {prev_month} was {previous_revenue} and in {month} the revenue was {current_revenue}, representing a difference of {mom_pct} percent
Use the Context, Insight and Implication framework. Make sure you use only the numbers that I have provided above.
Insight should be stated as a fact, and any hypotheses should be labeled as such
Make a specific recommendation at the end

## Checklist
1. All numbers used in the draft match those I provided
2. The name of the category and the percentage are both included
3. Fact or hypothesis is mentioned for each claim made
4. The recommendation specifies precisely what should be checked
5. Resellers are only mentioned as an alias and not by name