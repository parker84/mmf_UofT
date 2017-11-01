/* most and least popular items?*/
IF OBJECT_ID('tempdb..#rev_per_item_t1') IS NOT NULL DROP TABLE #rev_per_item_t1;

select 
	count(*) as n, 
	ix = 1,
	sum(UnitPrice * Quantity) as tot_rev_per_item,
	StockItemID, Description, UnitPrice
into #rev_per_item_t1
from Sales.Orders as orders
inner join Sales.OrderLines as info
	on orders.OrderID = info.OrderID
group by 
	StockItemID, Description, UnitPrice;

select t1.*, tot_rev_per_item / tot_rev as prop_of_tot_rev
into #rev_per_item
from 
	#rev_per_item_t1 as t1
inner join 
	(select 
		sum(tot_rev_per_item) as tot_rev,
		ix = 1
	from #rev_per_item_t1) as t2
	on t1.ix = t2.ix
order by tot_rev desc;


select top 100 * from #rev_per_item;
select top 100 * from #rev_per_item
order by tot_rev_per_item;

/*geographic presence*/
/*top sales talent*/
/*exersizes, similar to above*/
