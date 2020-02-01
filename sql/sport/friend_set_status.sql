INSERT
INTO friends (
    member_id,
    friend_id,
    "status"
)
VALUES (
    @member_id@,
    @friend_id@,
    @status@
)
ON CONFLICT(member_id, friend_id) DO
    UPDATE
    SET
        "status" = @status@
RETURNING *
