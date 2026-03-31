from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.db.connection import get_db
from app.schemas.analytics import SummaryResponse, CategoryBreakdown

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=SummaryResponse)
async def get_summary(db: AsyncIOMotorDatabase = Depends(get_db)):
    
    
    pipeline = [
        {"$group": {"_id": "$type", "total": {"$sum": "$amount"}}}
    ]
    cursor = db["transactions"].aggregate(pipeline)
    results = await cursor.to_list(length=None)

    income = 0.0
    expense = 0.0
    
    for r in results:
        if r["_id"] == "income":
            income = float(r["total"])
        elif r["_id"] == "expense":
            expense = float(r["total"])

    return SummaryResponse(
        total_income=income,
        total_expense=expense,
        net_balance=income - expense
    )

@router.get("/category", response_model=list[CategoryBreakdown])
async def get_category_breakdown(db: AsyncIOMotorDatabase = Depends(get_db)):
    
    pipeline = [
        {"$match": {"type": "expense"}},  # Only look at expenses
        {"$group": {"_id": "$category_id", "total_amount": {"$sum": "$amount"}}}, # Group by category
        {"$sort": {"total_amount": -1}}   # Sort highest to lowest
    ]
    cursor = db["transactions"].aggregate(pipeline)
    results = await cursor.to_list(length=None)

    breakdown = []
    for r in results:
        cat_name = r["_id"] if r["_id"] else "Uncategorized"
        breakdown.append(CategoryBreakdown(category=cat_name, total_amount=float(r["total_amount"])))

    return breakdown