#!/usr/bin/env python3
"""Migration script for postgres_air database."""

import os
import psycopg2

DATABASE_URL = "postgresql://user:pass@localhost:5432/postgres_air"

def connect_to_postgres_air():
    """Connect to the postgres_air database."""
    return psycopg2.connect(DATABASE_URL)