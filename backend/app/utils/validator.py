import uuid
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple, Any
from sqlalchemy.orm import Session
from io import BytesIO

from ..models import FollowupRecord, FollowupTemplate, FollowupPlan, ErrorRecord, Alert, AuditLog
from ..schemas import RecordResponse, ErrorRecordResponse


class ValidationError(Exception):
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)


def generate_batch_id() -> str:
    return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"


def validate_row(row: Dict[str, Any], row_num: int, template: FollowupTemplate, existing_records: set, db: Session) -> Tuple[bool, Dict[str, Any], List[str]]:
    errors = []
    cleaned_data = {}

    patient_id = str(row.get('patient_id', '')).strip()
    if not patient_id or patient_id == 'nan':
        errors.append("患者编号缺失")
    cleaned_data['patient_id'] = patient_id

    patient_name = str(row.get('patient_name', '')).strip()
    cleaned_data['patient_name'] = patient_name if patient_name != 'nan' else None

    try:
        date_val = row.get('followup_date')
        if pd.isna(date_val):
            errors.append("随访日期缺失")
        else:
            if isinstance(date_val, str):
                followup_date = datetime.strptime(date_val, '%Y-%m-%d')
            else:
                followup_date = pd.to_datetime(date_val).to_pydatetime()
            if followup_date > datetime.now():
                errors.append("随访日期不能晚于当前日期")
            cleaned_data['followup_date'] = followup_date
    except Exception as e:
        errors.append(f"日期格式异常: {str(e)}")
        cleaned_data['followup_date'] = None

    try:
        score = float(row.get('score', 0))
        if pd.isna(score):
            errors.append("评分为空")
        else:
            if score < template.score_min or score > template.score_max:
                errors.append(f"评分越界: 应在 {template.score_min}-{template.score_max} 之间")
            cleaned_data['score'] = score
    except (ValueError, TypeError):
        errors.append("评分格式异常")
        cleaned_data['score'] = None

    record_key = (patient_id, cleaned_data.get('followup_date'))
    if patient_id and cleaned_data.get('followup_date'):
        if record_key in existing_records:
            errors.append("重复记录: 同一患者同一日期已存在随访记录")
        else:
            existing_db = db.query(FollowupRecord).filter(
                FollowupRecord.patient_id == patient_id,
                FollowupRecord.followup_date == cleaned_data['followup_date']
            ).first()
            if existing_db:
                errors.append("重复记录: 数据库中已存在该患者此日期的记录")

    if cleaned_data.get('followup_date') and patient_id:
        conflicting_plan = db.query(FollowupPlan).filter(
            FollowupPlan.patient_id == patient_id,
            FollowupPlan.plan_date == cleaned_data['followup_date'],
            FollowupPlan.status == 'pending'
        ).first()
        if conflicting_plan:
            existing_records.add(record_key)

    data_fields = {}
    for key, value in row.items():
        if key not in ['patient_id', 'patient_name', 'followup_date', 'score']:
            if pd.isna(value):
                data_fields[key] = None
            else:
                data_fields[key] = str(value)
    cleaned_data['data'] = str(data_fields) if data_fields else None

    return len(errors) == 0, cleaned_data, errors


def process_upload_file(file_content: bytes, filename: str, template_id: int, user_id: int, db: Session) -> Dict[str, Any]:
    batch_id = generate_batch_id()

    template = db.query(FollowupTemplate).filter(FollowupTemplate.id == template_id).first()
    if not template:
        raise ValueError("模板不存在")

    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(BytesIO(file_content))
        else:
            raise ValueError("不支持的文件格式，请上传CSV或Excel文件")
    except Exception as e:
        raise ValueError(f"文件解析失败: {str(e)}")

    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

    required_columns = ['patient_id', 'followup_date', 'score']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"缺少必要列: {', '.join(missing_cols)}")

    total_rows = len(df)
    success_count = 0
    error_count = 0
    errors = []
    success_records = []
    existing_records = set()

    for idx, row in df.iterrows():
        row_num = idx + 2
        is_valid, cleaned_data, row_errors = validate_row(row.to_dict(), row_num, template, existing_records, db)

        if is_valid:
            try:
                record = FollowupRecord(
                    patient_id=cleaned_data['patient_id'],
                    patient_name=cleaned_data['patient_name'],
                    template_id=template_id,
                    followup_date=cleaned_data['followup_date'],
                    score=cleaned_data['score'],
                    data=cleaned_data['data'],
                    uploaded_by=user_id,
                    batch_id=batch_id
                )
                db.add(record)
                db.flush()

                existing_records.add((cleaned_data['patient_id'], cleaned_data['followup_date']))
                success_count += 1
                success_records.append(RecordResponse.model_validate(record))

                check_score_abnormality(record, db)

            except Exception as e:
                error_count += 1
                error_record = ErrorRecord(
                    batch_id=batch_id,
                    row_number=row_num,
                    patient_id=cleaned_data.get('patient_id'),
                    error_type="保存失败",
                    error_message=str(e),
                    row_data=str(row.to_dict())
                )
                db.add(error_record)
                errors.append(ErrorRecordResponse.model_validate(error_record))
        else:
            error_count += 1
            error_record = ErrorRecord(
                batch_id=batch_id,
                row_number=row_num,
                patient_id=cleaned_data.get('patient_id'),
                error_type="校验失败",
                error_message="; ".join(row_errors),
                row_data=str(row.to_dict())
            )
            db.add(error_record)
            errors.append(ErrorRecordResponse.model_validate(error_record))

    audit_log = AuditLog(
        user_id=user_id,
        action="批量上传随访记录",
        batch_id=batch_id,
        details=f"总行数: {total_rows}, 成功: {success_count}, 失败: {error_count}"
    )
    db.add(audit_log)
    db.commit()

    return {
        "batch_id": batch_id,
        "total_rows": total_rows,
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors,
        "success_records": success_records
    }


def check_score_abnormality(record: FollowupRecord, db: Session):
    previous = db.query(FollowupRecord).filter(
        FollowupRecord.patient_id == record.patient_id,
        FollowupRecord.followup_date < record.followup_date
    ).order_by(FollowupRecord.followup_date.desc()).first()

    if previous:
        change = record.score - previous.score
        if abs(change) >= 20:
            alert_type = "评分大幅下降" if change < 0 else "评分大幅上升"
            alert = Alert(
                patient_id=record.patient_id,
                patient_name=record.patient_name,
                alert_type=alert_type,
                message=f"患者评分从 {previous.score} 变为 {record.score}，变化幅度超过20分",
                record_id=record.id
            )
            db.add(alert)
