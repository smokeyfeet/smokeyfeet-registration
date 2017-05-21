copy (
select
    r.first_name,
    r.last_name,
    r.email,
    r.residing_country,
    r.dance_role,
    pt.type as pass_type,
    pt.name as pass_name,
    r.workshop_partner_name,
    r.workshop_partner_email,
    lt.name as lunch_type,
    crew_remarks
from registration_registration r
    left join registration_passtype pt on r.pass_type_id = pt.id
    left join registration_lunchtype lt on r.lunch_id = lt.id
where exists (
    select 1
    from registration_payment p
    where p.registration_id = r.id
        group by r.id
    having sum(p.amount) >= r.total_price
)
order by r.last_name, r.first_name
) to stdout with (format csv, header true)
;
