from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
import crud, schemas, langc, models
from database import stakeholder_engine, user_engine, media_engine




def get_media_id_from_stakeholder(db: Session, id: int= None, media_id : int = None, stakeholder_id: int = None):
  query = db.query(models.StakeholdersMentioned)
  
  if stakeholder_id is not None:
    query = query.filter(models.StakeholdersMentioned.stakeholder_id == stakeholder_id)

  if media_id is not None:
    query = query.filter(models.StakeholderMentioned.media_id == media_id)

  results = query.all()
  return results


def get_media_id_from_stakeholder(db: Session, stakeholder_id):
    with Session as s:
        media_ids = get_media_id_from_stakeholder(s, stakeholder_id=stakeholder_id)
    return media_ids
if __name__ == '__main__':
    print(get_stakeholders(media_engine, stakeholder_id= 22183))
    