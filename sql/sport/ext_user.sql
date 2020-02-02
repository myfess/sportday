INSERT
INTO "user" (
    vk_id,
    vk_token,
    vk_token_expires,
    vk_name,
    vk_photo,
    vk_friends
)
VALUES (
    @vk_id@,
    @vk_token@,
    @vk_token_expires@,
    @vk_name@,
    @vk_photo@,
    @vk_friends@
)
ON CONFLICT(vk_id) DO
    UPDATE
    SET
        vk_token = @vk_token@,
        vk_token_expires = @vk_token_expires@,
        vk_name = @vk_name@,
        vk_photo = @vk_photo@,
        vk_friends = @vk_friends@
RETURNING *
