import csv
import sys
from collections import defaultdict

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else 'ss_metrics.csv'

sums = defaultdict(float)
rows = []
with open(CSV_PATH, newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)
        # sum useful columns
        sums['geofence_monitoring'] += float(r.get('geofence_count_monitoring', 0) or 0)
        sums['geofence_wait'] += float(r.get('geofence_count_waitforhalt', 0) or 0)
        sums['geofence_safehalt'] += float(r.get('geofence_count_safehaltactive', 0) or 0)

        sums['monitoring_time_ms'] += float(r.get('monitoring_time_ms', 0) or 0)
        sums['wait_time_ms'] += float(r.get('waitforhalt_time_ms', 0) or 0)
        sums['safe_time_ms'] += float(r.get('safehaltactive_time_ms', 0) or 0)

        sums['halt_in_wait'] += float(r.get('haltObserved_in_wait', 0) or 0)
        sums['tick_in_wait'] += float(r.get('tick_in_wait', 0) or 0)
        sums['wait_entries'] += float(r.get('waitforhalt_entry_count', 0) or 0)

        sums['move_in_safe'] += float(r.get('move_in_safehalt', 0) or 0)
        sums['safe_entries'] += float(r.get('safehaltactive_entry_count', 0) or 0)
        sums['safe_halt_request_count'] += float(r.get('safe_halt_request_count', 0) or 0)
        ts = r.get('safe_halt_request_timestamp', '')
        if ts:
            try:
                ts_val = int(ts)
                sums['safe_halt_request_timestamp_min'] = min(sums.get('safe_halt_request_timestamp_min', ts_val), ts_val)
                sums['safe_halt_request_timestamp_max'] = max(sums.get('safe_halt_request_timestamp_max', ts_val), ts_val)
            except ValueError:
                pass


    def parse_first_timestamp(field_val):
        """Return the first integer timestamp found in the field, or None."""
        if not field_val:
            return None
        s = str(field_val).strip()
        import re
        # find long integers (timestamps)
        m = re.findall(r"(\d{9,})", s)
        if m:
            try:
                return int(m[0])
            except ValueError:
                return None
        try:
            return int(s)
        except Exception:
            return None


    def compute_summary_metrics(rows):
        total = len(rows)
        m8_reached_safe = 0
        m10_safe_active = 0
        m11_geofence = 0
        min_distance = None

        safe_halt_response_normal = []
        safe_halt_response_enforced = []
        geofence_enforcement_latency = []

        for r in rows:
            def truthy(keys):
                for k in keys:
                    v = r.get(k, '')
                    if isinstance(v, str) and v.lower() in ('1', 'true'):
                        return True
                    try:
                        if int(v) == 1:
                            return True
                    except Exception:
                        pass
                return False

            enforced = truthy(['enforced_stop', 'enforced_stop'])
            safe_active = truthy(['safe_halt_active', 'safe_halt_active'])
            geofence = truthy(['geofence_violation', 'geofence_violation'])

            if enforced or safe_active:
                m8_reached_safe += 1
            if safe_active:
                m10_safe_active += 1
            if geofence:
                m11_geofence += 1

            # min distance
            try:
                md = float(r.get('min_distance', r.get('min_distance_observed', '') or 0) or 0)
                if min_distance is None or md < min_distance:
                    min_distance = md
            except Exception:
                pass

            sr_req = parse_first_timestamp(r.get('safe_halt_request_timestamp') or r.get('safe_halt_request_timestamps') or r.get('safe_halt_request', ''))
            sr_ts = parse_first_timestamp(r.get('safe_halt_timestamp') or r.get('safe_halt_time', ''))
            en_ts = parse_first_timestamp(r.get('enforced_stop_timestamp') or r.get('enforced_stop_time', ''))
            gv_ts = parse_first_timestamp(r.get('geofence_violation_timestamp') or r.get('geofence_violation_time', ''))

            if sr_req is not None and sr_ts is not None:
                safe_halt_response_normal.append(sr_ts - sr_req)
            if sr_req is not None and en_ts is not None:
                safe_halt_response_enforced.append(en_ts - sr_req)
            if gv_ts is not None and en_ts is not None:
                geofence_enforcement_latency.append(en_ts - gv_ts)

        def avg(lst):
            return (sum(lst) / len(lst)) if lst else None

        return {
            'Total runs': total,
            'M8 – Probability of reaching a safe terminal condition': m8_reached_safe / total if total else None,
            'M10 – Frequency of Safety System intervention': m10_safe_active / total if total else None,
            'M11 – Frequency of minimum-distance violations': m11_geofence / total if total else None,
            'M12 – Minimum distance to restricted boundary': min_distance,
            'M13 – Safe halt response time milliseconds (halt observed normally)': avg(safe_halt_response_normal),
            'M13 – Safe halt response time milliseconds (enforced by SS)': avg(safe_halt_response_enforced),
            'M14 – Geofence enforcement latency milliseconds': avg(geofence_enforcement_latency),
        }


