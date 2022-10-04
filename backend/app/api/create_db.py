from database import Base, engine
from models import Text, Citation, Keyword, Author, Fos, Org, org_author, text_author, text_fos, text_keywords

print('Creating database ...')

Base.metadata.create_all(engine)
