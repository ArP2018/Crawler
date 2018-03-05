#encoding:utf-8
DB_HOST = '10.13.*.*'
DB_NAME = '***'
DB_USER_NAME = '***'
PASSWORD = '***'

INSERT_ZB_SQL = 'INSERT INTO scp.NDS_PAR_INDEX(index_id, index_name, parent_index_id, parent_index_name, status, creat_time, update_time, unit)' \
                    ' VALUES("%s", "%s", "%s", "%s", "active", "%s", "%s", "%s")'

LANGUAGE = 'CN'

NODE_URL = 'http://data.stats.gov.cn/easyquery.htm'
NODE_URL_EN = 'http://data.stats.gov.cn/english/easyquery.htm'

LOAD_FACT = True

# SQL_INSERT_NODES = 'INSERT INTO scp.NDS_PAR_INDEX(index_id, index_name, index_desc, parent_index_id, parent_index_name, status, creat_time, ' \
#         'update_time, unit) VALUES(%s, %s, %s, %s, %s, "active", %s, %s, %s)'

SQL_INSERT_REG_NODES = 'INSERT INTO scp.NDS_LOC_PAR_INDEX(index_id, index_name, index_desc, parent_index_id, parent_index_name, creat_time, ' \
        'update_time, unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'

SQL_INSERT_NODES_EN = 'INSERT INTO scp.NDS_PAR_INDEX_ENS(index_id, index_name, index_desc, parent_index_id, parent_index_name, status, creat_time, ' \
        'update_time, unit) VALUES(%s, %s, %s, %s, %s, "active", %s, %s, %s)'

SQL_DELETE_NODES = 'truncate table NDS_PAR_INDEX'
SQL_DELETE_NODES_ENS = 'truncate table NDS_PAR_INDEX_ENS'

SQL_INSERT_NODES = 'INSERT INTO NDS_PAR_INDEX(index_id, index_name, index_desc, parent_index_id, parent_index_name, creat_time, ' \
        'update_time, unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'

SQL_DELETE_LOC_NODES = 'truncate table NDS_LOC_PAR_INDEX'
SQL_INSERT_LOC_NODES = 'INSERT INTO NDS_LOC_PAR_INDEX(index_id, index_name, index_desc, parent_index_id, parent_index_name, creat_time, ' \
        'update_time, unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'

SQL_INSERT_LOC_NODES_EN = 'INSERT INTO scp.NDS_LOC_PAR_INDEX_ENS(index_id, index_name, index_desc, parent_index_id, parent_index_name, creat_time, ' \
        'update_time, unit) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'

SQL_INSERT_FACT_DATA = 'INSERT INTO scp.NDS_LOC_FCT_FY_INDEX(area_id, `year`, index_id, index_value, creat_time, update_time)' \
            ' VALUES(%s, %s, %s, %s, %s, %s)'
SQL_DELETE_FS_FACT = 'truncate table NDS_LOC_FCT_FY_INDEX'

ZHIBIAO_URL = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"%s"}]&k1=%s'
ZHIBIAO_URL_EN = 'http://data.stats.gov.cn/english/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=[]&dfwds=[{"wdcode":"zb","valuecode":"%s"}]&k1=%s'


#获取省份名称列表
REGION_LIST_URL = 'http://data.stats.gov.cn/easyquery.htm?m=getOtherWds&dbcode=fsnd&rowcode=zb&colcode=sj&wds=[{"wdcode":"zb","valuecode":"A0101"}]&k1=%s'

#获取省份指标数据
REGION_ZB_URL = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=fsnd&rowcode=zb&colcode=sj&' \
                'wds=[{"wdcode":"reg","valuecode":"%s"}]&dfwds=[{"wdcode":"zb","valuecode":"%s"}]&k1=%s'

REGION_ZB_URL_EN = 'http://data.stats.gov.cn/english/easyquery.htm?m=QueryData&dbcode=fsnd&rowcode=zb&colcode=sj&' \
                   'wds=[{"wdcode":"reg","valuecode":"110000"}]&dfwds=[{"wdcode":"zb","valuecode":"%s"}]&k1=%s'
