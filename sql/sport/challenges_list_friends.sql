SELECT
    p.challenge_id,
    array_agg(
        json_build_object(
            'id', u.member_id,
            'name', u.vk_name
        )
    ) friends
FROM "user" u
LEFT JOIN participations p ON (p.user_id = u.member_id)
WHERE
    u.member_id = ANY(@friends@::int[])
    AND p.part_type = 'registered'
GROUP BY p.challenge_id
