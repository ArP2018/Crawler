# encoding:utf-8
import json
from collections import OrderedDict
import re

import sys
from lxml import etree
import MySQLdb
import datetime
import requests

from myutility import *
from config import *
from selenium import webdriver

# def gen_session():
# #使用sqlalchemy做ORM时，数据库表必须有主键
#     engine = sqlalchemy.create_engine(r'mysql+mysqldb://webcrawler:fd909d69c7b164406f59@10.13.1.76/scp?charset=utf8')
#     session = Session(engine)
#     Base = automap_base()
#     Base.prepare(engine, reflect=True)
#     return session


CONN = MySQLdb.connect(DB_HOST, DB_USER_NAME, PASSWORD, DB_NAME, charset='utf8')
CURSOR = CONN.cursor()

if LANGUAGE == 'EN':
    node_url = NODE_URL_EN
else:
    node_url = NODE_URL


# 构造第一层父节点code
# 第一层父节点code A01 - A09  A0A - A0S []
# level0 = [{'dbcode': 'hgnd', 'id': 'A0' + str(i), 'm': 'getTree', 'wdcode': 'zb'} for i in range(1, 10)]
# level0.extend([{'dbcode': 'hgnd', 'id': 'A0' + s, 'm': 'getTree', 'wdcode': 'zb'} for s in string.ascii_uppercase[:string.ascii_uppercase.find('S')+1]])
# 初始化第一级节点
def search_parents():
    # 手动分析页面请求拿到以下post 参数，向node_url发起请求，带上post参数，返回包含所有最上级指标的json对象
    # json对象中的每一项格式为{"dbcode":"hgnd","id":"A0101","isParent":false,"name":"行政区划","pid":"A01","wdcode":"zb"}
    post_data = {'dbcode': 'hgnd', 'id': 'zb', 'm': 'getTree', 'wdcode': 'zb'}
    resp_text = requests.post(node_url, post_data).text
    resp_json = json.loads(resp_text)
    print(resp_json)
    return resp_json


# 存放所有中间节点
CHILD_NODES = []


def search_children(p_node):
    '''
    传入一个父节点，通过父节点里的各个属性值构造post参数，发送请求到node_url，返回所有直属于该父节点的子节点
    :param p_node:  父节点， 格式如{"dbcode":"hgnd","id":"A0202","isParent":true,"name":"国内生产总值指数","pid":"A02","wdcode":"zb"}
    :return:
    '''

    post_data = {'dbcode': p_node['dbcode'], 'id': p_node['id'], 'm': 'getTree', 'wdcode': p_node['wdcode']}
    resp_text = requests.post(node_url, post_data).text
    resp_json = json.loads(resp_text)

    for temp_node in resp_json:
        node = temp_node
        node['p_name'] = p_node['name']  # 数据库需要存入父节点name

        CHILD_NODES.append(node)
        # 如果节点是父节点，就递归调用本方法，取出该节点下面的子节点
        if temp_node['isParent']:
            search_children(temp_node)


if LANGUAGE == 'EN':
    zhibiao_url = ZHIBIAO_URL_EN
else:
    zhibiao_url = ZHIBIAO_URL


