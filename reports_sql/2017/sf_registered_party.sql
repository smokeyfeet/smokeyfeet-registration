select
    o.first_name,
    o.last_name,
    o.email,
    o.partner_name,
    o.partner_email,
    item.product_name,
    item.price
from minishop_order o
    join minishop_orderitem item on o.id = item.order_id
    join minishop_payment p on p.order_id = o.id
order by o.last_name
;
