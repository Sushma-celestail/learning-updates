import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, SessionLocal, get_db
import os

# Using global client from conftest.py

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_register_duplicate_user(client):
    client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })
    response = client.post("/auth/register", json={
        "username": "dupuser",
        "email": "another@example.com",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })
    assert response.status_code == 409

def test_register_invalid_email(client):
    response = client.post("/auth/register", json={
        "username": "bademail",
        "email": "invalid-email",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })
    assert response.status_code == 422

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123",
        "phone": "9876543210",
        "monthly_income": 50000
    })
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "loginuser"

def test_login_wrong_password(client):
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
