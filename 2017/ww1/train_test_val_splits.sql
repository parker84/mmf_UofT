/*train test val splits*/
IF OBJECT_ID('tempdb..#features_per_order_random') IS NOT NULL DROP TABLE #features_per_order_random;

select * 
into #features_per_order_random
from feature_table_total_per_order
order by newid();

select count(*) from feature_table_per_order;

select top 180000 *, 
into feature_table_train
from #features_per_order_random;

select * 
into feature_table_val
from #features_per_order_random
where row_id > 180000 and row_number() <210000;

select * 
into feature_table_test
from #features_per_order_random
where row_number() >=210000;


