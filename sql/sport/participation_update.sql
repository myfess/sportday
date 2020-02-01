INSERT
INTO participations (challenge_id, "user_id", part_type)
VALUES (@challenge_id@, @member_id@, @part_type@)
ON CONFLICT(challenge_id, "user_id") DO
    UPDATE
    SET
        part_type = @part_type@
RETURNING *

