from sqlalchemy import create_engine, MetaData
#import oracledb

#初始化ORACLE客户端
#oracledb.init_oracle_client(lib_dir=r"D:\DB\oracle11g\product\11.2.0\dbhome_1\BIN")

#数据库引擎
#oracle_engine = create_engine('oracle+oracledb://{user}:{password}@{ip}:{port}?service_name={db}'.format(user='dd_portal', password='dd_portal', ip='127.0.0.1', port=1521, db='orcl'), echo=True)

postgre_engine = create_engine('postgresql+psycopg2://{user}:{password}@{ip}:{port}/{database}'.format(user='dev', password='dev', ip='127.0.0.1', port=5432, database='postgres'), echo=True)

# 把当前的引擎绑定给这个会话
#oracle_metadata = MetaData()

postgre_metadata = MetaData()
