


create table payment_features as
select
  "SK_ID_CURR" as sk_id_curr,
  "SK_ID_PREV" as sk_id_prev,
  cast("DAYS_ENTRY_PAYMENT" > "DAYS_INSTALMENT" as int) as is_late,
  cast("AMT_PAYMENT" < "AMT_INSTALMENT" as int) as underpaid
from installments_payments;

drop table if exists cc_history_features;
create table cc_history_features as
select
  "SK_ID_CURR" as sk_id_curr,
  "SK_ID_PREV" as sk_id_prev,
  "SK_DPD" as sk_dpd,
  "MONTHS_BALANCE" as months_balance,
  cast("AMT_CREDIT_LIMIT_ACTUAL" <= "AMT_BALANCE" as int) as over_max_on_cc,
  cast("SK_DPD" > 0 as int) past_due,
   "AMT_CREDIT_LIMIT_ACTUAL" - "AMT_BALANCE" as cc_limit_minus_cc_amount
from credit_card_balance;