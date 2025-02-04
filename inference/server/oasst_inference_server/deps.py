import contextlib

import redis.asyncio as redis
import sqlmodel
from fastapi import Depends
from oasst_inference_server import auth
from oasst_inference_server.chat_repository import ChatRepository
from oasst_inference_server.database import db_engine
from oasst_inference_server.settings import settings
from oasst_inference_server.user_chat_repository import UserChatRepository

# create async redis client
redis_client = redis.Redis(
    host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True
)


def create_session():
    with sqlmodel.Session(db_engine) as session:
        yield session


@contextlib.contextmanager
def manual_create_session():
    with contextlib.contextmanager(create_session)() as session:
        yield session


def create_chat_repository(session: sqlmodel.Session = Depends(create_session)) -> ChatRepository:
    repository = ChatRepository(session)
    return repository


def create_user_chat_repository(
    session: sqlmodel.Session = Depends(create_session),
    user_id: str = Depends(auth.get_current_user_id),
) -> UserChatRepository:
    repository = UserChatRepository(session, user_id)
    return repository


@contextlib.contextmanager
def manual_chat_repository():
    with manual_create_session() as session:
        yield create_chat_repository(session)


@contextlib.contextmanager
def manual_user_chat_repository(user_id: str):
    with manual_create_session() as session:
        yield create_user_chat_repository(session, user_id)
