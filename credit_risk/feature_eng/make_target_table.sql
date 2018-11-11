

--to make training features
drop table if exists target_table;
create table target_table as
select * from application_train;

-- for testing / prod
drop table if exists target_table;
create table target_table as
select * from application_test;