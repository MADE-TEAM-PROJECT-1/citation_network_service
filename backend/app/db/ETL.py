import pandas as pd
from sqlalchemy import create_engine
import uuid


engine = create_engine('postgresql://postgres:postgres@0.0.0.0:5432/postgres')
df = pd.DataFrame()
for i in range(1,4):
    df = pd.concat([df, pd.read_json('data/part_'+str(i)+'_clean.json')], ignore_index=True)
    
df = df.rename(columns = {'venue' : 'venue_name'})
df['venue_name'] = df['venue_name'].apply(lambda x: list(x.values()))


# filling in the table "text"
df.loc[:, 'UUID_id'] = df['_id'].apply(lambda x: uuid.uuid4())
text_df = df[['UUID_id', 'title','year','n_citation','abstract','venue_name']]
text_df = text_df.rename(columns = {'UUID_id' : 'id'})
text_df.to_sql('text', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "authors"
authors_dict = {}
tmp_l = []
for i in df['authors']:
    l_local = []
    for j in i:
        u = uuid.uuid4()
        if list(j.values())[0] not in authors_dict:
            authors_dict[list(j.values())[0]] = [u,list(j.values())[1]]
            l_local.append(u)
        else:
            l_local.append(authors_dict[list(j.values())[0]][0])
    tmp_l.append(l_local)
df.loc[:,'UUID_authors'] = tmp_l      
autors_df = pd.DataFrame()
autors_df['id_name'] = authors_dict.values()
autors_df['id'] = autors_df['id_name'].apply(lambda x: x[0])
autors_df['name'] = autors_df['id_name'].apply(lambda x: x[1])
del autors_df['id_name']
autors_df.to_sql('author', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "text_autor"
tmp_l = []
for i, row in df[['UUID_id','UUID_authors']].iterrows():
    for UUID_author in row['UUID_authors']:
        tmp_l.append((uuid.uuid4(),row['UUID_id'],UUID_author))        
text_autor_df = pd.DataFrame(tmp_l, columns=['author_keywords_id', 'text_id', 'author_id'])
text_autor_df.to_sql('text_author', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "org"
org_dict = {}
tmp_l = []
for i in df['authors']:
    l_local = []
    for j in i:
        if 'org' in j.keys():
            if j['org'] not in org_dict:
                u = uuid.uuid4()
                org_dict[j['org']] = u
                l_local.append(u)
            else:
                l_local.append(org_dict[j['org']])
    tmp_l.append(l_local)    
df.loc[:,'UUID_org'] = tmp_l
org_df = pd.DataFrame()
org_df['name'] = org_dict.keys()
org_df['id'] = org_dict.values()
org_df.to_sql('org', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "org_author"
tmp_l = []
for i, row in df[['UUID_org','UUID_authors']].iterrows():
    if row['UUID_org'] != []:
        for UUID_org, UUID_author in zip(row['UUID_org'],row['UUID_authors']):
            tmp_l.append((uuid.uuid4(),UUID_org,UUID_author))     
org_autor_df = pd.DataFrame(tmp_l, columns=['org_author_id', 'org_id', 'author_id'])
org_autor_df.to_sql('org_author', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "fos"
fos_dict = {}
tmp_l = []
for i, row in df[['UUID_id','fos']].iterrows():
    for j in row['fos']:
        if j not in fos_dict:
            fos_dict[j] = uuid.uuid4()
        tmp_l.append((uuid.uuid4(),row['UUID_id'],fos_dict[j],j))       
df_text_fos_fosid = pd.DataFrame(tmp_l, columns=['text_fos_fosid','UUID_id','UUID_fos','fos'])
df_fos = df_text_fos_fosid[['UUID_fos','fos']]
df_fos.columns = ['id','name']
df_fos = df_fos.drop_duplicates()
df_fos.to_sql('fos', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "text_fos"
df_text_fos = df_text_fos_fosid[['text_fos_fosid','UUID_fos','UUID_id']]
df_text_fos.columns = ['text_fos_id','fos_id','text_id']
df_text_fos.to_sql('text_fos', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "keywords"
keywords_dict = {}
tmp_l = []
for i, row in df[['UUID_id','keywords']].iterrows():
    for j in row['keywords']:
        if j not in keywords_dict:
            keywords_dict[j] = uuid.uuid4()
        tmp_l.append((uuid.uuid4(),row['UUID_id'],keywords_dict[j],j))        
df_text_keywords_keywordsid = pd.DataFrame(tmp_l, columns=['text_keywords_keywordsid','UUID_id','UUID_keywords','keywords'])
df_keywords = df_text_keywords_keywordsid[['UUID_keywords','keywords']]
df_keywords.columns = ['id','name']
df_keywords = df_keywords.drop_duplicates()
df_keywords.to_sql('keywords', con=engine, schema='citation_network', if_exists='append', index=False)


# filling in the table "text_keywords"
df_text_keywords = df_text_keywords_keywordsid[['text_keywords_keywordsid','UUID_keywords','UUID_id']]
df_text_keywords.columns = ['text_keywords_id','keyword_id','text_id']
df_text_keywords.to_sql('text_keywords', con=engine, schema='citation_network', if_exists='append', index=False)
