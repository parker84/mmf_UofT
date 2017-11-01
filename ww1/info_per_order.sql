/*get info per order*/

IF OBJECT_ID('feature_table_per_order') IS NOT NULL DROP TABLE feature_table_per_order;

select
	t1.OrderID, t1.OrderDate, t1.ExpectedDeliveryDate,
	order_year = year(t1.OrderDate),
	order_month = month(t1.OrderDate),
	order_wk = datepart(wk, t1.OrderDate),
	order_year_month = (100*year(t1.OrderDate)) + month(t1.OrderDate),
	order_year_wk = (100*year(t1.OrderDate)) + datepart(wk, t1.OrderDate),
	 t2.StockItemID, t2.Description, t2.UnitPrice, t2.Quantity, 
	 t2.UnitPrice * t2.Quantity as total_rev,
	 t1.CustomerID,
	t3.CustomerName, t4.CustomerCategoryID, t4.CustomerCategoryName, 
	t1.SalespersonPersonID, t5.IsEmployee, t5.FullName, 
	t6.CityName, t7.StateProvinceName,
	t8.CountryName, t6.CityID, t7.StateProvinceID,
	t8.CountryID
into feature_table_per_order
from Sales.Orders as t1
inner join Sales.OrderLines as t2
  on t1.OrderID = t2.OrderID
inner join Sales.Customers as t3
	on t3.CustomerID = t1.CustomerID
inner join Sales.CustomerCategories as t4
	on t4.CustomerCategoryID = t3.CustomerCategoryID
inner join Application.People as t5
	on t5.PersonID = t1.SalespersonPersonID
inner join Application.Cities as t6
	on t3.DeliveryCityID = t6.CityID
inner join Application.StateProvinces as t7
	on t7.StateProvinceID = t6.StateProvinceID
inner join Application.Countries as t8
	on t7.CountryID = t8.CountryID
order by t1.OrderID;

select top 10 * from feature_table_per_order;


select count( distinct order_year_month) from feature_table_per_order;
select count( distinct order_year_wk) from feature_table_per_order;

/*lookout for duplicated rows because of joins
- heres one way you can introduce bias into your model
- this can happen from duplicates in a key youre joining on
*/
select count(*) from feature_table_per_order;
select count(*) from Sales.Orders;
/*duplicates*/
select count(distinct OrderID), count(*)
from Sales.Orders;
select count(distinct OrderID), count(*) 
from Sales.OrderLines;
select count(distinct CustomerID), count(*) 
from Sales.Customers;
select count(distinct CustomerCategoryID), count(*) 
from Sales.CustomerCategories;
select count(distinct PersonID), count(*) 
from Application.People;
select count(distinct StateProvinceID), count(*) 
from Application.StateProvinces;
select count(distinct CountryID), count(*) 
from Application.Countries;

/*duplicate rows in orderlines*/
select top 10 * from Sales.OrderLines;
/*because we can have multiple products per order
- we have to aggregate per order*/

select 
	OrderID, OrderDate, ExpectedDeliveryDate,
	order_year = year(t1.OrderDate),
	order_month = month(t1.OrderDate),
	order_wk = datepart(wk, t1.OrderDate),
	order_year_month = (100*year(t1.OrderDate)) + month(t1.OrderDate),
	order_year_wk = (100*year(t1.OrderDate)) + datepart(wk, t1.OrderDate), 
	 sum(total_rev) as order_rev,
	 CustomerID,
	CustomerName, CustomerCategoryID, CustomerCategoryName, 
	t1.SalespersonPersonID, IsEmployee, FullName, 
	CityName, StateProvinceName,
	CountryName, CityID, StateProvinceID,
	CountryID
into feature_table_total_per_order
from feature_table_per_order as t1
group by 
	OrderID, OrderDate, ExpectedDeliveryDate, CustomerID,
	CustomerName, CustomerCategoryID, CustomerCategoryName, 
	t1.SalespersonPersonID, IsEmployee, FullName, 
	CityName, StateProvinceName,
	CountryName, CityID, StateProvinceID,
	CountryID;


select count(*) from feature_table_total_per_order;
select count(*) from Sales.Orders;

/*better*/