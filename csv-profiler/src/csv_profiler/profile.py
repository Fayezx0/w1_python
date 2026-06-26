# from __future__ import annotations
# def basic_profile(rows: list[dict[str, str]]) -> dict:
#     """Compute row count, column names, and missing values per column."""
    
#     # 1. Handle empty dataset case
#     if not rows:
#         return {"rows": 0, "columns": [], "missing": {}}
#     # 2. Get column names from the first row
#     columns = list(rows[0].keys())
#     # 3. Initialize missing counters for each column
#     missing = {c: 0 for c in columns}

#     # 4. Loop through rows and count missing values
#     for row in rows:
#         for c in columns:
#             # Get value, treat None or whitespace as missing
#             value = (row.get(c) or "").strip()
#             if value == "":
#                 missing[c] += 1     
#     # 5. Return the final report dictionary
#     return {"rows": len(rows),"columns": columns,"missing": missing }

# def basic_profile(rows: list[dict[str, str]]) -> dict:
#     """
#     Compute a profile of the dataset including shape and column types.
#     """
#     # Get all column names
#     cols = get_columns(rows)
    
#     # Initialize the report structure
#     report = {
#         "summary": {
#             "rows": len(rows),
#             "columns": len(cols),
#             "column_names": cols,
#         },
#         "columns": {},
#     }


#     # Loop through each column to analyze it
#     for col in cols:
#         # Get all data for this specific column
#         values = column_values(rows, col)     
#         # Ask our logic: is this a number or text?
#         typ = infer_type(values)       
#         # Save the result in the report
#         report["columns"][col] = {
#             "type": typ,
#             # We will add more stats (min/max) here in the next step
#         }    
#     return report

def basic_profile(rows: list[dict[str, str]]) -> dict:
    """
    Compute the full profile report with types and statistics.
    """
    cols = get_columns(rows) # ماهي اسماء الأعمدة
    report = {
        "summary": {
            "rows": len(rows),
            "columns": len(cols),
            "column_names": cols,
        },
        "columns": {},
    }
    for col in cols:
        values = column_values(rows, col) # استخراج كل القيم للعمود المحدد
        
        # 1. Infer the type (number vs text)
        typ = infer_type(values) # 3 هل العمود نص ام رقم
        # 2. Compute stats based on the inferred type
        if typ == "number":
            stats = numeric_stats(values)
        else:
            stats = text_stats(values) 
        # 3. Save everything to the report
        report["columns"][col] = {
            "type": typ,**stats  # **stats merges the stats dict into this dict
        }
    return report



def try_float(value: str) -> float | None:
    """
    محاولة تحويل النص إلى رقم عشري.
    إذا نجح، يرجع الرقم.
    إذا فشل (كان نصاً)، يرجع None.
    """
    try:
        return float(value)
    except ValueError:
        return None



# 1. قائمة الكلمات التي نعتبرها "فارغة"
MISSING = {"", "na", "n/a", "null", "none", "nan"}

def is_missing(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().casefold() in MISSING

# دالة لتحديد نوع العمود
def infer_type(values: list[str]) -> str:
    """
    تحدد نوع البيانات في قائمة من القيم:
    - ترجع "number" إذا كانت كل القيم (غير الفارغة) أرقاماً.
    - ترجع "text" إذا وجدت أي قيمة نصية.
    """
    # نجمع فقط القيم غير الفارغة
    usable = [v for v in values if not is_missing(v)]

    # إذا كان العمود كله فارغاً، نعتبره نصاً افتراضياً
    if not usable:
        return "text"

    # نفحص كل قيمة
    for v in usable:
        # إذا فشل تحويل أي قيمة لرقم، فالعمود كله يعتبر نصاً
        if try_float(v) is None:
            return "text"

    # إذا نجت كل القيم من الاختبار، فالعمود رقمي
    return "number"


def get_columns(rows: list[dict[str, str]]) -> list[str]:
    """Return a list of column names from the first row."""
    if not rows:
        return []
    return list(rows[0].keys())

def column_values(rows: list[dict[str, str]], col: str) -> list[str]:
    """Extract all values for a specific column as a list of strings."""
    return [row.get(col, "") for row in rows]



def numeric_stats(values: list[str]) -> dict:
    """
    Compute statistics for a numeric column.
    
    Calculates:
    - min: Minimum value
    - max: Maximum value
    - mean: Average value
    - count: Number of valid numeric values
    - unique: Number of unique values
    """
    # Filter out missing values first
    usable = [v for v in values if not is_missing(v)]
    
    # Calculate how many values are missing based on original list length
    missing_count = len(values) - len(usable)
    
    # Convert strings to floats
    nums: list[float] = []
    for v in usable:
        val = try_float(v)
        # If we encounter a value that can't be converted, we skip it or handle error
        if val is not None:
            nums.append(val)
            
    # If no valid numbers are found, return empty stats
    if not nums:
        return {
            "min": 0,
            "max": 0,
            "mean": 0,
            "count": 0,
            "missing": missing_count,
            "unique": 0
        }

    # Calculate statistics
    avg = sum(nums) / len(nums)
    
    return {
        "min": min(nums),
        "max": max(nums),
        "mean": avg,
        "count": len(nums),
        "missing": missing_count,
        "unique": len(set(nums))
    }

def text_stats(values: list[str], top_k: int = 5) -> dict:
    """
    Compute statistics for a text column.
    
    Calculates:
    - count: Number of non-missing values
    - missing: Number of missing values
    - unique: Number of unique values
    - top: List of the top-k most frequent values
    """
    # Filter out missing values
    usable = [v for v in values if not is_missing(v)]
    
    # Calculate missing count
    missing_count = len(values) - len(usable)
    
    # Count frequency of each value
    counts: dict[str, int] = {}
    for v in usable:
        counts[v] = counts.get(v, 0) + 1
        
    # Sort by frequency (highest count first) to find top values
    top_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    
    # Extract just the top K items
    top = [{"value": v, "count": c} for v, c in top_items[:top_k]]
    
    return {
        "count": len(usable),
        "missing": missing_count,
        "unique": len(counts),
        "top": top
    }

def text_stats(values: list[str], top_k: int = 5) -> dict:
    """
    Compute statistics for a text column.
    
    Calculates:
    - count: Number of non-missing values
    - missing: Number of missing values
    - unique: Number of unique values
    - top: List of the top-k most frequent values
    """
    # Filter out missing values
    usable = [v for v in values if not is_missing(v)]
    
    # Calculate missing count
    missing_count = len(values) - len(usable)
    
    # Count frequency of each value
    counts: dict[str, int] = {}
    for v in usable:
        counts[v] = counts.get(v, 0) + 1
        
    # Sort by frequency (highest count first) to find top values
    top_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    
    # Extract just the top K items
    top = [{"value": v, "count": c} for v, c in top_items[:top_k]]
    
    return {
        "count": len(usable),
        "missing": missing_count,
        "unique": len(counts),
        "top": top
    }