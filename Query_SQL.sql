--QUERY 1
select "Marital Status" , round(avg(age),0) as average_age
from customer
group by "Marital Status" 

--QUERY 2
select gender  , round(avg(age),0) as average_age
from customer
group by gender 

--QUERY 3
select s.storename, sum(t.qty) as total_quantity
from store s 
join "Transaction" t on s.storeid = t.storeid 
group by s.storename 
order by total_quantity desc 
limit 1

--QUERY 4
select p."Product Name", sum(t.totalamount) as total_sales
from product p 
join "Transaction" t on p.productid = t.productid 
group by p."Product Name" 
order by total_sales desc 
limit 1