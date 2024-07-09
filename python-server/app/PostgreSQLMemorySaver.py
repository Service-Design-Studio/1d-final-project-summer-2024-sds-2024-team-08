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

from .models import Checkpoint_ORM

class PostgreSQLMemorySaver(BaseCheckpointSaver):
    def __init__(self, engine, *, serde: Optional[SerializerProtocol] = None) -> None:
        super().__init__(serde=serde)
        self.engine = engine

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = config["configurable"]["thread_id"]

        query = select(Checkpoint_ORM).where(Checkpoint_ORM.chat_id == thread_id)
        print(query)
        
        if ts := config["configurable"].get("thread_ts"):
            query = query.where(Checkpoint_ORM.timestamp == ts)
        else:
            query = query.order_by(Checkpoint_ORM.timestamp.desc()).limit(1)
        
        with Session(self.engine) as s:
            checkpoint = s.scalars(query).one_or_none()
        
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
            new_checkpoint = s.scalars(
                select(Checkpoint_ORM)
                .where(Checkpoint_ORM.chat_id == chat_id)).one_or_none()
            
            if new_checkpoint is None:
                new_checkpoint = Checkpoint_ORM()
                new_checkpoint.chat_id = chat_id
            
            new_checkpoint.cp_data = self.serde.dumps(checkpoint)
            new_checkpoint.metadata_data = self.serde.dumps(metadata)
            
            s.add(new_checkpoint)
            s.commit()
            ts = new_checkpoint.timestamp
        
        return {
            "configurable": {
                "thread_id": chat_id,
                "thread_ts": ts,
            }
        }