# print urllib.unquote(zhibiao_url)
def search_zhibiao(node):
    '''
    根据传入的节点，构造请求的url，发送url请求，得到返回的json对象，从json对象里取出该节点对应的所有指标每一年的值
    :param node: {"dbcode":"hgnd","id":"A0101","isParent":false,"name":"行政区划","pid":"A01","wdcode":"zb"}
    :return:
    '''
    # params = {
    #     'colcode': 'sj',
    #     'dbcode': 'hgnd',
    #     'dfwds': '[{"wdcode": "zb", "valuecode": %s}]'%code,
    #     'k1': int(time.time()),
    #     'm': 'QueryData',
    #     'rowcode': 'zb',
    #     'wds': '[]'
    # }
    url = zhibiao_url % (node['id'], str(int(time.time())))

    resp_text = requests.post(url).text
    # 返回结果有两个部分，一个部分是各年份数据，一个部分是指标名，指标名为最细的

    try:
        resp_json = json.loads(resp_text, strict=False)
    except:
        print("%s has issue" % url)
        return

    # print resp_json
    if LOAD_FACT:
        zb_fact_data = []
        zhibiao_data = resp_json['returndata']['datanodes']
        for data in zhibiao_data:
            area_id = 0  # 国家id设为0
            zb_value = data['data']['data']
            zb_code = data['wds'][0]['valuecode']
            zb_year = data['wds'][1]['valuecode']

            zb_fact_data.append((area_id, zb_year, zb_code, zb_value, datetime.datetime.now(), datetime.datetime.now()))

        CURSOR.executemany(
            'INSERT INTO scp.NDS_FCT_FY_INDEX(area_id, `year`, index_id, index_value, status, creat_time, update_time)'
            ' VALUES(%s, %s, %s, %s, "active", %s, %s)', zb_fact_data)
        CONN.commit()

    zb_dim_data = []
    zbs = resp_json['returndata']['wdnodes'][0]['nodes']
    for zb in zbs:
        zb_code = zb['code']
        zb_name = zb['name'][:300]
        zb_pcode = node['id']
        zb_pname = node['name']
        zb_comment = zb['exp'][:300]
        zb_unit = zb['unit']

        zb_dim_data.append((zb_code, zb_name, zb_comment, zb_pcode, zb_pname, datetime.datetime.now(),
                            datetime.datetime.now(), zb_unit))

    nodes_to_db(zb_dim_data)


# search_zhibiao({'id':'A0101','name':'测试指标'})
# search_children({'dbcode': 'hgnd', 'id': 'A0O', 'm': 'getTree', 'wdcode': 'zb'})

# search_children(search_parents()[0])

def save_nodes():
    '''

    :return:
    '''
    parent_nodes = search_parents()
    if LANGUAGE == 'EN':
        sql = SQL_DELETE_NODES
    else:
        sql = SQL_DELETE_NODES
    CURSOR.execute(sql)
    CONN.commit()
    all_nodes = []
    for p_node in parent_nodes:
        all_nodes.append(
            (p_node['id'], p_node['name'], '', '0', '', datetime.datetime.now(), datetime.datetime.now(), ''))
        search_children(p_node)

    for node in CHILD_NODES:
        all_nodes.append((node['id'], node['name'], '', node['pid'], node['p_name'], datetime.datetime.now(),
                          datetime.datetime.now(), ''))

    nodes_to_db(all_nodes)


def nodes_to_db(nodes_list):
    if LANGUAGE == 'EN':
        sql = SQL_INSERT_NODES_EN
    else:
        sql = SQL_INSERT_NODES
    CURSOR.executemany(sql, nodes_list)
    CONN.commit()


# 行政区划数据
def get_areas():
    area_dict = OrderedDict()
    area_url = 'http://www.stats.gov.cn/tjsj/tjbz/xzqhdm/201703/t20170310_1471429.html'
    # 使用requests包抓下来的页面源码是乱码，不知道什么原因
    # user_agent = myutility.get_rand_ua()
    # header = {'User-Agent': user_agent}
    # resp = requests.get(area_url, headers=header)
    driver = webdriver.PhantomJS()
    driver.set_window_size(1200, 900)

    driver.get(area_url)

    area_nodes = etree.HTML(driver.page_source).xpath('//p[@class="MsoNormal"]')

    for area in area_nodes:
        # print area.xpath('.//text()')
        area_text = ''.join(area.xpath('.//text()')).replace(u'\xa0', '').replace(u'\u3000', '')
        area_code = re.search(r'(\d+)', area_text).group()
        area_name = re.search(r'([\u4e00-\u9fa5]+)', area_text).group()
        area_dict[area_code] = area_name

    driver.close()

    return area_dict


