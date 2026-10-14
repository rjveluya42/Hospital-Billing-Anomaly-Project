-- Run against results/billing_analysis.sqlite using a SQLite client.
SELECT review_reason, COUNT(*) AS records FROM billing_records GROUP BY review_reason ORDER BY records DESC;

SELECT "Insurance Provider", COUNT(*) AS total, SUM(needs_review) AS flagged
FROM billing_records GROUP BY "Insurance Provider" ORDER BY flagged DESC;

SELECT "Medical Condition", ROUND(AVG("Billing Amount"), 2) AS average_charge
FROM billing_records WHERE "Billing Amount" >= 0 GROUP BY "Medical Condition";
