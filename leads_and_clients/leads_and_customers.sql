SELECT * FROM customers;

SELECT * FROM leads;

SELECT CONCAT(customers.first_name,' ', customers.last_name) AS full_name, customers.client_id, count(leads.leads_id) 
AS quant, leads.customer_id FROM customers LEFT JOIN leads ON leads.customer_id = customers.client_id GROUP BY customers.client_id;


