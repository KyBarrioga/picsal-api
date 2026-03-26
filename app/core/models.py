"""This project no longer defines Django-managed database models.

Supabase owns authentication, the profiles table, and the schema lifecycle.
The Django app acts only as an API layer over the existing Supabase database.
"""
