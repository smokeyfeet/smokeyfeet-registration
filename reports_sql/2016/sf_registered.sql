--
select r.first_name, r.last_name, r.email, r.residing_country,
	r.dance_role, pt.type as pass_type, pt.name as pass_name,
	r.workshop_partner_name, r.workshop_partner_email,
	case when r.include_lunch=true then 'yes' else 'no' end as include_lunch,
	crew_remarks,
	(select string_agg(ct.name, ',') as competitions
		from registration_registration_competitions c
			join registration_competitiontype ct on c.competitiontype_id = ct.id
		where c.registration_id = r.id
	), r.strictly_partner,
	(select string_agg(vt.name, ',') as volunteering_for
		from registration_registration_volunteering_for v
			join registration_volunteertype vt on v.volunteertype_id = vt.id
		where v.registration_id = r.id
	)
	from registration_registration r
		left join registration_passtype pt on r.pass_type_id = pt.id
	where exists (
			select 1
			from registration_molliepayment p
			where r.id = p.registration_id and p.mollie_status = 'paid')
union
select o.first_name, o.last_name, o.email, '' as residing_country,
	case when i.product_name like '%follower%' then 'follower' else 'leader' end,
	'party' as pass_type, 'Party' as pass_name,
	'' as workshop_partner_name, '' as workshop_partner_email, 'no' as include_lunch,
	'(Purchased from SF shop)' as crew_remarks, '' as competitions, '' as strictly_partner,
	'' as volunteering_for
	from minishop_order o
		join minishop_orderitem i on o.id = i.order_id
	where o.mollie_payment_status = 'paid'
	order by last_name
	;
