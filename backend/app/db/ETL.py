import json
import pandas as pd
from sqlalchemy import create_engine
import uuid


engine = create_engine('postgresql://postgres:postgres@0.0.0.0:5432/postgres')
df = pd.DataFrame()
for i in range(17,18):
    with open('data/part_'+str(i)+'_clean.json') as f:
        data = pd.DataFrame()
        templates = json.load(f)
        data['_id'] = templates['_id'].values()
        data['title'] = templates['title'].values()
        data['year'] = templates['year'].values()
        data['fos'] = templates['fos'].values()
        data['n_citation'] = templates['n_citation'].values()
        data['abstract'] = templates['abstract'].values()
        data['references'] = templates['references'].values()
        data['keywords'] = templates['keywords'].values()
        data['authors'] = templates['authors'].values()
        data['authors'] = data['authors'].apply(lambda x: list(x))
        data['venue_name'] = templates['venue'].values()
        data['venue_name'] = data['venue_name'].apply(lambda x: list(x.values())[0])
        df = pd.concat([df, data])      
df_small = df[:1000]


df_small['UUID_id'] = df_small['_id'].apply(lambda x: uuid.uuid4())
text_df = df_small[['UUID_id', 'title','year','n_citation','abstract','venue_name']]
text_df = text_df.rename(columns = {'UUID_id' : 'id'})
text_df.to_sql('text', con=engine, schema='citation_network', if_exists='append', index=False)


d = {}
l = []
for i in df_small['authors']:
    l_local = []
    for j in i:
        u = uuid.uuid4()
        if list(j.values())[0] not in d:
            d[list(j.values())[0]] = [u,list(j.values())[1]]
            l_local.append(u)
        else:
            l_local.append(d[list(j.values())[0]][0])
    l.append(l_local)     
df_small['UUID_authors'] = l       
autors_df = pd.DataFrame()
autors_df['old_id'] = d.keys()
autors_df['id_name'] = d.values()
autors_df['id'] = autors_df['id_name'].apply(lambda x: x[0])
autors_df['name'] = autors_df['id_name'].apply(lambda x: x[1])
del autors_df['id_name']
del autors_df['old_id']
autors_df.to_sql('author', con=engine, schema='citation_network', if_exists='append', index=False)


text_autor_df = pd.DataFrame(columns=['author_keywords_id', 'text_id', 'author_id'])
l = []
for i, row in df_small[['UUID_id','UUID_authors']].iterrows():
    for UUID_author in row['UUID_authors']:
        l.append((uuid.uuid4(),row['UUID_id'],UUID_author))      
text_autor_df = pd.DataFrame(l, columns=['author_keywords_id', 'text_id', 'author_id'])
text_autor_df.to_sql('text_author', con=engine, schema='citation_network', if_exists='append', index=False)


d = {}
tmp = []
for i, row in df_small[['UUID_id','fos']].iterrows():
    for j in row['fos']:
        if j not in d:
            d[j] = uuid.uuid4()
        tmp.append((uuid.uuid4(),row['UUID_id'],d[j],j))         
df_text_fos_fosid = pd.DataFrame(tmp, columns=['text_fos_fosid','UUID_id','UUID_fos','fos'])
df_fos = df_text_fos_fosid[['UUID_fos','fos']]
df_fos.columns = ['id','name']
df_fos = df_fos.drop_duplicates()
df_fos.to_sql('fos', con=engine, schema='citation_network', if_exists='append', index=False)
df_text_fos = df_text_fos_fosid[['text_fos_fosid','UUID_fos','UUID_id']]
df_text_fos.columns = ['text_fos_id','fos_id','text_id']
df_text_fos.to_sql('text_fos', con=engine, schema='citation_network', if_exists='append', index=False)


d = {}
tmp = []
for i, row in df_small[['UUID_id','keywords']].iterrows():
    for j in row['keywords']:
        if j not in d:
            d[j] = uuid.uuid4()
        tmp.append((uuid.uuid4(),row['UUID_id'],d[j],j))       
df_text_keywords_keywordsid = pd.DataFrame(tmp, columns=['text_keywords_keywordsid','UUID_id','UUID_keywords','keywords'])
df_keywords = df_text_keywords_keywordsid[['UUID_keywords','keywords']]
df_keywords.columns = ['id','name']
df_keywords = df_keywords.drop_duplicates()
df_keywords.to_sql('keywords', con=engine, schema='citation_network', if_exists='append', index=False)
df_text_keywords = df_text_keywords_keywordsid[['text_keywords_keywordsid','UUID_keywords','UUID_id']]
df_text_keywords.columns = ['text_keywords_id','keyword_id','text_id']
df_text_keywords.to_sql('text_keywords', con=engine, schema='citation_network', if_exists='append', index=False)