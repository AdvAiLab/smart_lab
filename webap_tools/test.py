import sys
from webap_tools.auto_punch import AutoPunching

auto_ap = AutoPunching(sys.argv[1])
auto_ap.calendar_plan_month_job()
