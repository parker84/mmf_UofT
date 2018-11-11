/*
Notice that payment and cc_history features are wrt
 */

drop table if exists historical_features_per_prev_app;

create table historical_features_per_prev_app as
  select previous_application."SK_ID_CURR" as sk_id_curr,
         previous_application."SK_ID_PREV" as sk_id_prev,
         "DAYS_TERMINATION"                as days_termination,
         "AMT_CREDIT"                      as amt_credit,
         "AMT_DOWN_PAYMENT"                as amt_down_payment,
         sum(SK_DPD)                       as total_num_days_past_due_cc,
         max(SK_DPD)                       as max_num_days_past_due_cc,
         sum(past_due)                     as num_times_dpd,
         sum(over_max_on_cc)               as num_times_over_max_cc,
         sum(is_late)                      as num_late_payments,
         sum(underpaid)                    as num_times_underpaid,
         case
           when count(is_late) > 10  --count wont count nulls
                   then avg(is_late)
           else null end                   as prop_late_payments,
         case
           when count(underpaid) > 10
                   then avg(underpaid)
           else null end                   as prop_underpaid_payments,
         case
           when count(over_max_on_cc) > 5
                   then avg(over_max_on_cc)
           else null end                   as prop_maxout_cc,
         count("SK_ID_CURR")               as num_payments
  from previous_application as previous_application
         left join payment_features as payments on previous_application."SK_ID_PREV" = payments.SK_ID_PREV
         left join cc_history_features as cc_history on previous_application."SK_ID_PREV" = cc_history.SK_ID_PREV
  group by previous_application."SK_ID_PREV", previous_application."DAYS_TERMINATION",
           previous_application."AMT_CREDIT", previous_application."AMT_DOWN_PAYMENT",
           previous_application."SK_ID_CURR";

