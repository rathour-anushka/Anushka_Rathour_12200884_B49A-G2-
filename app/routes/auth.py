from fastapi import APIRouter, Form, HTTPException
from ..utils.auth import authenticate_user

router = APIRouter()

