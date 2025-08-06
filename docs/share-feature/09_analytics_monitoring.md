# 09 – Analytics & Monitoring

Logging
• `log_user_action` called with `action_type="share_create"` and `"share_view"`.
• Include `token` and `viewer_id` (if available) anonymised.

Metrics
• Prometheus counter `bot_share_created_total` and `bot_share_viewed_total`.
• Grafana dashboard widget.

Cleanup
• Daily job logs deleted rows count.

Alerting
• Warning if share views fail with >1 % error rate per hour. 