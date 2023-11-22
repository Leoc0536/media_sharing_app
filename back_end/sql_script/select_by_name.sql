WITH parse AS(
    SELECT
        group_concat(t2.keyword) as keyword,
        t2.owner_id
    FROM keyword_table t2
    GROUP BY t2.owner_id
)
SELECT
    id,
    name,
    description,
    date_of_media,
    keyword,
    object_url
FROM media_metadata JOIN parse ON parse.owner_id = media_metadata.id
WHERE name='{media_name}';