# 行政区划数据爬取
@timer
def save_areas():
    area_dict = get_areas()
    if area_dict:
        CURSOR.execute('truncate table NDS_PAR_ADMIN_AREA')

        for area_code in area_dict.keys():
            if area_code[4:] == '00' and area_code[2:4] == '00':
                area_pid = 0
                area_p_name = u'中国'
            elif area_code[4:] == '00':
                area_pid = int(area_code[0:2] + '0000')
                area_p_name = area_dict[str(area_pid)]
                # print area_dict[str(area_pid)]
            else:
                area_pid = int(area_code[0:4] + '00')
                area_p_name = area_dict[str(area_pid)]
                # print area_dict[str(area_pid)]

            sql = 'INSERT INTO scp.NDS_PAR_ADMIN_AREA ' \
                  '(AREA_ID, AREA_NAME, PARENT_AREA_ID, PARENT_AREA_NAME, CREAT_TIME, UPDATE_TIME) ' \
                  'VALUES("%d", "%s", "%d", "%s", "%s", "%s")' % (int(area_code), area_dict[area_code], area_pid,
                                                                  area_p_name,
                                                                  datetime.datetime.now(), datetime.datetime.now())
            try:
                CURSOR.execute(sql)
            except MySQLdb.MySQLError:
                print u"行政区数据插入失败"

        CONN.commit()


# 获取省级名称列表
def get_region_codes(url):
    region_data_url = url % str(int(time.time()))
    resp = requests.get(region_data_url)
    resp_json = resp.json()

    region_nodes = resp_json['returndata'][0]['nodes']
    return [node['code'] for node in region_nodes]


# 获取省级的指标
def get_region_zb(url):
    '''
    传入拿取指标json数据的url，返回一个字典
    :param url:
    :return: 返回左边指标节点树形结构，类型为dict，key是指标的code
    '''
    node_dict = {}

    def get_nodes(code):
        post_data = {'dbcode': 'fsnd', 'id': code, 'm': 'getTree', 'wdcode': 'zb'}
        # 全国指标
        # post_data = {'dbcode': 'hgnd', 'id': code, 'm': 'getTree', 'wdcode': 'zb'}

        time.sleep(1)
        resp = requests.post(url, post_data)
        resp_json = resp.json()

        for node in resp_json:
            # print node
            id = node['id']
            pid = node['pid']
            if pid == '':
                node['pname'] = 'zb'
            else:
                node['pname'] = node_dict[pid]['name']

            node_dict[id] = node

            if node['isParent']:
                get_nodes(node['id'])

    get_nodes('zb')

    return node_dict


def save_zb(nodes, sql):
    if nodes:
        all_records = []
        for node in nodes:
            unit = ''
            desc = ''

            all_records.append((node['id'], node['name'][:300], desc, node['pid'], node['pname'],
                                datetime.datetime.now(), datetime.datetime.now(), unit))

        try:
            CURSOR.executemany(sql, all_records)
            CONN.commit()
        except:
            print('insert index failure')


def save_zb_mx(nodes, pid, pname, sql):
    if nodes:
        all_records = []
        for node in nodes:
            all_records.append((node['code'], node['name'][:300], node['exp'][:300], pid, pname,
                                datetime.datetime.now(), datetime.datetime.now(), node['unit']))

        # try:
        #     CURSOR.executemany(SQL_INSERT_NODES, all_records)
        #     CONN.commit()
        # except:
        #     print 'insert index failure'
        CURSOR.executemany(sql, all_records)
        CONN.commit()


