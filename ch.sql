CREATE TABLE IF NOT EXISTS reklamito.shows
(
    event_id         UUID,
    timestamp        DateTime64(3, 'UTC'),
    timestamp_date   Date MATERIALIZED toDate(timestamp),  -- Для TTL
    banner_id        UInt32,
    campaign_id      UInt32,
    user_id          Nullable(UInt32),
    ip_address       Nullable(String),
    user_agent       Nullable(String),
    country          Nullable(String),
    city             Nullable(String),
    latitude         Nullable(Float64),
    longitude        Nullable(Float64),
    device_type      Nullable(Enum8('mobile' = 1, 'desktop' = 2, 'tablet' = 3)),
    os_family        Nullable(String),
    os_version       Nullable(String),
    browser_family   Nullable(String),
    browser_version  Nullable(String),
    screen_width     Nullable(UInt16),
    screen_height    Nullable(UInt16),
    language         Nullable(String),
    referer_domain   Nullable(String),
    referer_path     Nullable(String),
    is_robot         Nullable(UInt8),
    ad_position      Nullable(String),
    ad_size          Nullable(String),
    cost_model       Nullable(Enum8('CPM' = 1, 'CPC' = 2)),
    session_id       Nullable(String),
    network_type     Nullable(Enum8('wifi' = 1, 'cellular' = 2, 'wired' = 3)),
    connection_speed Nullable(UInt32)
)
ENGINE = MergeTree()
ORDER BY (timestamp, banner_id, campaign_id)
TTL timestamp_date + INTERVAL 18 MONTH;

CREATE TABLE IF NOT EXISTS reklamito.clicks
(
    show_event_id    UUID,
    timestamp        DateTime64(3, 'UTC'),
    timestamp_date   Date MATERIALIZED toDate(timestamp),  -- Для TTL
    banner_id        UInt32,
    campaign_id      UInt32,
    click_x          Nullable(UInt16),
    click_y          Nullable(UInt16),
    element_id       Nullable(String),
    element_class    Nullable(String),
    referer_url      Nullable(String),
    http_method      Nullable(String),
    form_data        Nullable(String),
    time_to_click    Nullable(Float64),
    is_conversion    Nullable(UInt8),
    conversion_value Nullable(Decimal(18, 6)),
    click_cost       Nullable(Decimal(18, 6)),
    button_type      Nullable(Enum8('text' = 1, 'image' = 2, 'video' = 3)),
    click_depth      Nullable(UInt8),
    scroll_position  Nullable(UInt16),
    hover_time       Nullable(UInt32)
)
ENGINE = MergeTree()
ORDER BY (timestamp, banner_id, campaign_id)
TTL timestamp_date + INTERVAL 18 MONTH;
