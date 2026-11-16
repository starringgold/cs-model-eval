# Portfolio triage from account data

## What a strong answer does

- Reads the numbers correctly (adoption = active users / seats, days to renewal)
- Catches Account E: usage looks fine, but the ticket spike plus the competitor mention make it high risk
- Does not over-prioritize Account H just because it is the biggest, since it is healthy
- Recognizes that Account C is low risk despite low adoption, because renewal is far out and the new rollout explains it
- Produces a clear ranked list with one concrete action per top account
- Flags what data is missing instead of inventing it

## Prompt

You manage a book of Tidewell accounts (a B2B workflow management platform). You have time for deep work on only 3 accounts this week. Here is your account data:

| Account | ARR | Seats | Weekly active users | Days to renewal | Support tickets last 30 days | Notes |
|---|---|---|---|---|---|---|
| A: Corvel Labs | $42,000 | 80 | 71 | 45 | 1 | Asked about adding SSO |
| B: Mirelle Foods | $18,000 | 40 | 14 | 30 | 0 | No reply to last 2 emails |
| C: Ostrava Health | $95,000 | 250 | 60 | 300 | 4 | Started rollout to 2nd region last month |
| D: Quinlan Legal | $12,000 | 25 | 22 | 20 | 0 | Renewal paperwork already sent back signed |
| E: Saltmarsh Energy | $64,000 | 120 | 104 | 75 | 11 | Admin mentioned in a ticket: "our IT team is comparing tools" |
| F: Tern & Co | $9,000 | 15 | 6 | 200 | 2 | Small team, owner is the only admin |
| G: Velda Retail | $51,000 | 100 | 48 | 90 | 3 | New executive sponsor joined 2 weeks ago |
| H: Brask Industries | $130,000 | 300 | 270 | 150 | 2 | Very happy, gave a G2 review last month |

Give me:
1. Your top 3 accounts for this week, ranked, with the reasoning for each
2. One concrete action for each of the top 3
3. Any accounts that look risky but that you are deliberately not prioritizing, and why
4. Any data you wish you had
