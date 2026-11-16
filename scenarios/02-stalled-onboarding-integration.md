# Stalled onboarding: CRM integration blocker

## What a strong answer does

- Identifies the likely technical cause (field mapping / picklist value mismatch, permissions, or the sync user) instead of generic "contact support"
- Gives troubleshooting steps in a sensible order, cheapest checks first
- Proposes a way to unblock value now (partial go-live) while the integration is fixed
- Resets expectations with the customer honestly, without blaming them
- Notices the risk that the go-live slip threatens the customer's own internal deadline

## Prompt

You are the CSM for Brightline Dental Group, a chain of 35 dental clinics. They bought Tidewell (a B2B workflow management platform) 7 weeks ago to manage patient-referral workflows between clinics. Go-live was planned for week 6 and has slipped.

Situation:
- The blocker is the Salesforce integration. Referral records created in Tidewell should create Opportunity records in Salesforce
- About 60% of sync attempts fail with the error: "INVALID_OR_NULL_FOR_RESTRICTED_PICKLIST: Referral Source: bad value for restricted picklist field"
- The other 40% sync fine
- Their Salesforce admin, Marco, is part-time and contracted, available Tuesdays and Thursdays only
- In Tidewell, the "Referral Source" field is a free-text field that clinic staff fill in
- The customer's project lead, Lena, emailed yesterday: "We told our board this would be live by the end of the month. I'm starting to question whether this was the right purchase."
- End of the month is 16 days away

Give me:
1. What you think is causing the failures and how to confirm it
2. A step-by-step fix plan, including who does what
3. A plan to still show value before the end of the month
4. A reply to Lena
