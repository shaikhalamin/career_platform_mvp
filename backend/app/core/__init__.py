"""Core infrastructure: config, database, envelope, exceptions, dependencies.

Everything cross-cutting lives here; domain code (models, schemas, services,
api) builds on top of this package and never reimplements it.
"""
