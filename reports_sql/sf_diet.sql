--
select first_name, last_name, email, diet_requirements
	from registration_registration reg
	where reg.diet_requirements <> ''
		and exists (
			select 1
			from registration_molliepayment p
			where reg.id = p.registration_id and p.mollie_status = 'paid')
	order by last_name;
