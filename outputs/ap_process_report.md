# Accounts Payable Duplicate Payment Detection Report

## Executive Overview

This report summarizes the process-mining analysis of the invoice-to-pay workflow and highlights duplicate and rogue payment risks.

## Key Metrics

- Total invoices analyzed: 1200
- Duplicate payment candidates: 43
- Rogue / unauthorized payments: 12
- Invoices with skipped approval: 18
- Looping invoice cases: 28
- Average activity lag: 15.8 hours
- Approval-to-payment lag: 31.2 hours
- Top risky vendor: VENDOR_08

## Process Mining Interpretation

- PU_COUNT: 1200
- Case conformance rate: 91.33%
- Loop rate: 2.33%

## Risk Reasons

- Duplicate vendor-reference clustering
- Payment release without proper approval
- Repeated validation loops
- Delayed approval-to-payment flow

## Recommendation

Priority must be given to duplicate payment references, approval bypass events, and invoices with repeated looping activities.
