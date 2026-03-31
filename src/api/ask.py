from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/ask", tags=["ask"])

