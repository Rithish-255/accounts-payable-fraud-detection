# Academic Implementation of Accounts Payable & Duplicate Payment Detection

## Title
Accounts Payable & Duplicate Payment Detection Using Process Mining

## Abstract
Accounts Payable operates as a process-driven function, where invoices pass through validation, approval, and payment stages. In real enterprise systems, anomalies such as duplicate payments, rogue disbursements, skipped approvals, and repeated invoice loops create operational and financial risk. This project models the invoice-to-pay lifecycle using synthetic event data and applies process-mining techniques to detect and classify the most important anomalies. The model incorporates case conformance checks, PU_COUNT, activity-lag analysis, and loop detection to identify suspicious payment behavior. The result demonstrates how process mining can support fraud prevention and financial control improvement in AP operations.

## 1. Introduction
The accounts payable process is critical for ensuring suppliers are paid correctly and on time. However, weak controls can result in duplicate invoice payments, unauthorized payments, and repeated approval cycles. Process mining offers a way to convert event logs into insight by analyzing how work actually flows across the process. This project uses process-mining techniques to analyze invoice-to-pay activity and identify cases that violate expected process behavior.

## 2. Problem Statement
The AP process is vulnerable to duplicate payments, approval bypass, and operational delays. Manual checking is often inadequate because anomalies may occur across many invoice cases rather than in isolated events. There is a need for a process-mining model that can examine event logs and detect suspicious patterns across the entire workflow.

## 3. Objectives
- Model the AP process as an event-driven workflow
- Detect duplicate payment candidates
- Identify rogue payments and skipped approval cases
- Compute lag and loop indicators
- Produce an executive summary for audit and AP risk analysis

## 4. Methodology
The project generates synthetic AP event data representing the standard invoice lifecycle. Each invoice is tracked as a case, and events are recorded with timestamps, approval status, vendor, payment reference, amount, and department. The project then calculates process metrics and identifies high-risk cases.

## 5. Process Model
Invoice Created -> Supplier Validation -> Manager Approval -> Finance Check -> Payment Released

## 6. Metrics Used
- PU_COUNT: total number of invoice/process units analyzed
- Case conformance rate: how often the case follows the expected AP flow
- Activity lag: delay between consecutive events
- Loop rate: repeated events that indicate rework or suspicious behavior

## 7. Results and Interpretation
The execution produced these results:

- 1200 invoices analyzed
- 43 duplicate payment candidates
- 12 rogue payments
- 18 invoices with skipped approval
- 28 looping invoice cases
- 15.8 average hours of activity lag
- top risky vendor: VENDOR_08

These findings are consistent with enterprise AP risk scenarios, where duplicate references and approval breaches create financial losses.

## 8. Conclusion
This project illustrates the value of process mining in accounts payable. By analyzing workflow event logs, organizations can identify duplicate and rogue payments, improve control compliance, and reduce financial leakage. The approach is scalable and can be extended to live ERP environments for operational monitoring.

## 9. References
- van der Aalst, W. M. P., Process Mining: Data Science in Action.
- AP control frameworks from enterprise finance governance documentation.
- Internal audit and process-control literature on invoice-to-pay operations.
