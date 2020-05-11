# init tabels
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import requests
import json

Base = declarative_base()
user = ''
password = ''
db_url = ''
port = ''
db = ''
table_name = ''

# 可选， 高德地图开发key
amap_dev_key = ''
engine = create_engine("mysql+pymysql://{user}:{password}@{url}:{port}/{db}".format(user=user,password=password,url=db_url,port=port, db=db), encoding='utf-8', echo=True)
from sqlalchemy import Column, Integer, String
Base.metadata.create_all(engine)

class RegionCity(Base):
    __tablename__ = table_name
    id = Column(Integer, primary_key=True)
    adcode = Column(String(32))
    citycode = Column(String(32))
    name = Column(String(32))
    center = Column(String(128))
    level = Column(String(16))
    pid = Column(Integer)

def geography_data_init():
    # 高德地图开发key
    # 传送门 - https://lbs.amap.com/api/webservice/guide/api/district
    # 传送门 - https://lbs.amap.com/?ref=https://console.amap.com
    url = 'https://restapi.amap.com/v3/config/district?keywords=中国&subdistrict=5&key={key}'.format(key=amap_dev_key)
    resp = requests.get(url)
    geography_data = resp.text
    return json.loads(geography_data)

# 根据文件读取 - 数据有时效性，2020-5-11 更新
def geography_data_init_by_file():
    path = '../data.txt' # 就是项目中data.txt的路径. 可能根据操作系统会有不一样
    file = open(path, 'r')
    geography_data = file.read()
    return json.loads(geography_data)

def dict2obj(dict):
    obj = dict.mapping()
    obj.__dict__.update(dict)
    return obj

from sqlalchemy.orm import sessionmaker

class MySqlutils(object):

    Session_class = sessionmaker(bind=engine)
    Session = Session_class()
    Base.metadata.create_all(engine)

    # 初始化数据
    def __init__(self):
        pass

    def put(self, obj):
        self.Session.add(obj)
        self.Session.flush()

    def commit(self):
        self.Session.commit()

def build_and_do(district, pid, mySqlutils):
    regionCity = RegionCity()
    regionCity.name = district['name']
    regionCity.adcode = district['name']
    regionCity.center = district['center']
    regionCity.level = district['level']
    regionCity.pid = pid
    if district['citycode'] is None or len(district['citycode']) == 0:
        pass
    else:
        regionCity.citycode = district['citycode']
    mySqlutils.put(regionCity)
    mySqlutils.commit()
    districts = district['districts']
    if len(districts) == 0:
        return
    for c_district in districts:
        build_and_do(c_district, regionCity.id, mySqlutils)

if __name__ == '__main__':
    # 通过高德地图获取
    # geography_data = geography_data_init()
    # 通过历史文件数据获取
    geography_data = geography_data_init_by_file()
    mySqlutils = MySqlutils()
    pid = 0
    country = geography_data['districts'][0]
    build_and_do( country, 0, mySqlutils)


