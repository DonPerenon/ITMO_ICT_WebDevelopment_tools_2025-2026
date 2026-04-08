from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.db.session import get_session
from app.models import Goal, User
from app.schemas.goals import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("", response_model=list[GoalRead])
def goals_list(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Goal]:
    return session.exec(select(Goal).where(Goal.user_id == current_user.id)).all()


@router.get("/{goal_id}", response_model=GoalRead)
def goals_get(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.post("", response_model=GoalRead, status_code=201)
def goals_create(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    goal = Goal(
        title=payload.title,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        deadline=payload.deadline,
        user_id=current_user.id,
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def goals_update(
    goal_id: int,
    payload: GoalUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Goal:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(goal, key, value)

    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.delete("/{goal_id}")
def goals_delete(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    goal = session.get(Goal, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Goal not found")

    session.delete(goal)
    session.commit()
    return {"ok": True}
