

create table cc_features_per_prev_id as
select
  count(*) as n
from cc_history_features
group by sk_id_prev;

select
  max(n),
  min(n),
  count(*), --104
  count(case when n > 5 --97
        then n else null end),
  count(case when n > 10 --76
        then n else null end)
--   percentile(n, .5)
from cc_features_per_prev_id;

create table payment_features_per_prev_id as
select
  count(*) as n
from payment_features
group by sk_id_prev;

select
  max(n),
  min(n),
  count(*), --997
  count(case when n > 5 --783
        then n else null end),
  count(case when n > 10 --429
        then n else null end),
  count(case when n > 50
          then n else null end)
--   percentile(n, .5)
from payment_features_per_prev_id;