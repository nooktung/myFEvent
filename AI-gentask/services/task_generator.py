"""
Task Generator V3 - Dynamic Task Count Based on Actual Team Size
Calculates: Available Workers = Total Headcount - 1 HOOC - Number of HODs
Each task assigned to specific person (except HOOC and HODs who manage epics)
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from services.venue_classifier import VenueTier, get_tier_multiplier, scale_complexity


# Action templates - ALL with action verbs
ACTION_TEMPLATES = {
    "Điều phối vận hành & hậu cần": [
        {
            "name": "Khảo sát địa điểm & đo đạc kích thước",
            "description": "Đo đạc kích thước, đánh giá hạ tầng điện nước, xác định điểm đặt thiết bị",
            "priority": "high",
            "duration_days": 2,
            "depends_on": []
        },
        {
            "name": "Thiết kế layout sân khấu",
            "description": "Vẽ bản thiết kế 2D/3D, phân vùng, xác định luồng di chuyển",
            "priority": "high",
            "duration_days": 3,
            "depends_on": ["Khảo sát địa điểm & đo đạc kích thước"]
        },
        {
            "name": "Lập phương án an toàn",
            "description": "Thiết kế phân luồng, lối thoát hiểm, checklist an toàn",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Thiết kế layout sân khấu"]
        },
        {
            "name": "Liên hệ nhà cung cấp thiết bị",
            "description": "Tìm vendor, yêu cầu báo giá, so sánh chất lượng",
            "priority": "medium",
            "duration_days": 2,
            "depends_on": ["Lập phương án an toàn"]
        },
        {
            "name": "Đặt cọc thiết bị & xác nhận giao hàng",
            "description": "Ký hợp đồng thuê, đặt cọc, xác nhận thời gian giao",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Liên hệ nhà cung cấp thiết bị"]
        },
        {
            "name": "Vận chuyển thiết bị tới địa điểm",
            "description": "Điều phối xe tải, bốc xếp, kiểm tra hàng hóa",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Đặt cọc thiết bị & xác nhận giao hàng"]
        },
        {
            "name": "Lắp đặt sân khấu & cấu trúc",
            "description": "Dựng khung, gắn backdrop, setup màn hình LED",
            "priority": "critical",
            "duration_days": 2,
            "depends_on": ["Vận chuyển thiết bị tới địa điểm"]
        },
        {
            "name": "Kéo dây điện & hệ thống mạng",
            "description": "Chạy dây nguồn, dây tín hiệu, test nguồn điện",
            "priority": "critical",
            "duration_days": 1,
            "depends_on": ["Lắp đặt sân khấu & cấu trúc"]
        },
        {
            "name": "Test hệ thống âm thanh",
            "description": "Kiểm tra loa, mic, mixer, xử lý feedback",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Kéo dây điện & hệ thống mạng"]
        },
        {
            "name": "Test hệ thống ánh sáng",
            "description": "Kiểm tra đèn, điều chỉnh góc chiếu, lập cue ánh sáng",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Kéo dây điện & hệ thống mạng"]
        },
        {
            "name": "Tổng duyệt kỹ thuật toàn bộ",
            "description": "Chạy thử toàn bộ hệ thống, xử lý lỗi, backup plan",
            "priority": "critical",
            "duration_days": 1,
            "depends_on": ["Test hệ thống âm thanh", "Test hệ thống ánh sáng"]
        },
    ],
    "Triển khai truyền thông & marketing": [
        {
            "name": "Nghiên cứu đối tượng mục tiêu",
            "description": "Phân tích demographics, insight, behavior khách hàng",
            "priority": "high",
            "duration_days": 2,
            "depends_on": []
        },
        {
            "name": "Lập kế hoạch truyền thông tổng thể",
            "description": "Xác định mục tiêu, KPI, kênh truyền thông, timeline, budget",
            "priority": "high",
            "duration_days": 3,
            "depends_on": ["Nghiên cứu đối tượng mục tiêu"]
        },
        {
            "name": "Phát triển concept sáng tạo",
            "description": "Brainstorm ý tưởng, chọn direction, viết creative brief",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Lập kế hoạch truyền thông tổng thể"]
        },
        {
            "name": "Thiết kế Key Visual chính",
            "description": "Concept và design bộ nhận diện thương hiệu cho event",
            "priority": "high",
            "duration_days": 4,
            "depends_on": ["Phát triển concept sáng tạo"]
        },
        {
            "name": "Sản xuất ấn phẩm poster/banner",
            "description": "Design poster, standee, backdrop theo KV",
            "priority": "medium",
            "duration_days": 2,
            "depends_on": ["Thiết kế Key Visual chính"]
        },
        {
            "name": "Tạo nội dung social media",
            "description": "Viết content, design post, lên lịch đăng",
            "priority": "medium",
            "duration_days": 3,
            "depends_on": ["Thiết kế Key Visual chính"]
        },
        {
            "name": "Quay dựng video teaser",
            "description": "Kịch bản, quay phim, edit video promo",
            "priority": "medium",
            "duration_days": 4,
            "depends_on": ["Thiết kế Key Visual chính"]
        },
        {
            "name": "Triển khai chiến dịch Facebook Ads",
            "description": "Setup campaign, targeting, chạy ads, optimize",
            "priority": "high",
            "duration_days": 7,
            "depends_on": ["Tạo nội dung social media"]
        },
        {
            "name": "Đăng bài trên các kênh social",
            "description": "Post theo lịch, engage với audience, theo dõi comments",
            "priority": "medium",
            "duration_days": 10,
            "depends_on": ["Tạo nội dung social media"]
        },
        {
            "name": "Theo dõi metrics & tối ưu",
            "description": "Track reach, engagement, conversion, A/B testing",
            "priority": "low",
            "duration_days": 7,
            "depends_on": ["Triển khai chiến dịch Facebook Ads"]
        },
    ],
    "Làm việc với nghệ sĩ & đối tác": [
        {
            "name": "Nghiên cứu & lập danh sách nghệ sĩ",
            "description": "Research nghệ sĩ phù hợp, check budget và lịch trình",
            "priority": "high",
            "duration_days": 3,
            "depends_on": []
        },
        {
            "name": "Liên hệ manager nghệ sĩ",
            "description": "Gửi email/call manager, giới thiệu event, hỏi availability",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Nghiên cứu & lập danh sách nghệ sĩ"]
        },
        {
            "name": "Thương lượng điều khoản hợp đồng",
            "description": "Đàm phán cát-xê, technical rider, quyền lợi",
            "priority": "high",
            "duration_days": 4,
            "depends_on": ["Liên hệ manager nghệ sĩ"]
        },
        {
            "name": "Ký kết hợp đồng chính thức",
            "description": "Review contract, ký kết, thanh toán deposit",
            "priority": "critical",
            "duration_days": 2,
            "depends_on": ["Thương lượng điều khoản hợp đồng"]
        },
        {
            "name": "Thu thập technical rider",
            "description": "Lấy yêu cầu kỹ thuật: âm thanh, ánh sáng, sân khấu",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Ký kết hợp đồng chính thức"]
        },
        {
            "name": "Thu thập hospitality rider",
            "description": "Lấy yêu cầu về đồ ăn, phòng nghỉ, vận chuyển",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Ký kết hợp đồng chính thức"]
        },
        {
            "name": "Đặt phòng khách sạn cho nghệ sĩ",
            "description": "Book khách sạn, confirm check-in/out, special requests",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Thu thập hospitality rider"]
        },
        {
            "name": "Sắp xếp vận chuyển nghệ sĩ",
            "description": "Book xe đưa đón sân bay, arrange transfers",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Thu thập hospitality rider"]
        },
        {
            "name": "Chuẩn bị backstage & amenities",
            "description": "Setup phòng chờ, đồ ăn, nước uống theo rider",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Thu thập hospitality rider"]
        },
        {
            "name": "Tổ chức soundcheck & rehearsal",
            "description": "Arrange lịch tổng duyệt, phối hợp technical team",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Thu thập technical rider"]
        },
    ],
    "Quản lý tài chính sự kiện": [
        {
            "name": "Lập dự trù ngân sách chi tiết",
            "description": "List tất cả hạng mục chi, estimate cost, dự phòng 15%",
            "priority": "critical",
            "duration_days": 3,
            "depends_on": []
        },
        {
            "name": "Phân bổ ngân sách theo từng ban",
            "description": "Chia budget cho mỗi department, set spending limit",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Lập dự trù ngân sách chi tiết"]
        },
        {
            "name": "Trình duyệt với ban lãnh đạo",
            "description": "Prepare presentation, pitch budget, giải trình chi tiết",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Phân bổ ngân sách theo từng ban"]
        },
        {
            "name": "Điều chỉnh theo feedback",
            "description": "Revise budget theo góp ý, tối ưu chi phí",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Trình duyệt với ban lãnh đạo"]
        },
        {
            "name": "Chuẩn bị hợp đồng mua sắm",
            "description": "Draft contracts cho vendors, negotiate terms",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Điều chỉnh theo feedback"]
        },
        {
            "name": "Ký kết hợp đồng với vendors",
            "description": "Review và ký contracts, lưu trữ documents",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Chuẩn bị hợp đồng mua sắm"]
        },
        {
            "name": "Thanh toán tạm ứng cho vendors",
            "description": "Process deposit payments, lưu receipts",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Ký kết hợp đồng với vendors"]
        },
        {
            "name": "Theo dõi chi tiêu thực tế",
            "description": "Track actual spending, so sánh vs budget, cảnh báo vượt chi",
            "priority": "high",
            "duration_days": 15,
            "depends_on": ["Thanh toán tạm ứng cho vendors"]
        },
        {
            "name": "Thu thập chứng từ thanh toán",
            "description": "Gather invoices, receipts, organize documents",
            "priority": "medium",
            "duration_days": 10,
            "depends_on": ["Theo dõi chi tiêu thực tế"]
        },
        {
            "name": "Quyết toán & báo cáo tài chính",
            "description": "Tổng hợp thu chi, phân tích variance, báo cáo ROI",
            "priority": "low",
            "duration_days": 3,
            "depends_on": ["Thu thập chứng từ thanh toán"]
        },
    ],
    "Quản lý chuyên môn & kỹ thuật": [
        {
            "name": "Phân tích yêu cầu kỹ thuật",
            "description": "Xác định specs cho âm thanh, ánh sáng, IT, streaming",
            "priority": "high",
            "duration_days": 2,
            "depends_on": []
        },
        {
            "name": "Lập danh sách thiết bị cần thiết",
            "description": "List equipment với specifications chi tiết",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Phân tích yêu cầu kỹ thuật"]
        },
        {
            "name": "Tìm nhà cung cấp thiết bị",
            "description": "Research vendors, so sánh giá và chất lượng",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Lập danh sách thiết bị cần thiết"]
        },
        {
            "name": "Test chất lượng thiết bị",
            "description": "Demo equipment trước khi thuê, check functionality",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Tìm nhà cung cấp thiết bị"]
        },
        {
            "name": "Ký hợp đồng thuê thiết bị",
            "description": "Negotiate contract, confirm delivery date",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Test chất lượng thiết bị"]
        },
        {
            "name": "Thiết lập hệ thống IT network",
            "description": "Setup router, switch, cabling, configure network",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Ký hợp đồng thuê thiết bị"]
        },
        {
            "name": "Cài đặt hệ thống livestream",
            "description": "Setup cameras, encoder, streaming software, test connection",
            "priority": "high",
            "duration_days": 2,
            "depends_on": ["Thiết lập hệ thống IT network"]
        },
        {
            "name": "Test kết nối internet bandwidth",
            "description": "Kiểm tra tốc độ mạng, stability, backup connection",
            "priority": "critical",
            "duration_days": 1,
            "depends_on": ["Cài đặt hệ thống livestream"]
        },
        {
            "name": "Chuẩn bị phương án backup",
            "description": "Setup backup equipment, alternative plans, redundancy",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Test kết nối internet bandwidth"]
        },
        {
            "name": "Bố trí technician onsite",
            "description": "Schedule tech team shifts, brief responsibilities, standby plan",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Chuẩn bị phương án backup"]
        },
    ],
}


def calculate_available_workers(headcount_total: int, num_departments: int) -> int:
    """
    Calculate actual workers available for task assignment
    
    Formula: Available = Total - 1 HOOC - Number of HODs
    
    Args:
        headcount_total: Total people in organizing team
        num_departments: Number of departments (each has 1 HOD)
        
    Returns:
        int: Number of workers available for tasks
    """
    if headcount_total <= 0:
        return 0
    
    hooc_count = 1  # 1 HOOC (Head of Organizing Committee)
    hod_count = num_departments  # Each department has 1 HOD (Head of Department)
    
    available = headcount_total - hooc_count - hod_count
    
    # Minimum 1 worker even if calculation goes negative
    return max(1, available)


def distribute_workers_to_departments(
    available_workers: int,
    departments: List[str],
    venue_tier: VenueTier
) -> Dict[str, int]:
    """
    Distribute workers to departments based on workload
    
    Args:
        available_workers: Total workers available
        departments: List of department names
        venue_tier: Venue tier for workload estimation
        
    Returns:
        Dict mapping department name to worker count
    """
    if not departments:
        return {}
    
    # Workload weights by department type
    workload_weights = {
        "hậu cần": 1.5,      # Highest workload
        "marketing": 1.2,
        "chuyên môn": 1.3,
        "tài chính": 0.8,
        "đối ngoại": 1.0,
    }
    
    # Normalize department names and get weights
    dept_weights = {}
    for dept in departments:
        normalized = _normalize_dept(dept)
        weight = workload_weights.get(normalized, 1.0)
        # Adjust by venue tier
        if venue_tier == "XL":
            weight *= 1.3
        elif venue_tier == "L":
            weight *= 1.1
        elif venue_tier == "S":
            weight *= 0.8
        
        dept_weights[dept] = weight
    
    # Calculate proportional distribution
    total_weight = sum(dept_weights.values())
    distribution = {}
    
    assigned = 0
    for dept, weight in dept_weights.items():
        count = int((weight / total_weight) * available_workers)
        count = max(1, count)  # At least 1 person per department
        distribution[dept] = count
        assigned += count
    
    # Adjust if total doesn't match (distribute remainder to heaviest dept)
    diff = available_workers - assigned
    if diff != 0:
        # Find department with highest workload
        heaviest_dept = max(dept_weights.keys(), key=lambda d: dept_weights[d])
        distribution[heaviest_dept] += diff
        distribution[heaviest_dept] = max(1, distribution[heaviest_dept])
    
    return distribution


def generate_tasks(
    epics: List[Dict[str, Any]],
    event_date: str,
    venue_tier: VenueTier,
    headcount_total: int
) -> List[Dict[str, Any]]:
    """
    Generate tasks dynamically based on actual team size
    
    Args:
        epics: List of epic dictionaries
        event_date: Event date in YYYY-MM-DD format
        venue_tier: Venue tier for scaling
        headcount_total: Total headcount (includes HOOC + HODs + workers)
        
    Returns:
        List of task dictionaries with proper person assignment
    """
    
    if not epics:
        return []
    
    # Calculate available workers
    num_departments = len(epics)
    available_workers = calculate_available_workers(headcount_total, num_departments)
    
    # Distribute workers to departments
    worker_distribution = distribute_workers_to_departments(
        available_workers,
        [e["department"] for e in epics],
        venue_tier
    )
    
    # Generate tasks
    tasks = []
    task_counter = 1
    
    # Parse event date
    try:
        event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    except:
        event_dt = datetime.now()
    
    # Track used task names globally to avoid duplicates
    used_names: set = set()
    
    for epic in epics:
        epic_id = epic["epic_id"]
        epic_name = epic["name"]
        department = epic["department"]
        
        # Get action templates for this epic
        templates = ACTION_TEMPLATES.get(epic_name, [])
        
        if not templates:
            templates = _get_generic_templates()
        
        # Get number of workers for this department
        num_workers = worker_distribution.get(department, 1)
        
        # Select appropriate number of tasks based on workers
        # Rule: Each worker handles 2-3 tasks on average
        target_task_count = min(len(templates), max(3, num_workers * 2))
        
        # Take first N templates
        selected_templates = templates[:target_task_count]
        
        # Track epic-level task name to ID mapping
        epic_task_map: Dict[str, str] = {}
        
        for action in selected_templates:
            task_name = action["name"]
            
            # Skip if duplicate globally
            if task_name in used_names:
                continue
            
            used_names.add(task_name)
            
            task_id = f"T-{task_counter:03d}"
            task_counter += 1
            
            # Calculate deadline (backward from event date)
            duration = action.get("duration_days", 1)
            adjusted_duration = max(1, int(duration * get_tier_multiplier(venue_tier)))
            
            days_before_event = _calculate_days_before_event(action["priority"], adjusted_duration)
            deadline_dt = event_dt - timedelta(days=days_before_event)
            start_dt = deadline_dt - timedelta(days=adjusted_duration - 1)
            
            start_date = start_dt.strftime("%Y-%m-%d")
            deadline = deadline_dt.strftime("%Y-%m-%d")
            
            # Resolve dependencies
            depends_on_names = action.get("depends_on", [])
            depends_on_ids = [epic_task_map.get(name, "") for name in depends_on_names]
            depends_on_ids = [tid for tid in depends_on_ids if tid]
            
            # Scale complexity
            base_complexity = _priority_to_complexity(action["priority"])
            complexity = scale_complexity(base_complexity, venue_tier)
            
            task = {
                "task_id": task_id,
                "epic_id": epic_id,
                "name": task_name,
                "category": epic_name,
                "description": action["description"],
                "priority": action["priority"],
                "start-date": start_date,
                "deadline": deadline,
                "assign": "",  # Will be assigned by frontend/HOD
                "depends_on": depends_on_ids,
                "complexity": complexity,
            }
            
            tasks.append(task)
            epic_task_map[task_name] = task_id
    
    return tasks


def _calculate_days_before_event(priority: str, duration: int) -> int:
    """Calculate how many days before event this task should be completed"""
    base_days = {
        "critical": 1,
        "high": 5,
        "medium": 10,
        "low": 15,
    }
    return base_days.get(priority, 7) + duration


def _priority_to_complexity(priority: str) -> str:
    """Map priority to complexity level"""
    mapping = {
        "critical": "critical",
        "high": "high",
        "medium": "medium",
        "low": "low",
    }
    return mapping.get(priority, "medium")


def _normalize_dept(dept: str) -> str:
    """Normalize department name"""
    dept_lower = dept.lower().strip()
    
    if any(k in dept_lower for k in ["hậu cần", "logistics"]):
        return "hậu cần"
    if any(k in dept_lower for k in ["marketing", "maketing", "media"]):
        return "marketing"
    if any(k in dept_lower for k in ["chuyên môn", "technical"]):
        return "chuyên môn"
    if any(k in dept_lower for k in ["tài chính", "finance"]):
        return "tài chính"
    if any(k in dept_lower for k in ["đối ngoại", "external"]):
        return "đối ngoại"
    
    return dept


def _get_generic_templates() -> List[Dict[str, Any]]:
    """Generic fallback templates"""
    return [
        {
            "name": "Lập kế hoạch chi tiết",
            "description": "Xác định mục tiêu, phạm vi, timeline",
            "priority": "high",
            "duration_days": 2,
            "depends_on": []
        },
        {
            "name": "Phân công nhiệm vụ",
            "description": "Assign tasks cho từng thành viên",
            "priority": "high",
            "duration_days": 1,
            "depends_on": ["Lập kế hoạch chi tiết"]
        },
        {
            "name": "Triển khai thực hiện",
            "description": "Execute theo plan đã định",
            "priority": "medium",
            "duration_days": 5,
            "depends_on": ["Phân công nhiệm vụ"]
        },
        {
            "name": "Kiểm tra chất lượng",
            "description": "Review output, identify issues",
            "priority": "medium",
            "duration_days": 1,
            "depends_on": ["Triển khai thực hiện"]
        },
        {
            "name": "Hoàn thiện & bàn giao",
            "description": "Finalize và hand over",
            "priority": "low",
            "duration_days": 1,
            "depends_on": ["Kiểm tra chất lượng"]
        },
    ]


# Example usage
if __name__ == "__main__":
    from services.venue_classifier import classify_venue
    
    # Test with realistic scenario
    print("="*70)
    print("TASK GENERATION WITH WORKER CALCULATION")
    print("="*70)
    
    # Scenario: 100 people, 4 departments
    headcount = 100
    departments = ["Hậu cần", "Marketing", "Chuyên môn", "Tài chính"]
    
    print(f"\n📊 Team Structure:")
    print(f"  Total headcount: {headcount}")
    print(f"  - 1 HOOC (Head of Organizing Committee)")
    print(f"  - {len(departments)} HODs (Heads of Department)")
    print(f"  - Available workers: {calculate_available_workers(headcount, len(departments))}")
    
    # Worker distribution
    venue_tier = classify_venue("đường 30m")
    worker_dist = distribute_workers_to_departments(
        calculate_available_workers(headcount, len(departments)),
        departments,
        venue_tier
    )
    
    print(f"\n👥 Worker Distribution by Department:")
    for dept, count in worker_dist.items():
        print(f"  {dept}: {count} workers")
    
    # Generate epics
    epics = [
        {
            "epic_id": f"EP-{i:03d}",
            "name": ACTION_TEMPLATES[list(ACTION_TEMPLATES.keys())[i % len(ACTION_TEMPLATES)]],
            "department": dept,
        }
        for i, dept in enumerate(departments)
    ]
    
    # Map to proper epic names
    epic_name_mapping = {
        "Hậu cần": "Điều phối vận hành & hậu cần",
        "Marketing": "Triển khai truyền thông & marketing",
        "Chuyên môn": "Quản lý chuyên môn & kỹ thuật",
        "Tài chính": "Quản lý tài chính sự kiện",
    }
    
    epics = [
        {
            "epic_id": f"EP-{i+1:03d}",
            "name": epic_name_mapping.get(dept, f"Điều phối {dept}"),
            "department": dept,
        }
        for i, dept in enumerate(departments)
    ]
    
    # Generate tasks
    tasks = generate_tasks(epics, "2024-12-25", venue_tier, headcount)
    
    print(f"\n📋 Generated Tasks:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Tasks per department:")
    
    for epic in epics:
        epic_tasks = [t for t in tasks if t["epic_id"] == epic["epic_id"]]
        workers = worker_dist.get(epic["department"], 0)
        ratio = len(epic_tasks) / workers if workers > 0 else 0
        print(f"    {epic['department']:15} : {len(epic_tasks):2} tasks ({workers:2} workers, {ratio:.1f} tasks/worker)")
        
        # Show sample tasks
        for task in epic_tasks[:3]:
            print(f"      - {task['name']}")
        if len(epic_tasks) > 3:
            print(f"      ... and {len(epic_tasks) - 3} more")
    
    # Verify all tasks start with action verbs
    print(f"\n✅ Task Name Verification (All should start with action verbs):")
    action_verbs = set()
    for task in tasks:
        first_word = task["name"].split()[0]
        action_verbs.add(first_word)
    
    print(f"  Unique action verbs: {', '.join(sorted(action_verbs))}")
    
    # Check for duplicates
    task_names = [t["name"] for t in tasks]
    duplicates = [name for name in task_names if task_names.count(name) > 1]
    
    if duplicates:
        print(f"\n❌ Found duplicates: {set(duplicates)}")
    else:
        print(f"\n✅ No duplicate tasks!")