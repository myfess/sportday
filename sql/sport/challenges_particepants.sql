
SELECT
    ch.id,
    p.user_id,
    u.vk_name
FROM challenges ch
INNER JOIN participations p ON (p.challenge_id = ch.id)
INNER JOIN "user" u ON (u.member_id = p.user_id)
WHERE
    ch.id = ANY(@challenges@::int[])
    AND p.part_type = 'registered'
    AND u.vk_name IS NOT NULL
