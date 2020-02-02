SELECT "name"
FROM "user" u
INNER JOIN members m ON (m.id = u.member_id)
WHERE
    u.id = @ext_user_id@
