from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    OVEN_TYPE_STONE,
    OVEN_TYPE_TRAY,
    Batch,
    ConflictLog,
    Oven,
    Product,
)


def seed_if_empty(db: Session) -> None:
    # 炉型只认 oven_type 字段，不从标签/备注文字推断
    if db.scalar(select(Product.id).limit(1)):
        # 旧库补一个只要石板的产品，便于演示炉型不符拦截
        has_stone = db.scalar(
            select(Product.id).where(Product.oven_type == OVEN_TYPE_STONE).limit(1)
        )
        if not has_stone:
            db.add(Product(name="石板法棍", ferment_min=45, bake_min=30, oven_type=OVEN_TYPE_STONE))
        db.commit()
        return

    products = [
        Product(name="乡村欧包", ferment_min=40, bake_min=35, oven_type=OVEN_TYPE_TRAY),
        Product(name="黄油可颂", ferment_min=25, bake_min=20, oven_type=OVEN_TYPE_TRAY),
        Product(name="布朗尼", ferment_min=0, bake_min=30, oven_type=OVEN_TYPE_TRAY),
        # 只可进石板炉的产品
        Product(name="石板法棍", ferment_min=45, bake_min=30, oven_type=OVEN_TYPE_STONE),
    ]
    ovens = [
        Oven(label="一层 1 号炉", capacity_note="盘炉", oven_type=OVEN_TYPE_TRAY),
        Oven(label="一层 2 号炉", capacity_note="盘炉", oven_type=OVEN_TYPE_TRAY),
        Oven(label="二层石板炉", capacity_note="石板", oven_type=OVEN_TYPE_STONE),
    ]
    db.add_all(products + ovens)
    db.flush()
    db.add_all(
        [
            Batch(product_id=products[0].id, oven_id=ovens[0].id, code="BO-0900", start_min=9 * 60, status="scheduled"),
            Batch(product_id=products[1].id, oven_id=ovens[0].id, code="BO-1030", start_min=10 * 60 + 30, status="scheduled"),
            Batch(product_id=products[2].id, oven_id=ovens[1].id, code="BO-1000", start_min=10 * 60, status="scheduled"),
        ]
    )
    db.add(
        ConflictLog(
            batch_code="BO-试排",
            oven_id=ovens[0].id,
            detail="试算与 BO-0900 烘烤段重叠（半开区间检测）",
        )
    )
    db.commit()
