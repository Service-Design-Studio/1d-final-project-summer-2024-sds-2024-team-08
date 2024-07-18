from langgraph.checkpoint.base import (
    BaseCheckpointSaver, 
    CheckpointTuple, 
    CheckpointMetadata, 
    SerializerProtocol)

from typing import Optional, Dict, Iterator, Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint import Checkpoint

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from .models import Checkpoint_ORM

class PostgreSQLMemorySaver(BaseCheckpointSaver):
    def __init__(self, engine, *, serde: Optional[SerializerProtocol] = None) -> None:
        super().__init__(serde=serde)
        self.engine = engine

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]

        query = select(Checkpoint_ORM).where(Checkpoint_ORM.chat_id == thread_id)
        
        if ts := config["configurable"].get("thread_ts"):
            query = query.where(Checkpoint_ORM.timestamp == ts)
        else:
            query = query.order_by(Checkpoint_ORM.timestamp.desc())
        
        with Session(self.engine) as s:
            checkpoint = s.scalars(query.limit(1)).one_or_none()
        
        if checkpoint is None: return

        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "thread_ts": checkpoint.timestamp}},
            checkpoint=self.serde.loads(checkpoint.cp_data),
            metadata=self.serde.loads(checkpoint.metadata_data),
        )

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        query = select(Checkpoint_ORM)
        
        if config:
            query = query.where(Checkpoint_ORM.cp_id.in_([config["configurable"]["thread_id"]]))
        
        if before:
            query = query.where(Checkpoint_ORM.timestamp <= before["configurable"]["thread_ts"])
        
        with Session(self.engine) as s:
            checkpoints = s.scalars(query).all()
        
        for checkpoint in checkpoints:
            metadata_data = self.serde.loads(checkpoint.metadata_data)
            if any(metadata_data[k] != v for k, v in filter.items()):
                continue

            if limit is not None:
                if limit <= 0:
                    return
                limit -= 1

            yield CheckpointTuple(
                config={"configurable": {"thread_id": checkpoint.chat_id, "thread_ts": checkpoint.timestamp}},
                checkpoint=self.serde.loads(checkpoint.cp_data),
                metadata_data=metadata_data
            )
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        chat_id = config["configurable"]["thread_id"]

        with Session(self.engine) as s:
            query = insert(Checkpoint_ORM).values(
                chat_id=chat_id,
                cp_data=self.serde.dumps(checkpoint),
                metadata_data=self.serde.dumps(metadata),
            )
            query = query.on_conflict_do_update(
                index_elements=[Checkpoint_ORM.chat_id],
                set_=query.excluded
            ).returning(Checkpoint_ORM.timestamp)
            
            ts = s.scalar(query)
            
            s.commit()
        
        return {
            "configurable": {
                "thread_id": chat_id,
                "thread_ts": ts,
            }
        }