SELECT
    ch.*,
    p.part_type
FROM "challenges" ch
LEFT JOIN participations p ON (
    p.challenge_id = ch.id
    AND p.user_id = @member_id@
)
WHERE
    TRUE
    {where}
    AND (
        (ch."data"->>'sport') = ANY(@filters@::text[])
        OR
        coalesce(array_length(@filters@::text[], 1), 0) = 0
    )
ORDER BY (ch."data"->>'date')::date
