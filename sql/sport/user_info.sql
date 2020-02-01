SELECT *
FROM members m
LEFT JOIN "user" u ON (u.member_id = m.id)
WHERE
    m.id = @member_id@
LIMIT 1
