WITH
    {cte}

    __stub AS (
        SELECT TRUE
    )

SELECT
    ch.*,
    p.part_type
FROM "challenges" ch

{join}

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

    AND (ch."data"->>'date')::date >= NOW()

ORDER BY (ch."data"->>'date')::date
