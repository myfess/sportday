chs AS (
    SELECT
        p.challenge_id
    FROM "members" m
    LEFT JOIN participations p ON (p.user_id = m.id)
    WHERE
        m.id = ANY(@friends@::int[])
        AND p.part_type = 'registered'
    GROUP BY p.challenge_id
),
