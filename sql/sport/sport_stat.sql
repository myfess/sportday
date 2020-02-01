SELECT
    data->>'sport' sport,
    count(*) cnt
FROM participations p
INNER JOIN challenges ch ON (ch.id = p.challenge_id)
WHERE
    p.user_id = @member_id@
    AND part_type = 'registered'
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10
