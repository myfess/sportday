
WITH
    chs AS (
        SELECT
            p.challenge_id,
            array_agg(
                json_build_object('id', m2.id, 'name', u2.vk_name)
            ) friends
        FROM "members" m1
        INNER JOIN "user" u1 ON (u1.member_id = m1.id)
        INNER JOIN "user" u2 ON (u2.vk_id = ANY(u1.vk_friends))
        INNER JOIN "members" m2 ON (m2.id = u2.member_id)
        LEFT JOIN participations p ON (p.user_id = m2.id)
        WHERE
            m1.id = @member_id@
            AND p.part_type = 'registered'
        GROUP BY p.challenge_id
    )

SELECT
    ch.*,
    p.part_type,
    chs.friends
FROM chs
LEFT JOIN challenges ch ON (ch.id = chs.challenge_id)
LEFT JOIN participations p ON (
    p.challenge_id = ch.id
    AND p.user_id = @member_id@
)
WHERE
    (
        (ch."data"->>'sport') = ANY(@filters@::text[])
        OR
        coalesce(array_length(@filters@::text[], 1), 0) = 0
    )

ORDER BY (ch."data"->>'date')::date
