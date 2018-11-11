create table helper_features_per_curr_app as
  select min(prev_apps."AMT_CREDIT" - target_table."AMT_CREDIT") as min_credit_diff_prev_vs_current_app,
      --TODO: make a better similarity measure
         max(
           case
             when prev_apps."DAYS_TERMINATION" <= 0 --to remove the weird bias we were seeing here (see eda_app_table.ipynb)
                     then prev_apps."DAYS_TERMINATION"
             else null end
             )                                                   as closest_days_termination_to_curr_app,
         target_table."SK_ID_CURR",
         "SK_ID_PREV"
  from target_table as target_table
         left join previous_application as prev_apps on target_table."SK_ID_CURR" = prev_apps."SK_ID_CURR"
  group by target_table."SK_ID_CURR", "SK_ID_PREV";


create table historical_features_per_curr_app as
  select target_table."SK_ID_CURR",
         sum(cc_history.SK_DPD)         as total_num_days_past_due_cc_in_total,
         sum(cc_history.past_due)       as num_times_dpd_in_total,
         sum(cc_history.over_max_on_cc) as num_times_over_max_cc_in_total,
         sum(payments.is_late)          as num_late_payments_in_total,
         sum(payments.underpaid)        as num_times_underpaid_in_total
  from target_table as target_table
         left join payment_features as payments on target_table."SK_ID_CURR" = payments.SK_ID_CURR
         left join cc_history_features as cc_history on target_table."SK_ID_CURR" = cc_history.SK_ID_CURR
  group by target_table."SK_ID_CURR";


create table features_from_most_similar_prev_app as
  select cred_diff.*
  from (select prev_app.*, prev_app.AMT_CREDIT - target_table."AMT_CREDIT" as prev_app_cred_curr_app_cred_diff
        from target_table as target_table
               left join historical_features_per_prev_app as prev_app
                 on target_table."SK_ID_CURR" = prev_app.SK_ID_CURR) as cred_diff
         left join helper_features_per_curr_app as helpers
           on cred_diff.prev_app_cred_curr_app_cred_diff = helpers.min_credit_diff_prev_vs_current_app
                and cred_diff.SK_ID_CURR = helpers."SK_ID_CURR"
  where cred_diff.prev_app_cred_curr_app_cred_diff is not null;


create table features_from_most_recent_prev_app as
  select prev_app.*
  from historical_features_per_prev_app as prev_app
         left join helper_features_per_curr_app as helpers
           on prev_app.days_termination = helpers.closest_days_termination_to_curr_app and
              prev_app.SK_ID_CURR = helpers."SK_ID_CURR"
  where prev_app.days_termination is not null;


create table final_feature_table as
  select target_table."SK_ID_CURR",
         target_table."TARGET"                                          as target,
         total_num_days_past_due_cc_in_total,
         num_times_dpd_in_total,
         num_times_over_max_cc_in_total,
         num_late_payments_in_total,
         num_times_underpaid_in_total,
         features_from_most_recent_prev_app.total_num_days_past_due_cc  as total_num_days_past_due_cc_from_prev_app,
         features_from_most_recent_prev_app.num_times_dpd               as num_times_dpd_from_prev_app,
         features_from_most_recent_prev_app.num_times_over_max_cc       as num_times_over_max_cc_from_prev_app,
         features_from_most_recent_prev_app.num_late_payments           as num_late_payments_from_prev_app,
         features_from_most_recent_prev_app.num_times_underpaid         as num_times_underpaid_from_prev_app,
         features_from_most_similar_prev_app.total_num_days_past_due_cc as total_num_days_past_due_cc_from_prev_app_w_most_sim_cred,
         features_from_most_similar_prev_app.num_times_dpd              as num_times_dpd_from_prev_app_w_most_sim_cred,
         features_from_most_similar_prev_app.num_times_over_max_cc      as num_times_over_max_cc_from_prev_app_w_most_sim_cred,
         features_from_most_similar_prev_app.num_late_payments          as num_late_payments_from_prev_app_w_most_sim_cred,
         features_from_most_similar_prev_app.num_times_underpaid        as num_times_underpaid_from_prev_app_w_most_sim_cred
  from target_table as target_table
         left join historical_features_per_curr_app as curr_app_features
           on target_table."SK_ID_CURR" = curr_app_features."SK_ID_CURR"
         left join features_from_most_recent_prev_app
           on target_table."SK_ID_CURR" = features_from_most_recent_prev_app.sk_id_curr
         left join features_from_most_similar_prev_app
           on target_table."SK_ID_CURR" = features_from_most_recent_prev_app.sk_id_curr;