def print_table(title, columns, rows):
    widths = [len(col) for col in columns]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))

    sep = '+{}+'.format('+'.join('-' * (w + 2) for w in widths))
    header = '| {} |'.format(' | '.join(col.ljust(widths[idx]) for idx, col in enumerate(columns)))
    print(f'\n{title}')
    print(sep)
    print(header)
    print(sep.replace('-', '='))
    for row in rows:
        print('| {} |'.format(' | '.join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(row))))
    print(sep)


def print_table4():
    print_table(
        'Table 4 — Geofence Monitoring (SS_SafeHaltController)',
        ['State', 'count geofenceViolation', 'total time ms'],
        [
            ['Monitoring', int(sums['geofence_monitoring']), int(sums['monitoring_time_ms'])],
            ['WaitForHalt', int(sums['geofence_wait']), int(sums['wait_time_ms'])],
            ['SafeHaltActive', int(sums['geofence_safehalt']), int(sums['safe_time_ms'])],
        ]
    )


def print_summary(metrics):
    print_table(
        'Summary Metrics (M8-M14)',
        ['Metric', 'Value'],
        [
            ['Total runs', metrics['Total runs']],
            ['M8 – Probability of reaching a safe terminal condition', '{:.4f}'.format(metrics['M8 – Probability of reaching a safe terminal condition']) if metrics['M8 – Probability of reaching a safe terminal condition'] is not None else ''],
            ['M10 – Frequency of Safety System intervention', '{:.4f}'.format(metrics['M10 – Frequency of Safety System intervention']) if metrics['M10 – Frequency of Safety System intervention'] is not None else ''],
            ['M11 – Frequency of minimum-distance violations', '{:.4f}'.format(metrics['M11 – Frequency of minimum-distance violations']) if metrics['M11 – Frequency of minimum-distance violations'] is not None else ''],
            ['M12 – Minimum distance to restricted boundary', metrics['M12 – Minimum distance to restricted boundary'] if metrics['M12 – Minimum distance to restricted boundary'] is not None else ''],
            ['M13 – Safe halt response time milliseconds (halt observed normally)', int(metrics['M13 – Safe halt response time milliseconds (halt observed normally)']) if metrics['M13 – Safe halt response time milliseconds (halt observed normally)'] is not None else ''],
            ['M13 – Safe halt response time milliseconds (enforced by SS)', int(metrics['M13 – Safe halt response time milliseconds (enforced by SS)']) if metrics['M13 – Safe halt response time milliseconds (enforced by SS)'] is not None else ''],
            ['M14 – Geofence enforcement latency milliseconds', int(metrics['M14 – Geofence enforcement latency milliseconds']) if metrics['M14 – Geofence enforcement latency milliseconds'] is not None else ''],
        ]
    )


def print_table5():
    print_table(
        'Table 5 — WaitForHalt Outcomes (SS_SafeHaltController)',
        ['State', 'count haltObserved', 'count tick', 'total entries'],
        [[
            'WaitForHalt',
            int(sums['halt_in_wait']),
            int(sums['tick_in_wait']),
            int(sums['wait_entries'])
        ]]
    )


def print_table6():
    print_table(
        'Table 6 — SafeHaltActive "move" outcomes (SS_SafeHaltController)',
        ['State', 'count move', 'total entries'],
        [[
            'SafeHaltActive',
            int(sums['move_in_safe']),
            int(sums['safe_entries'])
        ]]
    )


if __name__ == '__main__':
    if not rows:
        print('No rows found in', CSV_PATH)
        sys.exit(1)
    metrics = compute_summary_metrics(rows)
    print_summary(metrics)
    print_table4()
    print_table5()
    print_table6()

