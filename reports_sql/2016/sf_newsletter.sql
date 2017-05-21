--
select first_name, last_name, email
	from registration_registration reg
	where exists (
			select 1
			from registration_molliepayment p
			where reg.id = p.registration_id and p.mollie_status = 'paid')
union
select first_name, last_name, email
	from minishop_order where mollie_payment_status = 'paid'
	order by last_name
	;
