WITH
    t1 AS (
        SELECT friend_id fid
        FROM friends
        WHERE
            member_id = @member_id@
            AND "status" = 'friend'
    ),

    t2 AS (
        SELECT friend_id fid
        FROM friends
        WHERE
            member_id = @member_id@
            AND "status" = 'deleted'
    ),

    t3 AS (
        SELECT u2.member_id fid
        FROM "user" u1
        INNER JOIN "user" u2 ON (u2.vk_id = ANY(u1.vk_friends))
        WHERE
            u1.member_id = @member_id@
    ),

    f_union AS (
        SELECT *
        FROM t1

        UNION

        SELECT *
        FROM t3
    )

SELECT array_agg(f_union.fid)
FROM f_union
LEFT JOIN t2 ON (t2.fid = f_union.fid)
WHERE
    t2.fid IS NULL


