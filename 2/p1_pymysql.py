import pymysql


dbInfo = {
    'host' : 'localhost',
    'port' : 3306,
    'user' : 'root',
    'password' : 'tc2a_FLW',
    'db' : 'db1',
    'charset' : 'utf8'    
}

# sqls = ['select 1', 'select VERSION()']
sqls = ['select * from student_info']
results = []

class ConnDB(object):
    def __init__(self, dbInfo, sqls):
        self.host = dbInfo['host']
        self.port = dbInfo['port']
        self.user = dbInfo['user']
        self.password = dbInfo['password']
        self.db = dbInfo['db']
        self.charset = dbInfo['charset']
        self.sqls = sqls
    
    def run(self):
        conn = pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            db = self.db,
            charset = self.charset
        )
        '''
        cursor游标建立时候就开启了隐形事务
        事务：对数据库的一系列操作，保ACID，要么都执行后commit，要么都不执行rollback
        cursor(游标)：数据库中的操作操作通常会生成结果集，游标相当于指针，允许用户逐行查询和操作结果集中的数据
        1. 建立的时候开启隐形事务
        2. 执行sql语句时，隐形事务开始
        3. 执行sql语句后，隐形事务结束
        4. 如果执行sql语句后，隐形事务结束，则需要手动commit，否则自动rollback
        '''
        cur = conn.cursor()
        try:
            for sql in self.sqls:
                cur.execute(sql)    # execute执行sql语句，将结果集返回给游标，不会查询结果只是返回执行
                results.append(cur.fetchall()) # fetchall()查询结果集，返回结果集列表，当然可以使用fetchone进行单行查询
            cur.close()
            cur.commit()
        except:
            conn.rollback()

        conn.close()

if __name__ == '__main__':
    db = ConnDB(dbInfo, sqls)
    db.run()
    for result in results:
        print(result)

