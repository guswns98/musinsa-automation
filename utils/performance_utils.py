import os
import json
from datetime import datetime

APP_PACKAGE = "com.musinsa.store"


def get_performance_snapshot(driver):
    """앱의 현재 메모리/CPU 스냅샷을 반환합니다."""
    snapshot = {"time": datetime.now().isoformat()}

    try:
        mem_data = driver.get_performance_data(APP_PACKAGE, "memoryinfo", 5)
        if mem_data and len(mem_data) >= 2:
            mem_dict = dict(zip(mem_data[0], mem_data[1]))
            total_kb = int(mem_dict.get("totalPrivateDirty") or 0)
            snapshot["memory_mb"] = round(total_kb / 1024, 1)
            snapshot["memory_detail_kb"] = {
                "total": total_kb,
                "native": int(mem_dict.get("nativePrivateDirty") or 0),
                "dalvik": int(mem_dict.get("dalvikPrivateDirty") or 0),
            }
    except Exception as e:
        print(f"메모리 스냅샷 실패: {e}")

    return snapshot


def save_performance_log(test_name, before, after, report_dir=None):
    """성능 스냅샷 비교 결과를 리포트 디렉터리에 JSON으로 저장합니다."""
    diff_mb = None
    if "memory_mb" in before and "memory_mb" in after:
        diff_mb = round(after["memory_mb"] - before["memory_mb"], 1)

    result = {
        "test": test_name,
        "before": before,
        "after": after,
        "diff_memory_mb": diff_mb,
    }

    save_dir = report_dir or "reports"
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, f"perf_log_{test_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    mem_before = before.get("memory_mb", "?")
    mem_after = after.get("memory_mb", "?")
    diff_str = f"+{diff_mb}" if diff_mb and diff_mb > 0 else str(diff_mb)
    print(f"성능 로그 저장: {filepath} | 메모리 {mem_before}MB -> {mem_after}MB ({diff_str}MB)")

    return result