def save_zb_value(data, **kwargs):
    if data:
        all_records = []
        for d in data:
            if kwargs:
                area_id = kwargs['reg_id']
            else:
                area_id = 0  # 国家id设为0
            zb_value = d['data']['data']
            zb_code = d['wds'][0]['valuecode']
            # 分省的年份值的index是2，
            zb_year = d['wds'][2]['valuecode']

            all_records.append((area_id, zb_year, zb_code, zb_value, datetime.datetime.now(), datetime.datetime.now()))

        CURSOR.executemany(SQL_INSERT_FACT_DATA, all_records)
        CONN.commit()


def get_zb_fact_data(url, zb_id, load_fact=True, **kwargs):
    '''

    :param url: 两种url，全国的和省份的，全国的包括两个url参数，省份的包括三个url参数（多一个省份code）
    :param zb_id 表示指标code
    :param load_fact 表示要不要解析fact data， 默认为True
    :param kwargs:  reg_id 表示region（各省份）的代码
    :return:返回一个字典，字典包括两部分，'fact' key存储对应明细指标的数值, 'dim' key存储明细指标的名字
    '''
    zb_data = {}
    k_time = str(int(time.time()))
    if kwargs:
        fact_data_url = url % (kwargs['reg_id'], zb_id, k_time)
    else:
        fact_data_url = url % (zb_id, k_time)

    resp_text = requests.post(fact_data_url).text
    # 返回结果有两个部分，一个部分是各年份数据，一个部分是指标名，指标名为最细的

    try:
        resp_json = json.loads(resp_text, strict=False)
    except:
        print("%s has issue" % fact_data_url)
        return

    # print resp_json
    if load_fact:
        zb_fact_data = resp_json['returndata']['datanodes']
        zb_data['fact'] = zb_fact_data
    else:
        zb_data['fact'] = ''
    try:
        zb_dim_data = resp_json['returndata']['wdnodes'][0]['nodes']
        zb_data['dim'] = zb_dim_data
    except:
        print(zb_id)
        print(resp_json['returndata'])

    return zb_data


# 分省年度数据
@timer
def crawl_year_region_data():
    region_codes = get_region_codes(REGION_LIST_URL)

    CURSOR.execute(SQL_DELETE_LOC_NODES)
    CURSOR.execute(SQL_DELETE_FS_FACT)
    CONN.commit()

    zb_nodes = get_region_zb(NODE_URL)
    save_zb(zb_nodes.values(), SQL_INSERT_LOC_NODES)

    for zb in zb_nodes.values():
        counter = 0
        if not zb['isParent']:
            for region in region_codes:
                time.sleep(1)
                zb_data = get_zb_fact_data(REGION_ZB_URL, zb['id'], reg_id=region)
                if zb_data:
                    if counter == 0:
                        save_zb_mx(zb_data['dim'], zb['id'], zb['name'], SQL_INSERT_LOC_NODES)
                    save_zb_value(zb_data['fact'], reg_id=region)
                    counter += 1


# 年度数据
@timer
def crawl_year_data():
    save_nodes()
    for node in CHILD_NODES:
        time.sleep(0.5)
        if not node['isParent']:
            search_zhibiao(node)

    CURSOR.close()
    CONN.close()


if __name__ == '__main__':
    param = sys.argv[1]
    if param == 'year':
        crawl_year_data()
    elif param == 'year_region':
        crawl_year_region_data()
    else:
        print(u'请传入合法参数')
        pass

    # print get_zb_fact_data(REGION_ZB_URL, 'A010301')
    # # save_region_zb(NODE_URL)
    # zb_nodes = get_region_zb(NODE_URL_EN)
    # save_zb(zb_nodes.values(), SQL_INSERT_LOC_NODES_EN)
    # for zb in zb_nodes.values():
    #     if zb['isParent'] == False:
    #         time.sleep(1)
    #         zb_data = get_zb_fact_data(REGION_ZB_URL_EN, zb['id'], load_fact=False)
    #         save_zb_mx(zb_data['dim'], zb['id'], zb['name'], SQL_INSERT_LOC_NODES_EN)
    # save_areas()
