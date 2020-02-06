from flask import Flask, request
import xml.etree.ElementTree as ET

class Pool(object):
    def __init__(self, name, weekday_closure, weekend, pool_type):
        self.name = name
        self.weekday_closure = weekday_closure
        self.weekend = weekend
        self.pool_type = pool_type

def parseXML(file):
    tree = ET.parse(file)
    root = tree.getroot()
    pools = []
    for row in root.findall('row'):

        name = row.find('pool_name')
        if name != None:
            name = name.text

        weekday_closure = row.find('weekday_closure')
        if weekday_closure != None:
            weekday_closure = weekday_closure.text

        weekend = row.find('weekend')
        if weekend != None:
            weekend = weekend.text

        pool_type = row.find('pool_type')
        if pool_type != None:
            pool_type = pool_type.text

        pool = Pool(name, weekday_closure, weekend, pool_type)
        pools.append(pool)
    return pools

app = Flask(__name__)
@app.route('/')
def index():
    weekday_closure = request.args.get('weekday_closure')
    weekend = request.args.get('weekend')
    pool_type = request.args.get('pool_type')
    pool_list = parseXML('austin-pool-timings.xml')
    result_name = []

    for pool in pool_list:
        if (pool.weekday_closure == weekday_closure or weekday_closure == None) and (pool.weekend == weekend or weekend == None) and (pool.pool_type == pool_type or pool_type == None) and ((pool_type != None) or (weekend != None) or (weekday_closure != None )):
            if 'Splashpad' in pool.name:
                result_name.append(pool.name.strip('Splashpad'))
            else:
                result_name.append(pool.name)
    return '<br/>'.join(map(str, result_name))

if __name__ == "__main__":
        app.run()