SELECT
    ch.*,
    p.part_type
FROM challenges ch
LEFT JOIN participations p ON (
    p.challenge_id = ch.id
    AND p.user_id = @member_id@
)
WHERE
    ch.id = @challenge_id@
